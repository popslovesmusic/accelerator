import argparse
import json
import os
import shutil
import subprocess
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def _with_seed(cfg: dict, seed: int) -> dict:
    cfg2 = json.loads(json.dumps(cfg))  # deep copy
    if "engine_config" in cfg2:
        cfg2["engine_config"]["seed"] = int(seed)
    return cfg2


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RT-1 recoupling hypothesis program (wrappers + seeds)")
    parser.add_argument("--program_dir", required=True, help="Program directory (e.g., outputs/research_recoupling_rt1_2026-04-25)")
    parser.add_argument("--seeds", default="101,102,103", help="Comma-separated seeds")
    args = parser.parse_args()

    program_dir = Path(args.program_dir).resolve()
    configs_dir = program_dir / "configs"
    wrappers_dir = program_dir / "wrappers"
    runs_dir = program_dir / "runs"
    analysis_dir = program_dir / "analysis"
    runs_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]

    experiments = [
        ("ca", "baseline", configs_dir / "rt1_ca_baseline.json", wrappers_dir / "rt1_ca_runner.py"),
        ("graph", "baseline", configs_dir / "rt1_graph_baseline.json", wrappers_dir / "rt1_graph_runner.py"),
        ("rd", "baseline", configs_dir / "rt1_rd_baseline.json", wrappers_dir / "rt1_rd_runner.py"),
        ("rd", "falsify_leak", configs_dir / "rt1_rd_falsify_leak.json", wrappers_dir / "rt1_rd_runner.py"),
    ]

    index_rows: list[dict] = []

    for model, variant, cfg_path, runner_path in experiments:
        base_cfg = _load_json(cfg_path)
        for seed in seeds:
            run_name = f"{model}_{variant}__seed{seed}"
            run_dir = runs_dir / run_name
            run_dir.mkdir(parents=True, exist_ok=True)

            run_cfg = _with_seed(base_cfg, seed)
            generated_cfg_path = run_dir / "config.json"
            _write_json(generated_cfg_path, run_cfg)

            cmd = ["python", str(runner_path), "--config", str(generated_cfg_path), "--out", str(run_dir)]
            _run(cmd)

            summary_path = run_dir / "summary.json"
            index_rows.append(
                {
                    "run_name": run_name,
                    "model": model,
                    "variant": variant,
                    "seed": seed,
                    "config_path": str(generated_cfg_path),
                    "summary_path": str(summary_path),
                    "out_dir": str(run_dir),
                }
            )

    index_path = analysis_dir / "index.json"
    _write_json(index_path, {"generated_at": str(date.today()), "runs": index_rows})

    print(f"Wrote run index: {index_path}")


if __name__ == "__main__":
    main()

