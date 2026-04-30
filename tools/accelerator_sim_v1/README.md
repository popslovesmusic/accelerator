# Simple 6D Accelerator Simulation

CPU-first reduced accelerator simulation for the Dell Optiplex target.

The state vector is:

```text
x, px, y, py, z, delta
```

This is a simple research model, not a replacement for a production accelerator code. It is designed to be readable, reproducible, and expandable.

## Run

From this directory:

```powershell
python sim.py --config configs/optiplex_default.json --out outputs/run_default
```

Stretch run:

```powershell
python sim.py --config configs/optiplex_stretch.json --out outputs/run_stretch
```

## Model

Included:

- Gaussian 6D bunch initialization
- Alive mask for particle loss
- Drift elements
- Linear quadrupole elements
- Simple sinusoidal RF cavity kick to `delta`
- Circular aperture loss using `x^2 + y^2 > radius^2`
- Metrics CSV
- Summary JSON
- Compressed NPZ snapshots at a configurable interval

Excluded for now:

- Space charge
- Wakefields
- Real RF or magnetic field maps
- Full nonlinear coupled dynamics
- Synchrotron radiation
- Detailed collimation physics

## Outputs

Each run writes:

- `metrics.csv`: per-step aggregate beam metrics
- `summary.json`: final summary, configuration identity, runtime, and model limits
- `snapshots/*.npz`: compressed particle state and alive mask snapshots
- `figures/*.png`: optional plots if Matplotlib is installed

The simulator intentionally avoids saving every particle at every step.

## Metrics

Tracked metrics include:

- `alive_count`
- `survival_fraction`
- `x_mean`, `x_rms`
- `y_mean`, `y_rms`
- `z_mean`, `z_rms`
- `delta_mean`, `delta_rms`
- `px_rms`, `py_rms`
- `emittance_proxy_x`
- `emittance_proxy_y`

## Notes

The default config uses 10,000 particles and 1,000 steps. The stretch config uses 50,000 particles and the same number of steps. Both are intended to run without GPU support.
