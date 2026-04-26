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
    parser = argparse.ArgumentParser(description="Generate a per-run summary table for CDHDS dual-laws program")
    parser.add_argument("--index", required=True, help="Path to analysis/index.json")
    parser.add_argument("--out_csv", required=True, help="Path to write summary_table.csv")
    args = parser.parse_args()

    idx = _load_json(Path(args.index))
    rows = []

    for run in idx["runs"]:
        summary = _load_json(Path(run["summary_path"]))
        cdhds_final = summary.get("cdhds_final", {}) or {}
        metrics_path = Path(run["out_dir"]) / "metrics.csv"
        df = pd.read_csv(metrics_path) if metrics_path.exists() else None

        model = run["model"]
        out_row = {
            "run_name": run["run_name"],
            "model": model,
            "variant": run["variant"],
            "seed": run["seed"],
        }

        if model == "rd":
            out_row.update(
                {
                    "outside_activation_no_recouple_fraction_max": cdhds_final.get(
                        "outside_activation_no_recouple_fraction_max", 0.0
                    ),
                    "signal_outside_domain_fraction_max": cdhds_final.get("signal_outside_domain_fraction_max", 0.0),
                    "delta_recouple_events_total": cdhds_final.get("delta_recouple_events_total", 0),
                }
            )
            if df is not None and len(df):
                out_row["signal_outside_domain_fraction_mean"] = _safe_mean(df.get("signal_outside_domain_fraction", []))
        elif model == "fsa":
            out_row.update(
                {
                    "forbidden_occupancy_events_total": cdhds_final.get("forbidden_occupancy_events_total", 0),
                    "transitions_to_forbidden_total": cdhds_final.get("transitions_to_forbidden_total", 0),
                    "active_without_admissible_continuation_total": cdhds_final.get(
                        "active_without_admissible_continuation_total", 0
                    ),
                }
            )
            if df is not None and len(df):
                out_row["active_count_final"] = int(df.iloc[-1].get("active_count", 0))
                out_row["transitions_count_mean"] = _safe_mean(df.get("transitions_count", []))
        elif model == "graph":
            out_row.update(
                {
                    "inadmissible_edge_add_fraction_max": cdhds_final.get("inadmissible_edge_add_fraction_max", 0.0),
                    "traceability_failure_fraction_max": cdhds_final.get("traceability_failure_fraction_max", 0.0),
                }
            )
            if df is not None and len(df):
                cand = pd.to_numeric(df.get("candidate_pairs", []), errors="coerce").fillna(0)
                sub = df.loc[cand > 0]
                out_row["recouple_asymmetry_mean"] = _safe_mean(sub.get("recouple_asymmetry", [])) if len(sub) else 0.0

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

