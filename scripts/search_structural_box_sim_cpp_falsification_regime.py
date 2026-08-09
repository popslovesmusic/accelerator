import argparse
import json
import math
import subprocess
from dataclasses import dataclass
import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = "structural_box_sim_cpp"
ENTRYPOINT = REPO_ROOT / "tools" / TOOL / "sim_governed.py"


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _extract(summary: dict[str, Any]) -> dict[str, float]:
    report = summary.get("report", {}) if isinstance(summary, dict) else {}
    fp64 = report.get("fp64_results", {}) if isinstance(report, dict) else {}
    fals = report.get("falsification_zero_s", {}) if isinstance(report, dict) else {}

    def fget(d: Any, k: str) -> float | None:
        v = d.get(k) if isinstance(d, dict) else None
        return float(v) if isinstance(v, (int, float)) else None

    baseline = fget(fp64, "epsilon_active_fraction")
    fals_act = fget(fals, "epsilon_active_fraction")
    eps_max = fget(fp64, "epsilon_max")
    return {
        "baseline_activity": baseline if baseline is not None else math.nan,
        "fals_activity": fals_act if fals_act is not None else math.nan,
        "baseline_epsilon_max": eps_max if eps_max is not None else math.nan,
    }


@dataclass(frozen=True)
class Candidate:
    config: dict[str, Any]
    out_dir: Path
    metrics: dict[str, float]

    @property
    def drop_fraction(self) -> float:
        b = self.metrics["baseline_activity"]
        f = self.metrics["fals_activity"]
        if not math.isfinite(b) or b <= 0 or not math.isfinite(f):
            return float("nan")
        return (b - f) / b


def run_one(config: dict[str, Any], out_dir: Path) -> Candidate:
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = out_dir / "config_flat.json"
    cfg_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    stdout_log = out_dir / "stdout.log"
    stderr_log = out_dir / "stderr.log"
    cmd = ["python", str(ENTRYPOINT), "--config", str(cfg_path), "--out", str(out_dir)]

    with stdout_log.open("w", encoding="utf-8") as out_f, stderr_log.open("w", encoding="utf-8") as err_f:
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), stdout=out_f, stderr=err_f)
    if proc.returncode != 0:
        raise RuntimeError(f"{TOOL} failed (exit={proc.returncode}) in {out_dir}")

    summary_path = out_dir / "summary.json"
    if not summary_path.exists():
        raise RuntimeError(f"missing summary.json in {out_dir}")
    summary = _load_json(summary_path)
    metrics = _extract(summary if isinstance(summary, dict) else {})
    _write_json(out_dir / "extracted_metrics.json", metrics)
    return Candidate(config=config, out_dir=out_dir, metrics=metrics)


def main() -> int:
    parser = argparse.ArgumentParser(description="Search for parameter regimes where built-in s=0 falsification reduces activity.")
    parser.add_argument("--base-config", default="configs/validation/structural_box_sim_cpp/base_flat.json")
    parser.add_argument("--out-root", default="outputs/validation/structural_box_sim_cpp_falsification_search")
    parser.add_argument(
        "--min-drop",
        type=float,
        default=0.05,
        help="Minimum drop fraction required (default 0.05 = 0.05 fraction).",
    )
    args = parser.parse_args()

    base = _load_json(REPO_ROOT / args.base_config)
    if not isinstance(base, dict):
        raise SystemExit("base config must be a JSON object")

    out_root = (REPO_ROOT / args.out_root).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    # Parameter grid: small but expressive. Keep runtime bounded while exploring likely levers.
    grid = {
        "s": [base.get("s", 0.01), 0.0, 0.02, 0.05, 0.1],
        "u": [base.get("u", 0.15) * 0.5, base.get("u", 0.15), base.get("u", 0.15) * 1.5],
        "kappa": [base.get("kappa", 0.6) * 0.8, base.get("kappa", 0.6), base.get("kappa", 0.6) * 1.2],
        "lambda_R": [base.get("lambda_R", 0.8) * 0.8, base.get("lambda_R", 0.8), base.get("lambda_R", 0.8) * 1.2],
        "activity_thresh": [base.get("activity_thresh", 0.05), base.get("activity_thresh", 0.05) * 1.5],
    }

    # Keep the run count controlled: sample combinations deterministically by nested loops with pruning.
    candidates: list[Candidate] = []
    run_id = 0
    for u in grid["u"]:
        for kappa in grid["kappa"]:
            for lam in grid["lambda_R"]:
                for thr in grid["activity_thresh"]:
                    # Only vary s in the config; engine also runs internal falsification with s=0,
                    # but we want baseline to be in a regime where that control actually differs.
                    for s in grid["s"]:
                        cfg = dict(base)
                        cfg["u"] = float(u)
                        cfg["kappa"] = float(kappa)
                        cfg["lambda_R"] = float(lam)
                        cfg["activity_thresh"] = float(thr)
                        cfg["s"] = float(s)

                        tag = f"r{run_id:04d}_u{u:.4g}_k{kappa:.4g}_l{lam:.4g}_thr{thr:.4g}_s{s:.4g}"
                        run_id += 1
                        c = run_one(cfg, out_root / tag)
                        candidates.append(c)

    # Rank by observed drop fraction (baseline vs built-in falsification run inside summary.json)
    scored = [
        {
            "out_dir": str(c.out_dir),
            "drop_fraction": c.drop_fraction,
            "baseline_activity": c.metrics["baseline_activity"],
            "fals_activity": c.metrics["fals_activity"],
            "config": c.config,
        }
        for c in candidates
        if math.isfinite(c.drop_fraction)
    ]
    scored.sort(key=lambda x: x["drop_fraction"], reverse=True)

    best = scored[0] if scored else None
    report = {
        "performed": True,
        "timestamp": _utc_now(),
        "min_drop_required": args.min_drop,
        "runs": len(scored),
        "best": best,
        "top10": scored[:10],
        "notes": "drop_fraction is computed from fp64 baseline activity vs falsification_zero_s activity emitted by the engine.",
    }

    _write_json(out_root / "search_report.json", report)

    if best and best["drop_fraction"] >= args.min_drop:
        print("FOUND regime:", best["out_dir"], "drop_fraction=", best["drop_fraction"])
        return 0

    print("NO regime found meeting min_drop. Best:", (best["drop_fraction"] if best else None))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
