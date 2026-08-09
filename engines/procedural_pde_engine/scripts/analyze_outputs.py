import os
import json
import pandas as pd
import numpy as np
from pathlib import Path

def analyze_campaign(campaign_dir):
    campaign_dir = Path(campaign_dir)
    seed_dirs = [d for d in campaign_dir.iterdir() if d.is_dir() and d.name.startswith("seed_")]
    
    all_metrics = []
    
    for seed_dir in seed_dirs:
        timeseries_path = seed_dir / "metrics_timeseries.csv"
        if not timeseries_path.exists():
            continue
            
        df = pd.read_csv(timeseries_path)
        
        # Compute per-seed metrics
        seed_res = {
            "seed": int(seed_dir.name.split("_")[1]),
            "final_residue_coherence": df["residue_coherence"].iloc[-1],
            "mean_residue_coherence": df["residue_coherence"].mean(),
            "max_residue_coherence": df["residue_coherence"].max(),
            "final_corridor_count": df["corridor_count"].iloc[-1],
            "mean_corridor_count": df["corridor_count"].mean(),
            "proto_corridor_score_mean": df["proto_corridor_score_mean"].mean(),
            "proto_corridor_score_max": df["proto_corridor_score_max"].max(),
            "phase_alignment_mean": df["phase_alignment_mean"].mean(),
            "corridor_area_fraction_mean": df["corridor_area_fraction"].mean(),
            "corridor_area_fraction_final": df["corridor_area_fraction"].iloc[-1],
        }
        
        # Mature corridor lifetime: steps where corridor_area_fraction > 0.01 (mature)
        grid_size = 256 * 256
        threshold = 0.01
        mature_active = df["corridor_area_fraction"] > threshold
        if mature_active.any():
            diff = mature_active.astype(int).diff().fillna(0)
            starts = (diff == 1).sum()
            if starts == 0 and mature_active.iloc[0]: starts = 1
            seed_res["mature_corridor_lifetime"] = float(mature_active.sum() / max(1, starts))
            seed_res["corridor_activation_count"] = int(starts)
        else:
            seed_res["mature_corridor_lifetime"] = 0.0
            seed_res["corridor_activation_count"] = 0
            
        # Proto-corridor lifetime: steps where proto_corridor_score_max > 0.0001 AND mature_active is false
        proto_active = (df["proto_corridor_score_max"] > 0.0001) & (~mature_active)
        if proto_active.any():
            diff = proto_active.astype(int).diff().fillna(0)
            starts = (diff == 1).sum()
            if starts == 0 and proto_active.iloc[0]: starts = 1
            seed_res["proto_corridor_lifetime"] = float(proto_active.sum() / max(1, starts))
        else:
            seed_res["proto_corridor_lifetime"] = 0.0

        # Basin lifetime: steps where residue_coherence > threshold
        coherence_threshold = df["residue_coherence"].mean() * 0.5
        basin_active = df["residue_coherence"] > coherence_threshold
        if basin_active.any():
            diff = basin_active.astype(int).diff().fillna(0)
            starts = (diff == 1).sum()
            if starts == 0 and basin_active.iloc[0]: starts = 1
            seed_res["basin_lifetime"] = float(basin_active.sum() / max(1, starts))
            seed_res["basin_to_corridor_conversion_rate"] = float(seed_res["corridor_activation_count"] / max(1, starts))
        else:
            seed_res["basin_lifetime"] = 0.0
            seed_res["basin_to_corridor_conversion_rate"] = 0.0
            
        seed_res["collapse_locality"] = float(df["corridor_count"].max() / (df["corridor_count"].mean() + 1e-6))
        seed_res["reformation_latency"] = 100.0 # Placeholder
        
        all_metrics.append(seed_res)
        
    if not all_metrics:
        return None
        
    df_all = pd.DataFrame(all_metrics)
    
    summary = {
        "mean_residue_coherence": float(df_all["final_residue_coherence"].mean()),
        "mean_mature_corridor_lifetime": float(df_all["mature_corridor_lifetime"].mean()),
        "mean_proto_corridor_lifetime": float(df_all["proto_corridor_lifetime"].mean()),
        "mean_basin_lifetime": float(df_all["basin_lifetime"].mean()),
        "mean_basin_to_corridor_conversion_rate": float(df_all["basin_to_corridor_conversion_rate"].mean()),
        "mean_corridor_area_fraction": float(df_all["corridor_area_fraction_mean"].mean()),
        "mean_phase_alignment": float(df_all["phase_alignment_mean"].mean()),
        "cross_seed_variance": {
            "residue_coherence": float(df_all["final_residue_coherence"].var()),
            "mature_corridor_lifetime": float(df_all["mature_corridor_lifetime"].var())
        },
        "seeds_completed": len(all_metrics)
    }
    
    with open(campaign_dir / "multi_seed_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
        
    return summary

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_dir", help="Path to the campaign output directory")
    args = parser.parse_args()
    
    res = analyze_campaign(args.campaign_dir)
    if res:
        print(json.dumps(res, indent=2))
    else:
        print("No metrics found to analyze.")
