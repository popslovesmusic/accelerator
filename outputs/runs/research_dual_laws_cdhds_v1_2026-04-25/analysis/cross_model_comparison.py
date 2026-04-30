import argparse
import json
from pathlib import Path

import numpy as np


def _load_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def _safe_float(x) -> float:
    try:
        if x is None:
            return float("nan")
        return float(x)
    except Exception:
        return float("nan")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cross-model comparison for CDHDS dual-laws program")
    parser.add_argument("--index", required=True, help="Path to analysis/index.json")
    parser.add_argument("--out", required=True, help="Path to write cross_model_comparison.json")
    args = parser.parse_args()

    index = _load_json(Path(args.index))
    runs = index["runs"]

    baseline = [r for r in runs if r["variant"] == "baseline"]

    # Extract key invariants per baseline model.
    per_model = {}
    for r in baseline:
        summary = _load_json(Path(r["summary_path"]))
        model = r["model"]
        cdhds_final = summary.get("cdhds_final", {}) or {}
        if model == "rd":
            per_model.setdefault("rd", []).append(
                {
                    "seed": r["seed"],
                    "outside_activation_no_recouple_fraction_max": _safe_float(
                        cdhds_final.get("outside_activation_no_recouple_fraction_max")
                    ),
                }
            )
        elif model == "fsa":
            per_model.setdefault("fsa", []).append(
                {
                    "seed": r["seed"],
                    "forbidden_occupancy_events_total": _safe_float(cdhds_final.get("forbidden_occupancy_events_total")),
                    "transitions_to_forbidden_total": _safe_float(cdhds_final.get("transitions_to_forbidden_total")),
                    "active_without_admissible_continuation_total": _safe_float(
                        cdhds_final.get("active_without_admissible_continuation_total")
                    ),
                }
            )
        elif model == "graph":
            per_model.setdefault("graph", []).append(
                {
                    "seed": r["seed"],
                    "inadmissible_edge_add_fraction_max": _safe_float(cdhds_final.get("inadmissible_edge_add_fraction_max")),
                    "traceability_failure_fraction_max": _safe_float(
                        cdhds_final.get("traceability_failure_fraction_max")
                    ),
                }
            )

    # Decide agreement type for the main invariant: "no forbidden-origin updates / no forbidden-target updates"
    # Here we operationalize as "violations are zero" in each model's best-available indicator.
    def all_zero(vals: list[float], tol: float = 1e-12) -> bool:
        vals2 = [v for v in vals if not np.isnan(v)]
        return bool(vals2) and all(abs(v) <= tol for v in vals2)

    rd_vals = [d["outside_activation_no_recouple_fraction_max"] for d in per_model.get("rd", [])]
    graph_vals = [d["inadmissible_edge_add_fraction_max"] for d in per_model.get("graph", [])]
    fsa_vals = []
    for d in per_model.get("fsa", []):
        fsa_vals.extend(
            [
                d["forbidden_occupancy_events_total"],
                d["transitions_to_forbidden_total"],
                d["active_without_admissible_continuation_total"],
            ]
        )

    rd_ok = all_zero(rd_vals)
    graph_ok = all_zero(graph_vals)
    fsa_ok = all_zero(fsa_vals)

    if rd_ok and graph_ok and fsa_ok:
        agreement_type = "strong"
    elif graph_ok and fsa_ok and not rd_ok:
        agreement_type = "partial"
    else:
        agreement_type = "contradiction"

    out_obj = {
        "generated_from": str(Path(args.index).resolve()),
        "baseline_models": sorted(per_model.keys()),
        "agreement_type": agreement_type,
        "per_model": per_model,
        "qualitative_match": [
            "Graph/FSA invariants are primarily structural (hard gating) and can hold exactly by construction.",
            "RD invariants depend on boundary coupling between domain admissibility (D) and signal transport (S).",
        ],
        "notes": [
            "This comparison uses model-specific indicators because (ℰ≠0) and δ are represented differently across model classes."
        ],
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out_obj, f, indent=2)

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()

