# Poisson Sign Convention Audit (AUDIT-005)

This document records the mathematical and implementation-level sign conventions for the Poisson solver used in the accelerator simulation engine as of May 13, 2026.

## 1. Mathematical Convention

The Poisson equation for the electrostatic potential $\phi$ and charge density $\rho$ is generally expressed as:
$$\nabla^2 \phi = -\frac{\rho}{\epsilon_0}$$

In the current implementation, we assume $\epsilon_0 = 1$ for simplicity in the solver layer, though downstream force scaling may introduce effective coefficients.

## 2. Implementation Audit

### 2.1 Solver Implementation (`tools/accelerator_sim_v1_cpp/PoissonSolver.cpp`)
- **Method:** FFT-based solution in 2D.
- **Kernel:** $K(\mathbf{k}) = \frac{1}{k_x^2 + k_y^2}$.
- **FFT Relation:** $FFT(\nabla^2 \phi) = -(k_x^2 + k_y^2) \Phi(\mathbf{k})$.
- **Effective Equation:** The solver effectively computes $\Phi(\mathbf{k}) = \frac{R(\mathbf{k})}{k^2}$, which corresponds to:
  $$-(k_x^2 + k_y^2) \Phi(\mathbf{k}) = -R(\mathbf{k})$$
  $$\nabla^2 \phi = -\rho$$
- **Commentary:** The header file `PoissonSolver.h` explicitly states `Solve ∇²φ = -ρ/ε₀`, which is consistent with the code.

### 2.2 Downstream Usage (`tools/accelerator_sim_v1_cpp/LatticeElements.h`)
- **Charge Accumulation:** `rho` is accumulated by adding `1.0` per particle in the grid cell. Thus, $\rho \geq 0$.
- **Potential Calculation:** `solver_->solve(rho_grid_.data(), phi_grid_.data())`.
- **Field Calculation:** $\mathbf{E} = -\nabla \phi$.
  - `ex = -(phi(ix+1) - phi(ix-1)) / (2*dx)`
  - `ey = -(phi(iy+1) - phi(iy-1)) / (2*dy)`
- **Momentum Update:** $\Delta \mathbf{p} = \mathbf{E} \times 10^{-6}$.
- **Physical Interpretation:** For a positive charge density ($\rho > 0$), the resulting potential $\phi$ is generally positive, and the electric field $\mathbf{E} = -\nabla \phi$ points away from the density concentration. This results in a **repulsive force**, which is the expected physical behavior for space charge in a bunch of like-charged particles.

## 3. Findings & Risks

- **Convention Consistency:** The implementation of $\nabla^2 \phi = -\rho$ combined with $\mathbf{E} = -\nabla \phi$ is internally consistent and physically correct for repulsive dynamics.
- **Ambiguity Risk:** If a future patch attempts to "correct" the solver to $\nabla^2 \phi = \rho$ without updating the force calculation, the space charge effect would become **attractive**, leading to unphysical bunch collapse.
- **Normalization:** The solver includes a $1/(N_x N_y)$ normalization factor after the backward FFT to account for FFTW's unnormalized transform. This is correct.

## 4. Status
- **Sign Convention:** Verified as $\nabla^2 \phi = -\rho$.
- **Downstream Alignment:** Verified as $\mathbf{E} = -\nabla \phi$ (repulsive).
- **Modification Block:** No change to the Poisson sign is authorized without a simultaneous audit of force-scaling and directionality in all downstream `apply` methods.
