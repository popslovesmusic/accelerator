# Spectral Analysis Layer (v1)

This tool reveals hidden structures, coherent modes, and "phase packets" across the `acellorator` simulations by performing Fast Fourier Transform (FFT) on spatial fields and temporal signals.

## Theoretical Basis

- **Temporal Coherence:** Periodic oscillations in metrics (like emittance or phase order) reveal characteristic frequencies of system instability or locking.
- **Spatial Modes:** Patterns in 2D fields (like Reaction-Diffusion corridors) contain dominant wavelengths that can be quantified via spatial FFT.
- **Phase Packets:** High-power spectral bands in frequency space directly represent the concentrated information/energy packets defined in the theoretical framework.

## Usage

### 1. Temporal Mode
Analyze a time-series CSV (Power Spectrum):
```powershell
python analyze_spectrum.py --mode temporal --file ../kuramoto_sim_v1/outputs/run_01/metrics.csv --col order_parameter
```

### 2. Spatial Mode
Analyze a 2D snapshot (Spatial Modes):
```powershell
python analyze_spectrum.py --mode spatial --file ../rd_moving_boundary_sim_v1/outputs/run_01/snapshots/step_0500.npz
```

## Outputs

- `spectrum_report.json`: List of dominant frequencies/wavenumbers and their power.
- `plots/`: Periodograms and 2D spatial power heatmaps.
