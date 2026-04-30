import argparse
import csv
import json
from pathlib import Path

import pandas as pd


def _load_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def _safe_mean(series) -> float:
    try:
        s = pd.to_numeric(series, errors="coerce").dropna()
        return float(s.mean()) if len(s) else 0.0
    except Exception:
        return 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a compact per-run summary table for RT-1 program runs")
    parser.add_argument("--index", required=True, help="Path to analysis/index.json")
    parser.add_argument("--out_csv", required=True, help="Path to write summary_table.csv")
    args = parser.parse_args()

    idx = _load_json(Path(args.index))
    rows = []

    for run in idx["runs"]:
        summary = _load_json(Path(run["summary_path"]))
        final = summary.get("final_metrics", {}) or {}
        rt1_final = summary.get("rt1_final", {}) or {}
        metrics_path = Path(run["out_dir"]) / "metrics.csv"

        df = None
        if metrics_path.exists():
            df = pd.read_csv(metrics_path)

        model = run["model"]
        out_row = {
            "run_name": run["run_name"],
            "model": model,
            "variant": run["variant"],
            "seed": run["seed"],
            "inadmissible_activation_fraction_max": rt1_final.get(
                "inadmissible_activation_fraction_max",
                rt1_final.get("inadmissible_edge_add_fraction_max", 0.0),
            ),
            "traceability_failure_fraction_max": rt1_final.get("traceability_failure_fraction_max", 0.0),
            "signal_outside_domain_fraction_max": rt1_final.get("signal_outside_domain_fraction_max", ""),
            "corridor_signal_corr": rt1_final.get("corridor_signal_corr", ""),
        }

        if df is not None and len(df):
            if model == "ca":
                out_row["activation_fraction_of_admissible_mean"] = _safe_mean(df.get("activation_fraction_of_admissible", []))
            elif model == "graph":
                # Only average when candidates exist to reflect asymmetry meaningfully.
                cand = pd.to_numeric(df.get("candidate_pairs", []), errors="coerce").fillna(0)
                sub = df.loc[cand > 0]
                out_row["recouple_asymmetry_mean"] = _safe_mean(sub.get("recouple_asymmetry", [])) if len(sub) else 0.0
            elif model == "rd":
                out_row["signal_outside_domain_fraction_mean"] = _safe_mean(df.get("signal_outside_domain_fraction", []))

        rows.append(out_row)

    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({k for r in rows for k in r.keys()})
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()

