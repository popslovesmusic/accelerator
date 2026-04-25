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
    threshold: float,
    sharpness: float,
    eta_support: float,
    eta_S: float,
) -> Path:
    return base_output_dir / (
        f"it_{threshold:.2f}__ks_{sharpness:.2f}__es_{eta_support:.2f}__eS_{eta_S:.2f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a constrained-alignment identity-gate parameter scan")
    parser.add_argument("--config", required=True, help="Anchor JSON config")
    parser.add_argument("--identity-threshold-values", required=True, help="Comma-separated identity_gate_threshold values")
    parser.add_argument("--identity-sharpness-values", required=True, help="Comma-separated identity_gate_sharpness values")
    parser.add_argument("--eta-support-values", required=True, help="Comma-separated identity_eta_support values")
    parser.add_argument("--eta-s-values", required=True, help="Comma-separated identity_eta_S values")
    parser.add_argument("--scan-output-root", required=True, help="Directory for scan outputs")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    anchor = load_run_config(config_path)
    threshold_values = parse_float_list(args.identity_threshold_values)
    sharpness_values = parse_float_list(args.identity_sharpness_values)
    eta_support_values = parse_float_list(args.eta_support_values)
    eta_s_values = parse_float_list(args.eta_s_values)
    scan_output_root = Path(args.scan_output_root).resolve()
    scan_output_root.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for threshold in threshold_values:
        for sharpness in sharpness_values:
            for eta_support in eta_support_values:
                for eta_S in eta_s_values:
                    output_dir = build_output_dir(scan_output_root, threshold, sharpness, eta_support, eta_S)
                    model = replace(
                        anchor.model,
                        identity_gate_threshold=threshold,
                        identity_gate_sharpness=sharpness,
                        identity_eta_support=eta_support,
                        identity_eta_S=eta_S,
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
                            "identity_gate_threshold": threshold,
                            "identity_gate_sharpness": sharpness,
                            "identity_eta_support": eta_support,
                            "identity_eta_S": eta_S,
                            "output_dir": str(output_dir),
                            "support_fraction": final["support_fraction"],
                            "trigger_fraction": final["trigger_fraction"],
                            "region_count": final["region_count"],
                            "cycle_similarity_score": final["cycle_similarity_score"],
                            "event_closure_count": final["event_closure_count"],
                            "phase_alignment_score": final["phase_alignment_score"],
                            "mean_identity_proxy": final["mean_identity_proxy"],
                            "on_core_return_fraction": final["on_core_return_fraction"],
                            "off_core_return_fraction": final["off_core_return_fraction"],
                            "reservoir_to_deviation_conversion_efficiency": final[
                                "reservoir_to_deviation_conversion_efficiency"
                            ],
                        }
                    )

    summary_json_path = scan_output_root / "scan_summary.json"
    summary_csv_path = scan_output_root / "scan_summary.csv"
    summary_json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with summary_csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "identity_gate_threshold",
                "identity_gate_sharpness",
                "identity_eta_support",
                "identity_eta_S",
                "output_dir",
                "support_fraction",
                "trigger_fraction",
                "region_count",
                "cycle_similarity_score",
                "event_closure_count",
                "phase_alignment_score",
                "mean_identity_proxy",
                "on_core_return_fraction",
                "off_core_return_fraction",
                "reservoir_to_deviation_conversion_efficiency",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
