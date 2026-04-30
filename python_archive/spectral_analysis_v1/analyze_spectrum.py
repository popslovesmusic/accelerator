import os
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from spectral_engine import compute_temporal_psd, compute_spatial_power, radial_profile, detect_dominant_modes

def analyze_temporal(file_path, column, output_dir):
    df = pd.read_csv(file_path)
    if column not in df.columns:
        print(f"Column {column} not found in {file_path}")
        return
        
    signal = df[column].values
    # Detrend to remove DC component
    signal = signal - np.mean(signal)
    
    # Assume unit sampling freq if time not present
    f, psd = compute_temporal_psd(signal)
    
    if f is not None:
        modes = detect_dominant_modes(f, psd)
        
        report = {
            "mode": "temporal",
            "source": file_path,
            "column": column,
            "dominant_modes": modes
        }
        
        with open(os.path.join(output_dir, 'spectrum_report.json'), 'w') as f_out:
            json.dump(report, f_out, indent=2)
            
        print(f"Temporal spectrum report saved to {output_dir}")
        
        # Optional Plotting
        try:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(10, 5))
            plt.semilogy(f, psd)
            plt.xlabel('Frequency')
            plt.ylabel('Power')
            plt.title(f'Power Spectral Density: {column}')
            plt.grid(True)
            plt.savefig(os.path.join(output_dir, 'temporal_psd.png'))
            plt.close()
        except ImportError:
            pass

def analyze_spatial(file_path, output_dir):
    data = np.load(file_path)
    # Most snapshots have 'state' or 'epsilon'
    if 'state' in data:
        grid = data['state']
    elif 'epsilon' in data:
        grid = data['epsilon']
    else:
        # try first key
        grid = data[data.files[0]]

    # Ensure 2D
    if grid.ndim > 2:
        grid = grid[0] # take first slice if 3D
        
    power_2d = compute_spatial_power(grid)
    radial_prof = radial_profile(power_2d)
    
    # Wavenumber k
    k = np.arange(len(radial_prof))
    modes = detect_dominant_modes(k, radial_prof)
    
    report = {
        "mode": "spatial",
        "source": file_path,
        "dominant_wavenumbers": modes
    }
    
    with open(os.path.join(output_dir, 'spectrum_report.json'), 'w') as f_out:
        json.dump(report, f_out, indent=2)
        
    print(f"Spatial spectrum report saved to {output_dir}")
    
    # Optional Plotting
    try:
        import matplotlib.pyplot as plt
        # 1. 2D Power
        plt.figure(figsize=(8, 8))
        plt.imshow(np.log10(power_2d + 1e-12), cmap='magma')
        plt.colorbar(label='log10(Power)')
        plt.title('2D Spatial Power Spectrum')
        plt.savefig(os.path.join(output_dir, 'spatial_power_2d.png'))
        plt.close()
        
        # 2. Radial Profile
        plt.figure(figsize=(10, 5))
        plt.plot(k, radial_prof)
        plt.xlabel('Wavenumber (k)')
        plt.ylabel('Power')
        plt.title('Radial Average of Power Spectrum')
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, 'spatial_power_radial.png'))
        plt.close()
    except ImportError:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spectral Analysis Layer")
    parser.add_argument("--mode", type=str, choices=['temporal', 'spatial'], required=True)
    parser.add_argument("--file", type=str, required=True, help="Input CSV or NPZ file")
    parser.add_argument("--col", type=str, default="order_parameter", help="Column for temporal mode")
    parser.add_argument("--out", type=str, default="outputs/spectral_report", help="Output directory")
    args = parser.parse_args()
    
    os.makedirs(args.out, exist_ok=True)
    
    if args.mode == 'temporal':
        analyze_temporal(args.file, args.col, args.out)
    else:
        analyze_spatial(args.file, args.out)
