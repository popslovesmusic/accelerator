# Hamiltonian / Symplectic Simulation (v1)

This simulation models a Hamiltonian system (Nonlinear Pendulum) using a **Symplectic Integrator** (Leapfrog/Verlet) to study conservation-style dynamics, phase-space structure, and Liouville's theorem.

## Theoretical Basis

- **Hamiltonian Dynamics:** Evolution of states $(q, p)$ where the Hamiltonian $\mathcal{H}$ is conserved.
- **Symplectic Integration:** Numerical schemes that preserve the symplectic structure of phase space, ensuring no artificial energy drift.
- **Liouville's Theorem:** Area conservation in phase space.
- **Phase-Space Buckets:** Stable vs unstable regions (separatrix) in non-linear systems.

## Model Equations

### Hamiltonian (Nonlinear Pendulum)
$$\mathcal{H}(q, p) = \frac{p^2}{2m} - \kappa \cos(q)$$

### Symplectic Update (Leapfrog)
1. $p_{n+1/2} = p_n - \frac{\Delta t}{2} \nabla V(q_n)$
2. $q_{n+1} = q_n + \Delta t \frac{p_{n+1/2}}{m}$
3. $p_{n+1} = p_{n+1/2} - \frac{\Delta t}{2} \nabla V(q_{n+1})$

## Usage

```powershell
python sim.py --config configs/default.json --out outputs/symplectic_run_01
```

## Outputs

- `metrics.csv`: Time-series of mean energy $\mathcal{H}$ and ensemble spread.
- `summary.json`: Final energy statistics and orbit characterization.
- `plots/`: Phase-space traces $(q, p)$ and energy conservation plots.
