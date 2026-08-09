# Structural Box Euler Stability Policy (AUDIT-006)

This document records the stability constraints, known risks, and diagnostic requirements for the explicit Euler integrator used in `structural_box_sim_v2`.

## 1. Integrator Specification
The current simulation uses a first-order **explicit Euler** scheme for time integration:
$$u_{n+1} = u_n + \Delta t \cdot f(u_n, t_n)$$

## 2. Stability Constraints

### 2.1 Diffusion Stability (CFL Condition)
For the diffusion terms, numerical stability requires:
$$\Delta t \le \frac{\Delta x^2}{2 D_{max}}$$
where $D_{max} = \max(D_\epsilon, D_\rho, D_R)$. 
Exceeding this bound typically leads to high-frequency oscillation and numerical blow-up.

### 2.2 Reaction/Stiffness Stability
Explicit Euler is conditionally stable for non-linear reaction terms. Large values of coupling coefficients (e.g., $b, \beta, \kappa, \lambda_R, c, \gamma$) or large forcing terms ($s, h$) can make the system "stiff," requiring a much smaller $\Delta t$ than the diffusion limit.

## 3. Implementation Guardrails

### 3.1 Non-negativity Clamping
The simulation optionally applies `np.maximum(field, 0.0)` at each step. 
- **Role:** This is a physical constraint safeguard to prevent negative densities/concentrations.
- **Warning:** Clamping is **NOT** a numerical stability proof. It may mask underlying instabilities or oscillations by preventing them from crossing zero, while they may still grow unboundedly in the positive direction or introduce unphysical artifacts.

### 3.2 Stability Diagnostics
The simulation driver must include conservative checks to warn the user when a configuration enters a potentially fragile regime:
1. **Diffusion Check:** Warn if $\Delta t > 0.5 \cdot \frac{\Delta x^2}{2 D_{max}}$.
2. **Growth/Decay Check:** Warn if $\Delta t \cdot \max(\text{linear coefficients}) > 0.1$.

## 4. Governance Constraints
- **Full Stability Claims:** No `implementation_verified` or `C4+` claim may assert "full numerical stability" for the current explicit Euler implementation. 
- **Claim Humility:** All findings must acknowledge dependency on the chosen $\Delta t$ and discretization.
- **Future Integrators:** If stiff-regime research is required, a future patch should introduce an implicit (e.g., Crank-Nicolson) or semi-implicit integrator.

## 5. Regression Testing Requirements
Regression tests must verify:
1. Stable behavior under small $\Delta t$.
2. Diagnostic warnings under large $\Delta t$ or high-stiffness configurations.
3. Documentation of clamping limitations.
