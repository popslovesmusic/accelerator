from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


TOOL_DIR = Path(__file__).resolve().parent


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def resolve_repo_root() -> Path:
    for p in [TOOL_DIR, *TOOL_DIR.parents]:
        if (p / "registry" / "tool_manifest.json").exists():
            return p
    return TOOL_DIR.parents[2]


def flatten_trace_metrics(trace_path: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    if trace_path.exists():
        with trace_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))

    if not rows:
        return {
            "continuation_mismatch_mean": 0.0,
            "phase_error_mean": 0.0,
            "rejection_rate": 0.0,
            "hold_rate": 0.0,
            "reinforce_rate": 0.0,
            "survival_metrics": 0.0,
            "trajectory_alignment": 0.0,
            "phase_locking_value": 0.0,
            "frames_logged": 0,
        }

    def mean_float(key: str) -> float:
        vals = [float(r.get(key, 0.0) or 0.0) for r in rows]
        return float(sum(vals) / max(1, len(vals)))

    decisions = [str(r.get("survivability_decision", "")) for r in rows]
    total = float(max(1, len(decisions)))
    reject_rate = decisions.count("reject") / total
    hold_rate = decisions.count("hold") / total
    reinforce_rate = decisions.count("reinforce") / total

    # Alignment proxy: bounded inverse error. This is a reporting metric, not a rigor endorsement proof.
    phase_error = mean_float("phase_error")
    trajectory_alignment = float(max(0.0, min(1.0, 1.0 - phase_error)))

    return {
        "continuation_mismatch_mean": mean_float("continuation_mismatch"),
        "phase_error_mean": phase_error,
        "signal_x_mean": mean_float("signal_x"),
        "frequency_drift_mean": mean_float("frequency_drift"),
        "rejection_rate": float(reject_rate),
        "hold_rate": float(hold_rate),
        "reinforce_rate": float(reinforce_rate),
        "survival_metrics": float(reinforce_rate),
        "trajectory_alignment": trajectory_alignment,
        "phase_locking_value": trajectory_alignment,
        "frames_logged": len(rows),
    }


def write_metrics_csv(path: Path, metrics: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(metrics.keys()))
        writer.writeheader()
        writer.writerow(metrics)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Run the Signal Scope phase-continuation candidate.")
    parser.add_argument("--config", required=True, help="Candidate config JSON.")
    parser.add_argument("--out", "--out_dir", dest="out_dir", required=True, help="Output directory.")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed override.")
    args = parser.parse_args()

    repo_root = resolve_repo_root()
    config_path = Path(args.config).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = load_json(config_path)
    seed = int(args.seed if args.seed is not None else (cfg.get("fixed_seeds") or [101])[0])
    run_id = f"{cfg.get('id', 'signal_scope_run')}_seed{seed}_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    sys.path.insert(0, str(TOOL_DIR))
    previous_cwd = Path.cwd()
    try:
        os.chdir(TOOL_DIR)
        import numpy as np
        from native_platform.run_native_platform import run_platform

        np.random.seed(seed)
        engine_cfg = cfg.get("engine", {})
        ablation_cfg = cfg.get("ablations", {})
        thresholds = cfg.get("thresholds", {})
        
        summary = run_platform(
            num_frames=int(engine_cfg.get("num_frames", 100)),
            num_nodes=int(engine_cfg.get("num_nodes", 100)),
            engine_steps_per_frame=int(engine_cfg.get("engine_steps_per_frame", 5)),
            run_id=run_id,
            memory_path=str(Path("sessions") / f"{run_id}_memory.json"),
            connected=True,
            connected_state=str(engine_cfg.get("connected_state", "train")),
            ablation_cfg=ablation_cfg,
            thresholds=thresholds,
        )
    finally:
        os.chdir(previous_cwd)

    trace_path = TOOL_DIR / summary["feedback_trace_path"]
    metrics = flatten_trace_metrics(trace_path)

    copied_trace_path = out_dir / Path(summary["feedback_trace_path"]).name
    if trace_path.exists():
        shutil.copy2(trace_path, copied_trace_path)

    final_summary = {
        "tool_name": "signal_scope_phase_continuation_engine",
        "model_class": "agent_based_phase_continuation_sim",
        "mechanism_class": "agent_phase_continuation",
        "run_id": run_id,
        "seed": seed,
        "config_path": str(config_path),
        "config_hash": hash_file(config_path),
        "backend": "python_numpy",
        "precision": "float64",
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_commit": git_commit(repo_root),
        "input_generator": "native_default_synthetic_sine",
        "not_medical_tool": True,
        "native_summary": summary,
        "metrics": metrics,
        "recoverable_outputs": {
            "summary": str(out_dir / "summary.json"),
            "metrics": str(out_dir / "metrics.csv"),
            "feedback_trace": str(copied_trace_path),
            "provenance": str(out_dir / "provenance_report.json"),
        },
    }

    write_json(out_dir / "summary.json", final_summary)
    write_metrics_csv(out_dir / "metrics.csv", metrics)
    write_json(out_dir / "provenance_report.json", {
        "seed": seed,
        "config_hash": final_summary["config_hash"],
        "backend": final_summary["backend"],
        "precision": final_summary["precision"],
        "timestamp": final_summary["timestamp"],
        "source_commit": final_summary["source_commit"],
        "input_generator": final_summary["input_generator"],
        "run_id": run_id,
        "report_path": str(out_dir / "summary.json"),
    })

    print(json.dumps(final_summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
