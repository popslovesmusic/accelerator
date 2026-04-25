#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt

FLOOR_CANDIDATES = ["epsilon_floor_estimate", "floor_estimate", "epsilon_last_window_mean"]
DT_CANDIDATES = ["dt"]
TFINAL_CANDIDATES = ["t_final"]
BW_CANDIDATES = ["near_floor_bandwidth", "bandwidth"]
ID_CANDIDATES = ["candidate_id", "run_id", "stage_id"]

def pick_col(df, candidates, required=True):
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        raise ValueError(f"Could not find any of columns: {candidates}. Available columns: {list(df.columns)}")
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to top_refined_floor_candidates.csv or refinement summary CSV")
    ap.add_argument("--output", required=True, help="Path to output PNG")
    ap.add_argument("--title", default="Near-floor refinement behavior")
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    floor_col = pick_col(df, FLOOR_CANDIDATES)
    dt_col = pick_col(df, DT_CANDIDATES, required=False)
    tf_col = pick_col(df, TFINAL_CANDIDATES, required=False)
    bw_col = pick_col(df, BW_CANDIDATES, required=False)
    id_col = pick_col(df, ID_CANDIDATES, required=False)

    plt.figure(figsize=(8, 5))

    if dt_col:
        x = df[dt_col]
        xlabel = "dt"
    elif tf_col:
        x = df[tf_col]
        xlabel = "t_final"
    else:
        x = range(len(df))
        xlabel = "run index"

    plt.plot(x, df[floor_col], marker='o', label="epsilon_floor_estimate")
    if bw_col:
        plt.plot(x, df[bw_col], marker='x', label="near_floor_bandwidth")

    plt.xlabel(xlabel)
    plt.ylabel("value")
    plt.title(args.title)

    if id_col:
        try:
            for xi, yi, label in zip(x, df[floor_col], df[id_col].astype(str)):
                plt.annotate(label, (xi, yi), fontsize=6, alpha=0.7)
        except Exception:
            pass

    plt.legend()
    plt.tight_layout()
    plt.savefig(args.output, dpi=200)

if __name__ == "__main__":
    main()