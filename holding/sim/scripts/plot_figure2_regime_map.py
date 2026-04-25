#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt

REGIME_CANDIDATES = ["regime_classification", "classification", "regime"]

def pick_col(df, name_or_candidates):
    if isinstance(name_or_candidates, str):
        if name_or_candidates not in df.columns:
            raise ValueError(f"Column '{name_or_candidates}' not found. Available columns: {list(df.columns)}")
        return name_or_candidates
    for c in name_or_candidates:
        if c in df.columns:
            return c
    raise ValueError(f"Could not find any of columns: {name_or_candidates}. Available columns: {list(df.columns)}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to classification_summary.csv or similar")
    ap.add_argument("--x", required=True, help="Column for x-axis parameter")
    ap.add_argument("--y", required=True, help="Column for y-axis parameter")
    ap.add_argument("--output", required=True, help="Path to output PNG")
    ap.add_argument("--title", default="Regime map")
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    xcol = pick_col(df, args.x)
    ycol = pick_col(df, args.y)
    rcol = pick_col(df, REGIME_CANDIDATES)

    regimes = sorted(df[rcol].astype(str).unique())
    regime_to_code = {r: i for i, r in enumerate(regimes)}
    df["_regime_code"] = df[rcol].astype(str).map(regime_to_code)

    plt.figure(figsize=(7, 5))
    plt.scatter(df[xcol], df[ycol], c=df["_regime_code"])
    plt.xlabel(xcol)
    plt.ylabel(ycol)
    plt.title(args.title)

    handles = []
    for regime in regimes:
        handles.append(plt.Line2D([0], [0], marker='o', linestyle='', label=regime))
    plt.legend(handles=handles, title="regime", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(args.output, dpi=200)

if __name__ == "__main__":
    main()