import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_git_head(repo_root: str) -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "-C", repo_root, "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or None
    except Exception:
        return None


def _extract_seed_and_precision(config: dict[str, Any]) -> tuple[int | None, str | None]:
    seed = None
    precision = None

    if isinstance(config.get("seed"), int):
        seed = int(config["seed"])

    ic = config.get("initial_condition")
    if seed is None and isinstance(ic, dict) and isinstance(ic.get("seed"), int):
        seed = int(ic["seed"])

    if isinstance(config.get("precision"), str):
        precision = config["precision"]

    return seed, precision


def _write_run_metadata(out_dir: str, config_path: str, exe_path: str) -> None:
    os.makedirs(out_dir, exist_ok=True)

    config_hash = _sha256_file(config_path)
    try:
        config_obj = json.loads(Path(config_path).read_text(encoding="utf-8"))
    except Exception:
        config_obj = {}

    seed, precision = _extract_seed_and_precision(config_obj if isinstance(config_obj, dict) else {})

    repo_root = str(Path(__file__).resolve().parents[2])
    meta = {
        "seed": seed,
        "config_hash": config_hash,
        "backend": {
            "launcher": "sim_governed.py",
            "setvars_bat": r"C:\Program Files (x86)\Intel\oneAPI\setvars.bat",
            "exe_path": exe_path,
            "oneapi_root": os.environ.get("ONEAPI_ROOT"),
            "dpcpp_root": os.environ.get("DPCPP_ROOT"),
        },
        "precision": precision,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": _safe_git_head(repo_root),
        "implementation_language": "cpp",
        "cpp_equivalent_available": True,
    }

    Path(out_dir, "run_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--exe",
        default=None,
        help="Optional path to box_sim.exe (defaults to local tool directory).",
    )
    args = parser.parse_args()
    
    os.makedirs(args.out, exist_ok=True)
    
    tool_dir = Path(__file__).resolve().parent
    default_exe = tool_dir / "box_sim.exe"
    legacy_exe = tool_dir / "tools" / "structural_box_sim_cpp" / "box_sim.exe"
    exe_path = os.path.abspath(str(Path(args.exe) if args.exe else (default_exe if default_exe.exists() else legacy_exe)))
    config_path = os.path.abspath(args.config)
    out_dir = os.path.abspath(args.out)

    setvars = r"C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
    if os.path.exists(setvars):
        # Use a single string with shell=True, and let cmd handle the quotes
        full_cmd = f'call "{setvars}" && "{exe_path}" --config "{config_path}" --out "{out_dir}"'
    else:
        full_cmd = f'"{exe_path}" --config "{config_path}" --out "{out_dir}"'

    _write_run_metadata(out_dir=out_dir, config_path=config_path, exe_path=exe_path)

    print(f"Executing: {full_cmd}")
    subprocess.run(full_cmd, check=True, shell=True)

if __name__ == "__main__":
    run()
