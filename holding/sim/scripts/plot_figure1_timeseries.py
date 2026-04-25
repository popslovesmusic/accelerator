#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt

TIME_CANDIDATES = ["t", "time", "time_t", "time_value"]
EPS_CANDIDATES = ["epsilon", "epsilon_mean", "epsilon_t", "epsilon_value"]
RHO_CANDIDATES = ["rho", "rho_mean", "rho_t", "rho_value"]
R_CANDIDATES = ["R", "residue", "residue_mean", "R_t", "residue_value"]

def pick_col(df, candidates, required=True):
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        raise ValueError(f"Could not find any of columns: {candidates}. Available columns: {list(df.columns)}")
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to timeseries_global.csv")
    ap.add_argument("--output", required=True, help="Path to output PNG")
    ap.add_argument("--title", default="Representative ODE trajectories")
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    tcol = pick_col(df, TIME_CANDIDATES)
    ecol = pick_col(df, EPS_CANDIDATES)
    rcol = pick_col(df, RHO_CANDIDATES, required=False)
    Rcol = pick_col(df, R_CANDIDATES, required=False)

    plt.figure(figsize=(8, 5))
    plt.plot(df[tcol], df[ecol], label="epsilon")
    if rcol:
        plt.plot(df[tcol], df[rcol], label="rho")
    if Rcol:
        plt.plot(df[tcol], df[Rcol], label="R")
    plt.xlabel("time")
    plt.ylabel("value")
    plt.title(args.title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.output, dpi=200)

if __name__ == "__main__":
    main()