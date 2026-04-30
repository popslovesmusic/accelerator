# Research-Quality Linear Particle Accelerator Simulation Plan

## Goal

Build a scientifically credible linear particle accelerator simulation suitable for research writing, technical reporting, and reproducible computational experiments. The simulator should model charged-particle motion through drift regions, RF accelerating gaps, and optional focusing elements while recording phase, position, momentum, kinetic energy, emittance, and beam loss diagnostics.

The first version should emphasize correctness, transparent assumptions, reproducibility, and validation against known analytic or benchmark cases. Visualization should support analysis rather than serve as the main purpose of the project.

## Research Objectives

The simulation should be designed to answer questions such as:

- How does RF phase affect longitudinal acceleration and energy spread?
- How do drift length, RF frequency, and gap voltage influence bunch stability?
- What fraction of particles remain phase-synchronous through a sequence of accelerating gaps?
- How does initial beam spread affect final energy distribution and transmission efficiency?
- How do simplified focusing elements affect transverse beam envelope and losses?

The simulator should produce quantitative outputs that can be used directly in figures, tables, and methods sections.

## Core Simulation Scope

### 1. Particle Model

Each particle should track:

- Position along the accelerator axis, `x`
- Velocity, `v`
- Time, `t`
- Charge, `q`
- Mass, `m`
- Kinetic energy
- Relativistic momentum, `p`
- RF phase at each accelerating gap
- Active or lost status

The first version should use 1D longitudinal motion along the accelerator axis. Later versions can extend this to transverse phase space, including `x`, `x'`, `y`, and `y'`.

### 2. Accelerator Components

The accelerator can be represented as a sequence of components:

- Drift tubes: regions with no acceleration.
- RF gaps: regions where particles gain energy from an oscillating electric field.
- Focusing lenses: simplified forces that keep particles near the beam axis.
- Detector or end screen: records final energy, arrival time, and beam spread.

### 3. Physics Update and Numerical Method

The non-relativistic first-pass update is:

```text
F = qE
a = F / m
v += a * dt
x += v * dt
```

For a research-quality implementation, relativistic dynamics should be treated as the default once particle speeds become a meaningful fraction of the speed of light:

```text
E_total = gamma * m * c^2
p = gamma * m * v
gamma = 1 / sqrt(1 - v^2 / c^2)
K = (gamma - 1) * m * c^2
```

The integrator should be documented and tested. A simple explicit method is acceptable for an early prototype, but the research version should support at least one higher-quality integrator, such as velocity Verlet, Boris-style field integration where applicable, or adaptive Runge-Kutta for longitudinal studies.

All equations, units, constants, and approximations should be stated in the report.

### 4. RF Acceleration

The electric field in each RF gap can initially be modeled as:

```text
E(t) = E0 * sin(omega * t + phase)
```

Particles gain energy only when inside an accelerating gap. This allows the simulation to demonstrate phase stability: particles arriving at the wrong phase gain less energy or may even decelerate.

The RF model should record each particle's arrival phase at every gap. This allows direct analysis of phase slip, synchronous phase behavior, and longitudinal bunch stability.

### 5. Beam Simulation and Statistical Outputs

The simulation should eventually support many particles instead of just one. The beam can include randomized initial conditions:

- Initial position spread
- Initial velocity spread
- Initial phase spread

Track these beam-level outputs:

- Average energy
- Energy distribution
- Beam bunching
- Particle losses
- Transmission efficiency
- RMS bunch length
- RMS energy spread
- Longitudinal phase-space distribution
- Optional transverse emittance in later versions

Each run should save its input parameters, random seed, simulation results, and summary statistics so the run can be reproduced exactly.

## Scientific Quality Requirements

The project should include:

- Explicit physical assumptions and limitations.
- SI-unit consistency throughout the code.
- Named physical constants from a single source module.
- Reproducible random initialization using fixed seeds.
- Convergence testing with respect to time step size.
- Validation against analytic cases.
- Structured output files, such as CSV, JSON, or HDF5.
- Plot generation scripts for publication-quality figures.
- A methods section that describes the numerical model clearly enough to reproduce it.

Recommended validation cases:

- Particle in a zero-field drift region conserves kinetic energy.
- Particle in a constant electric field matches analytic acceleration in the non-relativistic limit.
- Relativistic update prevents velocity from exceeding `c`.
- Single-gap energy gain matches the expected phase-dependent approximation.
- Smaller time steps converge toward a stable final energy and phase distribution.

## Recommended Build Phases

### Phase 1: Minimal 1D Longitudinal Linac

- Simulate one particle and then a small beam.
- Add a sequence of drift tubes and RF gaps.
- Use time-step integration.
- Plot position and energy over time.
- Output final energy.
- Validate against drift and constant-field analytic cases.

### Phase 2: Multi-Particle Beam

- Add many particles.
- Randomize initial conditions.
- Track bunch compression and spread.
- Show a final energy histogram.

### Phase 3: Scientific Visualization

Add analysis-oriented plots:

- Mean kinetic energy versus accelerator position.
- Energy spread versus accelerator position.
- RF phase at each gap.
- Final energy histogram.
- Longitudinal phase-space plot.
- Transmission efficiency versus RF phase or field amplitude.

Optional 2D animation may show:

- Accelerator tube
- Moving particles
- Particle color based on energy
- RF gaps changing color with field phase

Add user controls:

- RF frequency
- RF field strength or voltage
- Number of particles
- Particle type, such as electron or proton
- Simulation speed
- Reset, run, and pause

### Phase 4: Better Physics

Add higher-fidelity physics:

- Relativistic momentum
- Magnetic or electrostatic focusing
- Space charge approximation for beam self-repulsion
- Particle loss if particles drift outside aperture
- Configurable accelerator lattice

## Recommended Tech Stack for Research Use

Since the current workspace is empty, the best initial choice depends on the desired user experience.

Recommended options:

- Python, NumPy, SciPy, and Matplotlib: best for a physics-first simulator with reproducible plots.
- Pandas or HDF5: useful for structured data export and analysis.
- Jupyter notebooks: useful for exploratory analysis and research writing, but the core simulator should remain in normal Python modules.
- C++ or Rust: useful later if high-performance beam simulation becomes necessary.

The recommended starting point is a Python physics core with a command-line runner, structured outputs, automated validation tests, and Matplotlib-based figure generation.

## First Implementation Target

The first milestone should be:

```text
Run a 1D relativistic proton linac simulation with 20 RF gaps and 500 particles.
Display:
- particle positions over time
- final energy histogram
- average beam energy vs time
- particles lost or out of phase
- RF phase distribution at each gap
- convergence results for at least two time-step sizes
```

## Design Sketch

```text
Simulation
  Accelerator
    components: Drift, RFGAP, Lens, Detector

  ParticleBeam
    particles: Particle[]

  Integrator
    step(dt)
    compute_fields(x, t)
    update_particles()

  Output
    history arrays
    plots/animation
    structured data files
    run metadata
    validation reports
```

## Research Writing Deliverables

The project should produce:

- A formal technical report.
- A methods section describing equations, numerical integration, assumptions, and parameter choices.
- A validation section comparing the simulator to analytic expectations.
- A results section with figures and quantitative diagnostics.
- A limitations section describing where the model is simplified.
- A reproducibility appendix listing code version, parameters, seed values, and output files.

## Key Implementation Direction

The project should be scientific and research-oriented rather than game-like. The simulation should prioritize defensible physics, reproducible computation, reliable diagnostics, and high-quality figures suitable for research writing.

## Implemented Prototype

The initial research prototype has been implemented as a Python package in `linac_sim/`.

Implemented capabilities:

- Longitudinal relativistic particle tracking.
- Two transverse phase-space planes, `y/y'` and `z/z'`.
- Alternating drift, focusing-lens, and RF-gap accelerator lattice.
- Linear paraxial focusing model.
- Aperture-based particle loss.
- Reproducible multi-particle beam initialization with fixed random seed.
- Proton and electron species definitions.
- RF phase recording at each gap crossing.
- Beam summary diagnostics over time.
- RMS beam size, RMS divergence, geometric emittance, and normalized emittance diagnostics for both transverse planes.
- RMS radial beam size and transverse cross-section figures.
- Final particle-level output table.
- Structured JSON and CSV output files.
- Optional Matplotlib figure generation.
- Built-in validation command.

Default simulation:

```text
Species: proton
Particle count: 500
Initial kinetic energy: 1 MeV
RF gaps: 20
Peak RF field: 2 MV/m
RF frequency: 200 MHz
Initial transverse size: 1 mm RMS
Initial transverse divergence: 1 mrad RMS
Initial z transverse size: 1 mm RMS
Initial z transverse divergence: 1 mrad RMS
Aperture radius: 10 mm
Y focusing strength: 25 1/m^2
Z focusing strength: 25 1/m^2
Time step: 2 ps
Maximum simulation time: 100 ns
```

Run command:

```text
python -m linac_sim run
```

Validation command:

```text
python -m linac_sim validate
```

Default output directory:

```text
outputs/default_run
```

Generated output files:

- `metadata.json`
- `history.csv`
- `particles_final.csv`
- `gap_phases.csv`
- `figures/mean_energy.png`
- `figures/energy_spread.png`
- `figures/final_energy_histogram.png`
- `figures/normalized_emittance.png`
- `figures/beam_size.png`
- `figures/transverse_phase_space.png`
- `figures/z_transverse_phase_space.png`
- `figures/transverse_cross_section.png`

Latest verification result:

```text
Validation checks: all passed
Particles tracked: 500
RF gap crossings recorded: 10,000
Transmission fraction: 1.0
Mean final kinetic energy: 978,221 eV
RMS final energy spread: 7,477 eV
Y normalized RMS emittance: 4.215e-08 m rad
Z normalized RMS emittance: 4.184e-08 m rad
Y RMS beam size: 6.006e-04 m
Z RMS beam size: 6.230e-04 m
RMS radial beam size: 8.661e-04 m
```

The prototype has also been extended with explicit validation checks for aperture loss and RMS emittance calculation.

## Simple 6D Optiplex Simulator Deliverable

A separate CPU-first 6D reduced simulator has been implemented in `accelerator_sim_v1/` from the task specification `simple_6d_accelerator_sim_optiplex.json`.

Implemented files:

- `accelerator_sim_v1/sim.py`
- `accelerator_sim_v1/configs/optiplex_default.json`
- `accelerator_sim_v1/configs/optiplex_stretch.json`
- `accelerator_sim_v1/README.md`

The simulator uses the state vector:

```text
x, px, y, py, z, delta
```

Implemented element types:

- Drift
- Quadrupole
- RF cavity
- Circular aperture

Default run command:

```text
cd accelerator_sim_v1
python sim.py --config configs/optiplex_default.json --out outputs/run_default
```

Default run verification:

```text
Particles: 10,000
Steps: 1,000
Final alive count: 9,853
Lost count: 147
Survival fraction: 0.9853
Snapshots written: 11
Metrics rows: 1,001
Repeatability: repeated metrics.csv matched exactly with the same seed
Alive count never increases: true
Survival fraction range: 0.9853 to 1.0
```

Generated outputs:

- `outputs/run_default/metrics.csv`
- `outputs/run_default/summary.json`
- `outputs/run_default/snapshots/*.npz`
- `outputs/run_default/figures/*.png`

## Simple Circular 6D Simulator Deliverable

A circular accelerator counterpart has been implemented in `circular_accelerator_sim_v1/`.

Implemented files:

- `circular_accelerator_sim_v1/ring_sim.py`
- `circular_accelerator_sim_v1/configs/optiplex_ring_default.json`
- `circular_accelerator_sim_v1/configs/optiplex_ring_stretch.json`
- `circular_accelerator_sim_v1/README.md`

The simulator uses the same state vector:

```text
x, px, y, py, z, delta
```

Circular-specific behavior:

- Repeated ring lattice tracked turn by turn.
- Longitudinal coordinate `z` is wrapped into one circumference after each turn.
- Linear momentum-compaction slip is applied once per turn.
- RF cavity uses sinusoidal phase based on `z / circumference`.
- Circular aperture loss is applied in transverse `x/y`.

Default run command:

```text
cd circular_accelerator_sim_v1
python ring_sim.py --config configs/optiplex_ring_default.json --out outputs/ring_default
```

Default ring verification:

```text
Particles: 10,000
Turns: 500
Final alive count: 9,905
Lost count: 95
Survival fraction: 0.9905
Snapshots written: 11
Metrics rows: 501
Repeatability: repeated turn_metrics.csv matched exactly with the same seed
Alive count never increases: true
Survival fraction range: 0.9905 to 1.0
Runtime on default run: about 3.2 seconds
```

Generated circular outputs:

- `outputs/ring_default/turn_metrics.csv`
- `outputs/ring_default/summary.json`
- `outputs/ring_default/snapshots/*.npz`
- `outputs/ring_default/figures/*.png`
