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


def _corr(x: list[float], y: list[float]) -> float:
    a = np.array(x, dtype=float)
    b = np.array(y, dtype=float)
    if a.size != b.size or a.size < 2:
        return float("nan")
    if np.allclose(a, a[0]) or np.allclose(b, b[0]):
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def main() -> None:
    parser = argparse.ArgumentParser(description="Cross-model comparison for RT-1 program runs")
    parser.add_argument("--index", required=True, help="Path to analysis/index.json")
    parser.add_argument("--out", required=True, help="Path to write cross_model_comparison.json")
    args = parser.parse_args()

    index = _load_json(Path(args.index))
    runs = index["runs"]

    # Collect per-run scalar metrics to enable cross-model comparison.
    per_run = []
    for r in runs:
        summary = _load_json(Path(r["summary_path"]))
        rt1_final = summary.get("rt1_final", {})
        per_run.append(
            {
                "run_name": r["run_name"],
                "model": r["model"],
                "variant": r["variant"],
                "seed": r["seed"],
                "inadmissible_activation_fraction_max": _safe_float(
                    rt1_final.get("inadmissible_activation_fraction_max", rt1_final.get("inadmissible_edge_add_fraction_max"))
                ),
                "signal_outside_domain_fraction_max": _safe_float(rt1_final.get("signal_outside_domain_fraction_max")),
                "recouple_asymmetry_proxy": _safe_float(rt1_final.get("corridor_signal_corr")),
            }
        )

    # Compare baseline-only across models.
    baseline = [r for r in per_run if r["variant"] == "baseline"]
    models = sorted(set(r["model"] for r in baseline))
    seeds = sorted(set(r["seed"] for r in baseline))

    # Build seed-aligned vectors per model for inadmissible activation metric.
    vecs = {}
    for m in models:
        vec = []
        for s in seeds:
            match = [r for r in baseline if r["model"] == m and r["seed"] == s]
            vec.append(match[0]["inadmissible_activation_fraction_max"] if match else float("nan"))
        vecs[m] = vec

    # Single headline correlation: CA vs RD where defined, else NaN.
    correlation = float("nan")
    if "ca" in vecs and "rd" in vecs:
        correlation = _corr(vecs["ca"], vecs["rd"])

    # Agreement type: heuristic based on whether all baseline runs have ~0 inadmissible activations.
    tol = 1e-12
    baseline_vals = [r["inadmissible_activation_fraction_max"] for r in baseline if not np.isnan(r["inadmissible_activation_fraction_max"])]
    all_zero_like = all(abs(v) <= tol for v in baseline_vals) if baseline_vals else False
    agreement_type = "strong" if all_zero_like else "partial"

    out_obj = {
        "generated_from": str(Path(args.index).resolve()),
        "baseline_models": models,
        "seeds": seeds,
        "inadmissible_activation_vectors": vecs,
        "correlation": correlation if not np.isnan(correlation) else 0.0,
        "agreement_type": agreement_type,
        "qualitative_match": [
            "inadmissible_activation_fraction_max ~ 0 indicates RT-1 P1 consistency (model-specific admissibility definitions)."
        ],
        "notes": [
            "Correlation may be undefined when one model's metric is constant across seeds; in that case it is reported as 0.0 and should not be over-interpreted."
        ]
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out_obj, f, indent=2)

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()

