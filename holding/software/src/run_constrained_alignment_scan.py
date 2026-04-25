from __future__ import annotations

import argparse
import csv
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from .constrained_alignment_v1 import RunConfig, load_run_config, simulate, write_outputs


def parse_float_list(raw: str) -> list[float]:
    values = []
    for part in str(raw).split(","):
        text = part.strip()
        if text:
            values.append(float(text))
    if not values:
        raise ValueError("Expected at least one float value")
    return values


def build_output_dir(base_output_dir: Path, alpha: float, gamma: float, lambda_R: float) -> Path:
    return base_output_dir / f"a_{alpha:.2f}__g_{gamma:.2f}__lr_{lambda_R:.2f}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a constrained-alignment parameter scan")
    parser.add_argument("--config", required=True, help="Anchor JSON config")
    parser.add_argument("--alpha-values", required=True, help="Comma-separated alpha values")
    parser.add_argument("--gamma-values", required=True, help="Comma-separated gamma values")
    parser.add_argument("--lambda-r-values", required=True, help="Comma-separated lambda_R values")
    parser.add_argument("--scan-output-root", required=True, help="Directory for scan outputs")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    anchor = load_run_config(config_path)
    alpha_values = parse_float_list(args.alpha_values)
    gamma_values = parse_float_list(args.gamma_values)
    lambda_r_values = parse_float_list(args.lambda_r_values)
    scan_output_root = Path(args.scan_output_root).resolve()
    scan_output_root.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for alpha in alpha_values:
        for gamma in gamma_values:
            for lambda_r in lambda_r_values:
                output_dir = build_output_dir(scan_output_root, alpha, gamma, lambda_r)
                model = replace(anchor.model, alpha=alpha, gamma=gamma, lambda_R=lambda_r)
                run_config = RunConfig(
                    grid=anchor.grid,
                    model=model,
                    initial_condition=anchor.initial_condition,
                    reference=anchor.reference,
                    output_dir=str(output_dir),
                )
                result = simulate(run_config)
                write_outputs(result, output_dir)
                final = dict(result["diagnostics"][-1])
                rows.append(
                    {
                        "alpha": alpha,
                        "gamma": gamma,
                        "lambda_R": lambda_r,
                        "output_dir": str(output_dir),
                        "mean_mismatch": final["mean_mismatch"],
                        "std_mismatch": final["std_mismatch"],
                        "support_fraction": final["support_fraction"],
                        "region_count": final["region_count"],
                        "closure_distance": final["closure_distance"],
                        "closure_count": final["closure_count"],
                        "mean_residue": final["mean_residue"],
                    }
                )

    summary_json_path = scan_output_root / "scan_summary.json"
    summary_csv_path = scan_output_root / "scan_summary.csv"
    summary_json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with summary_csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "alpha",
                "gamma",
                "lambda_R",
                "output_dir",
                "mean_mismatch",
                "std_mismatch",
                "support_fraction",
                "region_count",
                "closure_distance",
                "closure_count",
                "mean_residue",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
