"""Run only validation stages affected by a Git diff.

This is a bounded validation planner. It does not replace scheduled full
validation and does not alter canonical files.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "outputs/audits/diff_validation_report.json"

BASE_STAGE_SET = {"unified_manifest_validation", "hygiene_validation"}
GENERATED_PREFIXES = (
    "outputs/",
    "audit_outputs/",
    "validation/results/",
    "departments/analysis/crawl_reports/",
)
STAGE_MAP = {
    "registry/": {"registry_validation"},
    "governance/live/": {"governance_integrity_validation", "patch_chain_validation", "db_runtime_validation"},
    "governance/": {"governance_integrity_validation", "patch_chain_validation"},
    "registry/governance/": {"governance_integrity_validation", "patch_chain_validation"},
    "registry/db/": {"db_validation", "db_runtime_validation"},
    "scripts/db/": {"db_validation", "db_runtime_validation"},
    "docs/textbook/": {"textbook_projection_freshness_validation"},
    "docs/theory/": {"math_validation", "math_test_provenance_validation", "math_program_validation"},
    "registry/math/": {"math_validation", "math_test_provenance_validation", "math_program_validation"},
    "results/": {"evidence_validation", "campaign_validation"},
    "validation/": {"evidence_validation", "campaign_validation"},
    "tools/": {"implementation_validation", "hygiene_validation"},
    "scripts/": {"implementation_validation", "hygiene_validation"},
}

DB_AFFECTING_PREFIXES = (
    "registry/db/",
    "scripts/db/",
    "governance/live/",
    "governance/runtime/",
)
FULL_VALIDATION_PREFIXES = (
    "registry/",
    "governance/",
    "docs/textbook/",
    "docs/theory/",
)


def git_paths(base: str) -> list[str]:
    commands = [
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        ["git", "diff", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]
    paths: set[str] = set()
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
        paths.update(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())
    return sorted(paths)


def split_generated(paths: list[str]) -> tuple[list[str], list[str]]:
    source_paths = []
    generated_paths = []
    for path in paths:
        if path.startswith(GENERATED_PREFIXES):
            generated_paths.append(path)
        else:
            source_paths.append(path)
    return source_paths, generated_paths


def affected_stages(paths: list[str]) -> set[str]:
    stages = set(BASE_STAGE_SET)
    for path in paths:
        for prefix, mapped in STAGE_MAP.items():
            if path.startswith(prefix):
                stages.update(mapped)
        if path.endswith((".json", ".md", ".txt")):
            stages.add("unified_manifest_validation")
    return stages


def full_validation_required(paths: list[str]) -> bool:
    return any(path.startswith(FULL_VALIDATION_PREFIXES) for path in paths)


def db_validation_required(paths: list[str]) -> bool:
    return any(path.startswith(DB_AFFECTING_PREFIXES) for path in paths)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="HEAD", help="Git commit or ref used as the diff baseline")
    parser.add_argument("--stage-timeout-seconds", type=int, default=30)
    parser.add_argument("--out", default=str(REPORT))
    parser.add_argument(
        "--include-generated",
        action="store_true",
        help="Include generated reports and crawl outputs in impact planning",
    )
    args = parser.parse_args()
    all_paths = git_paths(args.base)
    paths, generated_paths = split_generated(all_paths)
    if args.include_generated:
        paths = all_paths
        generated_paths = []
    stages = sorted(affected_stages(paths))
    started = datetime.now(timezone.utc).isoformat()
    if not paths:
        payload = {
            "status": "PASS_NO_CHANGES",
            "started_at": started,
            "base": args.base,
            "changed_paths": [],
            "ignored_generated_paths": generated_paths,
            "selected_stages": [],
            "skipped_stages": "intentional_no_diff",
            "full_validation_required": False,
            "db_validation_required": False,
        }
        Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    command = [sys.executable, "scripts/global_validate.py", "--stages", *stages, "--stage-timeout-seconds", str(args.stage_timeout_seconds), "--out", args.out]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    try:
        report = json.loads(Path(args.out).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        report = {"status": "FAIL_REPORT_NOT_CREATED", "validator_stdout": result.stdout, "validator_stderr": result.stderr}
    stage_results = {item["stage_name"]: item["status"] for item in report.get("stage_results", [])}
    skipped = [name for name, status in stage_results.items() if status.startswith("SKIPPED")]
    failed = [name for name, status in stage_results.items() if status.startswith("FAIL")]
    payload = {
        "status": "FAIL_DIFF_VALIDATION" if failed else "PASS_DIFF_VALIDATION",
        "started_at": started,
        "base": args.base,
        "changed_paths": paths,
        "ignored_generated_paths": generated_paths,
        "selected_stages": stages,
        "selected_stage_results": {name: stage_results.get(name, "MISSING") for name in stages},
        "stage_results": stage_results,
        "intentionally_skipped_stages": skipped,
        "failed_selected_stages": failed,
        "full_validation_required": full_validation_required(paths),
        "db_validation_required": db_validation_required(paths),
        "underlying_exit_code": result.returncode,
        "underlying_report_path": str(Path(args.out).resolve()),
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
