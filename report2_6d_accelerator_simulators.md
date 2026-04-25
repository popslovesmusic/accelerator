# Report 2: 6D Accelerator Simulator Deliverables

## Overview

This report documents the implemented CPU-first 6D accelerator simulation deliverables created from the Optiplex task specification. The work includes two separate simulators:

- A simple linear 6D accelerator simulator.
- A simple circular 6D accelerator simulator.

Both are reduced research models intended for reproducible studies, diagnostics, early research writing, and future expansion. They do not require GPU support or external accelerator physics libraries.

## Hardware Target

Target machine:

```text
Dell Optiplex
12 logical CPU cores
24 GB RAM
GPU not required
```

Design priorities:

- CPU-first execution.
- Vectorized NumPy operations.
- Simple code structure.
- Reproducible seeded runs.
- Avoid saving every particle at every step.
- Preserve compatibility with the current config and output formats.

## Linear 6D Simulator

Project directory:

```text
D:\acellorator\accelerator_sim_v1
```

Main files:

- `accelerator_sim_v1/sim.py`
- `accelerator_sim_v1/configs/optiplex_default.json`
- `accelerator_sim_v1/configs/optiplex_stretch.json`
- `accelerator_sim_v1/README.md`

### State Vector

```text
x, px, y, py, z, delta
```

### Implemented Elements

- Drift
- Quadrupole
- RF cavity
- Circular aperture

### Default Run Command

```powershell
cd D:\acellorator\accelerator_sim_v1
python sim.py --config configs/optiplex_default.json --out outputs/run_default
```

### Default Run Results

```text
Particles: 10,000
Steps: 1,000
Final alive count: 9,853
Lost count: 147
Survival fraction: 0.9853
Snapshots written: 11
Metrics rows: 1,001
Runtime: about 6 seconds
```

### Verification Checks

The linear simulator was checked for:

- Successful execution without crash.
- `metrics.csv` written.
- `summary.json` written.
- Compressed NPZ snapshots written.
- Same seed produced identical `metrics.csv`.
- `alive_count` never increases.
- `survival_fraction` remains between 0 and 1.

### Linear Outputs

Default output directory:

```text
D:\acellorator\accelerator_sim_v1\outputs\run_default
```

Generated files:

- `metrics.csv`
- `summary.json`
- `snapshots/*.npz`
- `figures/survival_fraction.png`
- `figures/transverse_rms.png`
- `figures/delta_rms.png`

## Circular 6D Simulator

Project directory:

```text
D:\acellorator\circular_accelerator_sim_v1
```

Main files:

- `circular_accelerator_sim_v1/ring_sim.py`
- `circular_accelerator_sim_v1/configs/optiplex_ring_default.json`
- `circular_accelerator_sim_v1/configs/optiplex_ring_stretch.json`
- `circular_accelerator_sim_v1/README.md`

### State Vector

```text
x, px, y, py, z, delta
```

### Circular-Specific Behavior

- Repeated ring lattice tracked turn by turn.
- Longitudinal coordinate `z` is wrapped into one circumference after each turn.
- Linear momentum-compaction slip is applied once per turn.
- RF cavity phase is computed from `z / circumference`.
- Circular aperture loss is applied in transverse `x/y`.

### Default Run Command

```powershell
cd D:\acellorator\circular_accelerator_sim_v1
python ring_sim.py --config configs/optiplex_ring_default.json --out outputs/ring_default
```

### Default Run Results

```text
Particles: 10,000
Turns: 500
Final alive count: 9,905
Lost count: 95
Survival fraction: 0.9905
Snapshots written: 11
Metrics rows: 501
Runtime: about 3.2 seconds
```

### Verification Checks

The circular simulator was checked for:

- Successful execution without crash.
- `turn_metrics.csv` written.
- `summary.json` written.
- Compressed NPZ snapshots written.
- Same seed produced identical `turn_metrics.csv`.
- `alive_count` never increases.
- `survival_fraction` remains between 0.9905 and 1.0 in the default run.

### Circular Outputs

Default output directory:

```text
D:\acellorator\circular_accelerator_sim_v1\outputs\ring_default
```

Generated files:

- `turn_metrics.csv`
- `summary.json`
- `snapshots/*.npz`
- `figures/survival_fraction.png`
- `figures/transverse_rms.png`
- `figures/z_rms.png`
- `figures/delta_rms.png`

## Model Limits

Both simulators are reduced research models. They are useful for controlled studies, diagnostics, and development, but they are not full accelerator physics engines.

Currently excluded:

- Space charge
- Wakefields
- Realistic RF cavity field maps
- Detailed magnetic field maps
- Full coupled nonlinear dynamics
- Synchrotron radiation
- Detailed collimation physics beyond aperture loss

Circular simulator additionally excludes:

- Radiation damping
- Quantum excitation
- High-fidelity storage-ring or synchrotron dynamics

## Recommended Next Steps

Recommended next implementation tasks:

- Add formal validation scripts for both simulators.
- Add config-driven lattice import/export tests.
- Add parameter scans for aperture radius, focusing strength, and RF voltage.
- Add comparison plots across runs.
- Add an R730-scale config for larger particle counts and longer runs.
- Add optional elliptical aperture and dipole elements.
