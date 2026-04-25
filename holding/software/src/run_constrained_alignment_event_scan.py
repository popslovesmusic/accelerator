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


def build_output_dir(
    base_output_dir: Path,
    a_w: float,
    a_s: float,
    b: float,
    c: float,
    chi_ref: float,
    chi_residue: float,
) -> Path:
    return base_output_dir / (
        f"aw_{a_w:.2f}__as_{a_s:.2f}__b_{b:.2f}__c_{c:.2f}__cr_{chi_ref:.2f}__cs_{chi_residue:.2f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a constrained-alignment event-map parameter scan")
    parser.add_argument("--config", required=True, help="Anchor JSON config")
    parser.add_argument("--a-w-values", required=True, help="Comma-separated a_w values")
    parser.add_argument("--a-s-values", required=True, help="Comma-separated a_s values")
    parser.add_argument("--b-values", required=True, help="Comma-separated b values")
    parser.add_argument("--c-values", required=True, help="Comma-separated c values")
    parser.add_argument("--chi-ref-values", required=True, help="Comma-separated chi_ref values")
    parser.add_argument("--chi-residue-values", required=True, help="Comma-separated chi_residue values")
    parser.add_argument("--scan-output-root", required=True, help="Directory for scan outputs")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    anchor = load_run_config(config_path)
    a_w_values = parse_float_list(args.a_w_values)
    a_s_values = parse_float_list(args.a_s_values)
    b_values = parse_float_list(args.b_values)
    c_values = parse_float_list(args.c_values)
    chi_ref_values = parse_float_list(args.chi_ref_values)
    chi_residue_values = parse_float_list(args.chi_residue_values)
    scan_output_root = Path(args.scan_output_root).resolve()
    scan_output_root.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for a_w in a_w_values:
        for a_s in a_s_values:
            for b_value in b_values:
                for c_value in c_values:
                    for chi_ref in chi_ref_values:
                        for chi_residue in chi_residue_values:
                            output_dir = build_output_dir(
                                scan_output_root,
                                a_w,
                                a_s,
                                b_value,
                                c_value,
                                chi_ref,
                                chi_residue,
                            )
                            model = replace(
                                anchor.model,
                                a_w=a_w,
                                a_s=a_s,
                                b=b_value,
                                c=c_value,
                                chi_ref=chi_ref,
                                chi_residue=chi_residue,
                            )
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
                                    "a_w": a_w,
                                    "a_s": a_s,
                                    "b": b_value,
                                    "c": c_value,
                                    "chi_ref": chi_ref,
                                    "chi_residue": chi_residue,
                                    "output_dir": str(output_dir),
                                    "mean_mismatch": final["mean_mismatch"],
                                    "support_fraction": final["support_fraction"],
                                    "region_count": final["region_count"],
                                    "mean_residue": final["mean_residue"],
                                    "mean_reservoir": final["mean_reservoir"],
                                    "event_count": final["event_count"],
                                    "phase_alignment_score": final["phase_alignment_score"],
                                    "cycle_similarity_score": final["cycle_similarity_score"],
                                    "reservoir_to_deviation_conversion_efficiency": final[
                                        "reservoir_to_deviation_conversion_efficiency"
                                    ],
                                    "event_closure_count": final["event_closure_count"],
                                }
                            )

    summary_json_path = scan_output_root / "scan_summary.json"
    summary_csv_path = scan_output_root / "scan_summary.csv"
    summary_json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with summary_csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "a_w",
                "a_s",
                "b",
                "c",
                "chi_ref",
                "chi_residue",
                "output_dir",
                "mean_mismatch",
                "support_fraction",
                "region_count",
                "mean_residue",
                "mean_reservoir",
                "event_count",
                "phase_alignment_score",
                "cycle_similarity_score",
                "reservoir_to_deviation_conversion_efficiency",
                "event_closure_count",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
