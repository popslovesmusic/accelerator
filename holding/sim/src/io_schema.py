from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


def ensure_run_directory(root: Path, run_id: str) -> Path:
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_timeseries_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = ["step", "t", "epsilon", "rho", "residue"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary_csv(path: Path, summary: dict) -> None:
    fieldnames = list(summary.keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(summary)


def write_run_summary_markdown(path: Path, manifest: dict, summary: dict) -> None:
    lines = [
        f"# Run Summary: {manifest['run_id']}",
        "",
        "## Identity",
        "",
        f"- `run_id`: `{manifest['run_id']}`",
        f"- `equation_mode`: `{manifest['equation_mode']}`",
        f"- `experiment_family`: `{manifest['experiment_family']}`",
        f"- `timestamp_utc`: `{manifest['timestamp_utc']}`",
        f"- `code_version`: `{manifest['code_version']}`",
        f"- `config_path`: `{manifest['config_path']}`",
        f"- `config_sha256`: `{manifest['config_sha256']}`",
        f"- `seed`: `{manifest['seed']}`",
        "",
        "## Outcome",
        "",
        f"- `regime_classification`: `{summary['regime_classification']}`",
        f"- `epsilon_final`: `{summary['epsilon_final']}`",
        f"- `rho_final`: `{summary['rho_final']}`",
        f"- `residue_final`: `{summary['residue_final']}`",
        f"- `epsilon_max`: `{summary['epsilon_max']}`",
        f"- `rho_max`: `{summary['rho_max']}`",
    ]

    if "residue_max" in summary:
        lines.append(f"- `residue_max`: `{summary['residue_max']}`")
    if "epsilon_mean" in summary:
        lines.append(f"- `epsilon_mean`: `{summary['epsilon_mean']}`")
    if "rho_mean" in summary:
        lines.append(f"- `rho_mean`: `{summary['rho_mean']}`")
    if "residue_mean" in summary:
        lines.append(f"- `residue_mean`: `{summary['residue_mean']}`")
    if "collapse_time" in summary:
        collapse_value = summary["collapse_time"] if summary["collapse_time"] else "not_triggered"
        lines.append(f"- `collapse_time`: `{collapse_value}`")
    if "integrator" in summary:
        lines.append(f"- `integrator`: `{summary['integrator']}`")
    if "dt" in summary:
        lines.append(f"- `dt`: `{summary['dt']}`")
    if "t_final" in summary:
        lines.append(f"- `t_final`: `{summary['t_final']}`")
    if "sample_every" in summary:
        lines.append(f"- `sample_every`: `{summary['sample_every']}`")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            f"- {manifest['notes']}",
            "",
            "## Files",
            "",
            "- `run_manifest.json`",
            "- `config_snapshot.json`",
            "- `timeseries_global.csv`",
            "- `final_summary.csv`",
            "- `run_summary.md`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
