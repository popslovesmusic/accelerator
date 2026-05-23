import argparse
import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_NAME = "structural_box_sim_cpp"
TOOL_ENTRYPOINT = REPO_ROOT / "tools" / TOOL_NAME / "sim_governed.py"
VALIDATION_DIR = REPO_ROOT / "tools" / TOOL_NAME / "validation"


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def _sha256_json(obj: Any) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(data)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _safe_git_head() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or None
    except Exception:
        return None


@dataclass(frozen=True)
class RunResult:
    level_id: str
    out_dir: Path
    summary_path: Path
    summary: dict[str, Any]
    stdout_log: Path
    stderr_log: Path
    config_path: Path
    config_hash: str


def _run_one(config_obj: dict[str, Any], out_dir: Path, level_id: str) -> RunResult:
    out_dir.mkdir(parents=True, exist_ok=True)

    config_path = out_dir / "config_flat.json"
    config_path.write_text(json.dumps(config_obj, indent=2), encoding="utf-8")
    config_hash = _sha256_json(config_obj)

    stdout_log = out_dir / "stdout.log"
    stderr_log = out_dir / "stderr.log"
    summary_path = out_dir / "summary.json"

    cmd = [
        "python",
        str(TOOL_ENTRYPOINT),
        "--config",
        str(config_path),
        "--out",
        str(out_dir),
    ]

    with stdout_log.open("w", encoding="utf-8") as out_f, stderr_log.open("w", encoding="utf-8") as err_f:
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), stdout=out_f, stderr=err_f)

    if proc.returncode != 0:
        raise RuntimeError(f"{TOOL_NAME} failed for {level_id} (exit={proc.returncode}). See {stderr_log}")

    if not summary_path.exists():
        raise RuntimeError(f"Missing summary.json for {level_id} in {out_dir}")

    summary = _load_json(summary_path)
    if not isinstance(summary, dict) or summary.get("status") != "completed":
        raise RuntimeError(f"Unexpected summary.json content for {level_id} in {out_dir}")

    # Attach config hash + commit for convenience (provenance remains recoverable via files)
    validation_meta = {
        "timestamp": _utc_now(),
        "source_commit": _safe_git_head(),
        "config_hash": config_hash,
        "level_id": level_id,
    }
    _write_json(out_dir / "validation_meta.json", validation_meta)

    return RunResult(
        level_id=level_id,
        out_dir=out_dir,
        summary_path=summary_path,
        summary=summary,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        config_path=config_path,
        config_hash=config_hash,
    )


def _extract_metrics(summary: dict[str, Any]) -> dict[str, float]:
    report = summary.get("report", {})
    fp64 = report.get("fp64_results", {})
    fp32 = report.get("fp32_results", {})
    fals = report.get("falsification_zero_s", {})
    drift = report.get("precision_drift", {})

    def fget(d: Any, key: str) -> float | None:
        v = d.get(key) if isinstance(d, dict) else None
        return float(v) if isinstance(v, (int, float)) else None

    metrics: dict[str, float] = {}

    for prefix, block in [("fp64", fp64), ("fp32", fp32), ("falsification_zero_s", fals)]:
        for k in ["epsilon_max", "epsilon_active_fraction", "rho_min", "residue_max", "time_ms"]:
            v = fget(block, k)
            if v is not None:
                metrics[f"{prefix}.{k}"] = v

    for k in ["epsilon_max_abs", "epsilon_max_rel"]:
        v = fget(drift, k)
        if v is not None:
            metrics[f"precision_drift.{k}"] = v

    # Top-level mapped metrics
    for k in ["alignment_success_rate", "exclusion_rate_k"]:
        v = fget(report, k)
        if v is not None:
            metrics[k] = v

    return metrics


def _relative_change(a: float, b: float) -> float:
    denom = max(abs(a), 1e-12)
    return abs(a - b) / denom


def run_convergence(base_config: dict[str, Any], levels: list[dict[str, Any]], out_root: Path) -> dict[str, Any]:
    results: list[RunResult] = []
    for lvl in levels:
        level_id = str(lvl["level_id"])
        cfg = dict(base_config)
        for k in ["nx", "dt", "steps"]:
            if k in lvl:
                cfg[k] = lvl[k]
        res = _run_one(cfg, out_root / "convergence" / level_id, level_id=level_id)
        results.append(res)

    # Compare successive levels for key fp64 metrics
    comparisons: list[dict[str, Any]] = []
    key_metrics = ["fp64.epsilon_max", "fp64.epsilon_active_fraction", "fp64.rho_min", "fp64.residue_max"]

    metrics_by_level = {r.level_id: _extract_metrics(r.summary) for r in results}
    ordered = [r.level_id for r in results]
    for a, b in zip(ordered, ordered[1:]):
        ma = metrics_by_level[a]
        mb = metrics_by_level[b]
        entry = {"from": a, "to": b, "relative_changes": {}, "artifacts": {"from": str(results[ordered.index(a)].out_dir), "to": str(results[ordered.index(b)].out_dir)}}
        for k in key_metrics:
            if k in ma and k in mb:
                entry["relative_changes"][k] = _relative_change(ma[k], mb[k])
        comparisons.append(entry)

    report = {
        "performed": True,
        "timestamp": _utc_now(),
        "source_commit": _safe_git_head(),
        "levels": [{"level_id": r.level_id, "out_dir": str(r.out_dir), "config_hash": r.config_hash} for r in results],
        "comparisons": comparisons,
        "key_metrics": key_metrics,
    }
    return report


def run_precision_and_controls(base_config: dict[str, Any], out_root: Path) -> dict[str, Any]:
    res = _run_one(dict(base_config), out_root / "baseline", level_id="baseline")
    metrics = _extract_metrics(res.summary)

    # Falsification expectation: activity fraction for zero_s should not exceed baseline fp64 activity by much.
    baseline_activity = metrics.get("fp64.epsilon_active_fraction")
    fals_activity = metrics.get("falsification_zero_s.epsilon_active_fraction")
    fals_pass = None
    if baseline_activity is not None and fals_activity is not None:
        # Tool README claims s=0 should lead to collapse or lower activity. Treat "no meaningful change"
        # as a falsification failure (capability exists, expected negative-control effect not observed).
        min_drop_fraction = 0.05
        target = baseline_activity * (1.0 - min_drop_fraction)
        fals_pass = bool(fals_activity < target)
    fals_notes = None
    if baseline_activity is not None and fals_activity is not None:
        fals_notes = {
            "criterion": "fals_activity < baseline_activity*(1-0.05)",
            "baseline_activity": baseline_activity,
            "fals_activity": fals_activity,
            "target": baseline_activity * 0.95,
            "observed_drop_fraction": (baseline_activity - fals_activity) / max(baseline_activity, 1e-12),
        }

    report = {
        "performed": True,
        "timestamp": _utc_now(),
        "source_commit": _safe_git_head(),
        "baseline_out_dir": str(res.out_dir),
        "precision_drift": {
            "epsilon_max_abs": metrics.get("precision_drift.epsilon_max_abs"),
            "epsilon_max_rel": metrics.get("precision_drift.epsilon_max_rel"),
        },
        "falsification_zero_s": {
            "baseline_fp64_epsilon_active_fraction": baseline_activity,
            "falsification_epsilon_active_fraction": fals_activity,
            "passed": fals_pass,
            "notes": fals_notes,
        },
        "artifacts": {
            "summary": str(res.summary_path),
            "stdout": str(res.stdout_log),
            "stderr": str(res.stderr_log),
            "config": str(res.config_path),
        },
    }
    return report


def run_parameter_sensitivity(base_config: dict[str, Any], out_root: Path) -> dict[str, Any]:
    # This tool is deterministic (no RNG); we quantify uncertainty as parameter sensitivity around baseline.
    sweeps = [
        {"sweep_id": "kappa_pm5pct", "param": "kappa", "values": [base_config["kappa"] * 0.95, base_config["kappa"], base_config["kappa"] * 1.05]},
        {"sweep_id": "lambda_R_pm5pct", "param": "lambda_R", "values": [base_config["lambda_R"] * 0.95, base_config["lambda_R"], base_config["lambda_R"] * 1.05]},
        {"sweep_id": "s_pm10pct", "param": "s", "values": [base_config["s"] * 0.90, base_config["s"], base_config["s"] * 1.10]},
    ]

    runs: list[dict[str, Any]] = []
    for sweep in sweeps:
        param = sweep["param"]
        for v in sweep["values"]:
            cfg = dict(base_config)
            cfg[param] = float(v)
            level_id = f"{sweep['sweep_id']}__{param}={v:.6g}"
            res = _run_one(cfg, out_root / sweep["sweep_id"] / f"{param}_{v:.6g}", level_id=level_id)
            metrics = _extract_metrics(res.summary)
            runs.append(
                {
                    "sweep_id": sweep["sweep_id"],
                    "param": param,
                    "value": float(v),
                    "out_dir": str(res.out_dir),
                    "config_hash": res.config_hash,
                    "metrics": {k: metrics.get(k) for k in ["fp64.epsilon_max", "fp64.epsilon_active_fraction", "alignment_success_rate", "exclusion_rate_k"]},
                }
            )

    report = {
        "performed": True,
        "timestamp": _utc_now(),
        "source_commit": _safe_git_head(),
        "method": "parameter_sensitivity (deterministic tool; no seed/RNG path in engine)",
        "runs": runs,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate full-rigor validation artifacts for structural_box_sim_cpp.")
    parser.add_argument("--base-config", default="configs/validation/structural_box_sim_cpp/base_flat.json")
    parser.add_argument("--convergence-levels", default="configs/validation/structural_box_sim_cpp/convergence_levels.json")
    parser.add_argument("--out-root", default="outputs/validation/structural_box_sim_cpp_full_rigor")
    parser.add_argument("--skip-convergence", action="store_true")
    args = parser.parse_args()

    base = _load_json(REPO_ROOT / args.base_config)
    if not isinstance(base, dict):
        raise SystemExit("base config must be a JSON object")

    out_root = (REPO_ROOT / args.out_root).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    precision_report = run_precision_and_controls(base, out_root=out_root / "precision_and_controls")
    _write_json(VALIDATION_DIR / "precision_drift_report.json", precision_report)

    fals_report = {
        "tool_name": TOOL_NAME,
        "falsification_test": {
            "performed": True,
            "passed": precision_report["falsification_zero_s"]["passed"],
            "timestamp": precision_report["timestamp"],
            "run_id": "full_rigor_zero_mismatch_s_eq_0",
        },
        "artifacts": precision_report["artifacts"],
    }
    _write_json(VALIDATION_DIR / "falsification_report.json", fals_report)

    uncertainty_report = run_parameter_sensitivity(base, out_root=out_root / "parameter_sensitivity")
    _write_json(VALIDATION_DIR / "uncertainty_report.json", uncertainty_report)

    if not args.skip_convergence:
        levels_obj = _load_json(REPO_ROOT / args.convergence_levels)
        levels = levels_obj.get("levels", []) if isinstance(levels_obj, dict) else []
        convergence_report = run_convergence(base, levels=levels, out_root=out_root)
        _write_json(VALIDATION_DIR / "convergence_report.json", convergence_report)

    # Minimal known limits doc: tie to deterministic engine + flat config schema
    known_limits_path = VALIDATION_DIR / "known_limits.md"
    if known_limits_path.exists():
        existing = known_limits_path.read_text(encoding="utf-8", errors="ignore").strip()
    else:
        existing = ""

    if "Determinism" not in existing or "Config schema" not in existing:
        known_limits_path.write_text(
            "\n".join(
                [
                    "# Known Limits",
                    "",
                    "- Determinism: the engine initialization is fixed (no RNG/noise path); seed-based uncertainty is not applicable unless the engine is extended.",
                    "- Config schema: the C++ engine reads a *flat* JSON schema (e.g., `nx`, `steps`, `dt`, `kappa`, `lambda_R`, `s`). Nested `grid/model` configs are ignored by the engine.",
                    "- Hardware: GPU path uses default SYCL selector; device choice may vary by host configuration.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    print("Validation artifacts written to:", str(VALIDATION_DIR))
    print("Outputs written to:", str(out_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
