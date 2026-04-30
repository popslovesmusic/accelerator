# Simple Circular 6D Accelerator Simulation

CPU-first reduced circular accelerator simulation for the Optiplex target.

The state vector is:

```text
x, px, y, py, z, delta
```

The simulator tracks particles turn by turn through a repeated ring lattice. The longitudinal coordinate `z` is wrapped into one circumference after every turn.

## Run

From this directory:

```powershell
python ring_sim.py --config configs/optiplex_ring_default.json --out outputs/ring_default
```

Stretch run:

```powershell
python ring_sim.py --config configs/optiplex_ring_stretch.json --out outputs/ring_stretch
```

## Model

Included:

- Gaussian 6D bunch initialization
- Alive mask for particle loss
- Repeated ring lattice
- Drift elements
- Linear quadrupole elements
- Simple sinusoidal RF cavity kick to `delta`
- Linear momentum-compaction slip applied once per turn
- Circular aperture loss using `x^2 + y^2 > radius^2`
- Turn-level metrics CSV
- Summary JSON
- Compressed NPZ snapshots at configurable turn intervals

Excluded for now:

- Radiation damping
- Quantum excitation
- Space charge
- Wakefields
- Real RF or magnetic field maps
- Full nonlinear coupled ring dynamics
- Detailed collimation physics

## Outputs

Each run writes:

- `turn_metrics.csv`: per-turn aggregate beam metrics
- `summary.json`: final summary, runtime, model limits, and final metrics
- `snapshots/*.npz`: compressed particle state and alive mask snapshots
- `figures/*.png`: optional plots if Matplotlib is installed

## Notes

This is a circular counterpart to the simple linear 6D simulator. It is intentionally simple and should be treated as a reduced model for software development, diagnostics, and early research writing, not as a validated storage-ring physics engine.
