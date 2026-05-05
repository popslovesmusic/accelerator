from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def _load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Config-file wrapper for tools/linac_sim (python -m linac_sim).")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    cfg = _load_config(args.config)
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    # Run as a module so relative imports inside tools/linac_sim work.
    env = os.environ.copy()
    tools_path = str((Path(__file__).resolve().parents[1]).resolve())
    env["PYTHONPATH"] = tools_path + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    cmd = [
        sys.executable,
        "-m",
        "linac_sim",
        "run",
        "--output",
        str(out_dir),
    ]

    arg_map = {
        "species": "--species",
        "particles": "--particles",
        "seed": "--seed",
        "initial_energy_ev": "--initial-energy-ev",
        "energy_spread_fraction": "--energy-spread-fraction",
        "bunch_length_m": "--bunch-length-m",
        "transverse_size_m": "--transverse-size-m",
        "transverse_divergence_rad": "--transverse-divergence-rad",
        "z_transverse_size_m": "--z-transverse-size-m",
        "z_transverse_divergence_rad": "--z-transverse-divergence-rad",
        "aperture_radius_m": "--aperture-radius-m",
        "gaps": "--gaps",
        "drift_length_m": "--drift-length-m",
        "gap_length_m": "--gap-length-m",
        "peak_field": "--peak-field",
        "frequency": "--frequency",
        "phase": "--phase",
        "focusing_strength": "--focusing-strength",
        "z_focusing_strength": "--z-focusing-strength",
        "lens_length_m": "--lens-length-m",
        "dt": "--dt",
        "max_time": "--max-time",
        "history_interval": "--history-interval",
    }

    for key, flag in arg_map.items():
        if key in cfg and cfg[key] is not None:
            cmd.extend([flag, str(cfg[key])])

    return subprocess.call(cmd, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
