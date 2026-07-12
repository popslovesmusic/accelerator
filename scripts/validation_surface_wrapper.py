import argparse
import subprocess
import sys
from pathlib import Path


def run_validation_surface(description, stage_names, default_out, mode_flag=None, argv=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--out", default=default_out, help="Report output path")
    parser.add_argument("--profile", action="store_true", help="Emit a detailed stage timing profile in the report.")
    parser.add_argument("--stage-timeout-seconds", type=float, help="Mark any stage exceeding this budget as timed out in the report.")
    parser.add_argument("--history", action="store_true", help="Append a compact run summary to outputs/audits/validation_history.jsonl.")
    parser.add_argument("--trend", action="store_true", help="Generate outputs/audits/validation_trend_report.json from prior validation history.")
    parser.add_argument("--trend-baseline", help="Select a baseline run_id for trend comparison; defaults to the most recent passing full run.")
    parser.add_argument("--no-history", action="store_true", help="Disable history writing even when trend mode is enabled.")
    parser.add_argument("--no-db-log", action="store_true", help="Suppress DB-backed logging in auxiliary governance diagnostics.")
    parser.add_argument("--full-math-program", action="store_true", help="Embed full math-program validator payloads in the output report.")
    parser.add_argument("--list-stages", action="store_true", help="Print the stage names this wrapper runs and exit.")
    args = parser.parse_args(argv)

    if args.list_stages:
        for stage_name in stage_names:
            print(stage_name)
        return 0

    root = Path(args.root).resolve()
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = root / out_path

    cmd = [
        sys.executable,
        "-m",
        "scripts.global_validate",
        "--root",
        str(root),
        "--out",
        str(out_path),
    ]
    if mode_flag:
        cmd.append(mode_flag)
    cmd.append("--stages")
    cmd.extend(stage_names)
    if args.profile:
        cmd.append("--profile")
    if args.stage_timeout_seconds is not None:
        cmd.extend(["--stage-timeout-seconds", str(args.stage_timeout_seconds)])
    if args.history:
        cmd.append("--history")
    if args.trend:
        cmd.append("--trend")
    if args.trend_baseline:
        cmd.extend(["--trend-baseline", args.trend_baseline])
    if args.no_history:
        cmd.append("--no-history")
    if args.no_db_log:
        cmd.append("--no-db-log")
    if args.full_math_program:
        cmd.append("--full-math-program")

    completed = subprocess.run(cmd, cwd=str(root))
    return completed.returncode
