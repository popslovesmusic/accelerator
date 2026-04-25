# Linear Particle Accelerator Simulation

Research-oriented Python prototype for a linear particle accelerator simulation with longitudinal tracking and two transverse phase-space planes.

The project emphasizes:

- SI-unit consistency
- Relativistic particle updates
- Reproducible seeded beam initialization
- Two-plane transverse phase-space and emittance diagnostics
- Linear focusing lenses and aperture loss
- Structured JSON/CSV outputs
- Validation against analytic or expected limiting cases
- Publication-oriented plots when Matplotlib is installed

## Tooling Ecosystem

- `linac_sim`: Standard linear particle accelerator model.
- `accelerator_sim_v1`: 6D accelerator simulation.
- `circular_accelerator_sim_v1`: Ring accelerator simulation.
- `agent_based_sim_v1`: Phase-space swarm simulation for testing local rules, CSI coupling, and event chains.
- `ca_admissibility_sim_v1`: 2D Cellular Automata for testing discrete admissibility, threshold propagation, and zero logic.
- `graph_dynamics_sim_v1`: Dynamic network simulation for testing topological causal accessibility, decoupling, and recoupling between domains.
- `stochastic_sim_v1`: Continuous SDE simulation for testing deviation floors, detection thresholds, and phase packet onset events.
- `kuramoto_sim_v1`: 1D ring Kuramoto oscillator network for testing phase-locking, synchronization, and shelf regimes.
- `rd_moving_boundary_sim_v1`: Reaction-Diffusion simulation with moving boundaries for testing dynamic topology, pockets, and corridor formation.
- `lb_fluid_sim_v1`: 2D Lattice Boltzmann simulation for testing potential flow, coupling channels, and topology-guided motion through erosion.
- `symplectic_sim_v1`: Hamiltonian phase-space simulation for testing conservation-style dynamics and symplectic integration.
- `fsa_rule_engine_sim_v1`: Abstract state machine simulation for testing formal admissibility logic, exclusion rules, and residue-gated continuations.
- `mc_ensemble_sim_v1`: Monte Carlo meta-orchestrator for running parallel parameter sweeps and mapping empirical regime boundaries.
- `structural_box_sim_v2`: Advanced Level 2 1D PDE simulation for testing identity persistence and Structural Relational Closure (SRC).
- `info_metrics_module_v1`: Standalone information tracking engine (Entropy, MI, Complexity) to measure structure vs. noise.
- `bifurcation_analyzer_v1`: Dynamic parameter continuation tool for mapping formal regime boundaries and hysteresis.
- `spectral_analysis_v1`: Spectral analysis layer (FFT) for detecting coherent modes and phase packets in spatial/temporal data.
- `parameter_optimizer_v1`: Inverse problem solver using gradient-free optimization (Nelder-Mead) to discover optimal regimes.
- `tda_module_v1`: Topological Data Analysis module for quantifying pockets, corridors, and fragmentation.
- `falsification_suite_v1`: Unit test / falsification harness for verifying theoretical limiting cases and preventing self-confirmation bias.

## Quick Start

Run the default proton linac simulation:

```powershell
python -m linac_sim run
```

The default run tracks 500 protons through a 20-gap lattice with a 1 MeV initial beam energy.

Run validation checks:

```powershell
python -m linac_sim validate
```

Generated files are written to `outputs/` by default.

## Current Model

The simulator tracks longitudinal motion plus two transverse planes. Particles travel along the accelerator axis through a sequence of drift regions, linear focusing lenses, and RF gaps. Each particle stores longitudinal position and momentum, `y/y'`, `z/z'`, kinetic energy, arrival phase diagnostics, and loss status.

The RF field is modeled as:

```text
E(t) = E0 sin(omega t + phase)
```

The relativistic momentum update is:

```text
p(t + dt) = p(t) + q E dt
v = p / (gamma m)
gamma = sqrt(1 + (p / mc)^2)
x(t + dt) = x(t) + v dt
```

This update preserves the speed limit `v < c` by construction.

The transverse focusing model uses a paraxial linear approximation:

```text
dp_y / ds = -k_y p_s y
dp_z / ds = -k_z p_s z
```

Particles are marked lost when their transverse radius exceeds the configured aperture radius.

## Outputs

Each run writes:

- `metadata.json`: model parameters, seed, component layout, and summary statistics
- `history.csv`: beam summary over time
- `particles_final.csv`: final particle-level state
- `gap_phases.csv`: RF phase diagnostics for particles crossing accelerating gaps
- `figures/*.png`: optional plots if Matplotlib is installed

Tracked transverse diagnostics include RMS beam size, RMS divergence, geometric RMS emittance, and normalized RMS emittance for both transverse planes, plus RMS radial beam size.

## Limitations

This is still a reduced research model. It includes two transverse planes, simplified linear focusing, and circular aperture loss, but does not yet include full 6D coupled dynamics, space charge, realistic RF cavity field maps, or detailed magnetic lattice modeling.
