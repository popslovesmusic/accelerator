from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


def make_run_id(script_id: str, campaign_id: Optional[str] = None, now: Optional[datetime] = None) -> str:
    ts = (now or datetime.now()).strftime("%Y-%m-%d_%H%M%S")
    suffix = campaign_id or script_id
    suffix = str(suffix).strip().replace(" ", "_")
    return f"{ts}_{suffix}"


@dataclass(frozen=True)
class RunDirs:
    run_dir: Path
    configs_dir: Path
    outputs_dir: Path
    reports_dir: Path
    logs_dir: Path
    raw_dir: Path


def resolve_run_dir(run_id: str, root: Path | str = ".") -> Path:
    root_path = Path(root)
    return (root_path / "results" / run_id).resolve()


def create_run_dirs(run_id: str, root: Path | str = ".") -> RunDirs:
    run_dir = resolve_run_dir(run_id, root=root)
    configs_dir = run_dir / "configs"
    outputs_dir = run_dir / "outputs"
    reports_dir = run_dir / "reports"
    logs_dir = run_dir / "logs"
    raw_dir = run_dir / "raw"

    for p in (configs_dir, outputs_dir, reports_dir, logs_dir, raw_dir):
        p.mkdir(parents=True, exist_ok=True)

    return RunDirs(
        run_dir=run_dir,
        configs_dir=configs_dir,
        outputs_dir=outputs_dir,
        reports_dir=reports_dir,
        logs_dir=logs_dir,
        raw_dir=raw_dir,
    )


def write_resolved_config(run_dir: Path, name: str, data: dict[str, Any]) -> Path:
    configs_dir = run_dir / "configs"
    configs_dir.mkdir(parents=True, exist_ok=True)
    path = configs_dir / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return path


def resolve_output_path(run_dir: Path, category: str, name: str) -> Path:
    base = run_dir / category
    base.mkdir(parents=True, exist_ok=True)
    return base / name


def write_report(run_dir: Path, name: str, data: Any) -> Path:
    reports_dir = run_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / name
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(data, (dict, list)):
            json.dump(data, f, indent=2)
        else:
            f.write(str(data))
    return path


def write_run_metadata(run_dir: Path, script_id: str, argv: list[str], extra: Optional[dict[str, Any]] = None) -> Path:
    meta: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(),
        "script_id": script_id,
        "argv": argv,
    }
    if extra:
        meta.update(extra)
    return write_report(run_dir, "run_metadata.json", meta)

