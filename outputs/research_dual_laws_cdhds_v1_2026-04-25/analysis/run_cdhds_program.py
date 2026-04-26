import argparse
import json
import subprocess
from datetime import date
from pathlib import Path


def _load_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def _deepcopy(obj: dict) -> dict:
    return json.loads(json.dumps(obj))


def _with_seed(cfg: dict, seed: int) -> dict:
    cfg2 = _deepcopy(cfg)
    if "engine_config" in cfg2:
        cfg2["engine_config"]["seed"] = int(seed)
    return cfg2


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CDHDS dual-laws program across model classes and seeds")
    parser.add_argument("--program_dir", required=True, help="Program directory")
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
        ("rd", "baseline", configs_dir / "cdhds_rd_baseline.json", wrappers_dir / "cdhds_rd_runner.py"),
        ("rd", "negative_no_recouple", configs_dir / "cdhds_rd_negative_no_recouple.json", wrappers_dir / "cdhds_rd_runner.py"),
        ("fsa", "baseline", configs_dir / "cdhds_fsa_baseline.json", wrappers_dir / "cdhds_fsa_runner.py"),
        ("graph", "baseline", configs_dir / "cdhds_graph_baseline.json", wrappers_dir / "cdhds_graph_runner.py"),
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

