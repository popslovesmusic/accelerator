# Codex Volume 2: Admissibility and Continuation

This volume maps the operational dynamics of admissibility and state transition.

## 1. Pi_A (Admissibility Projection)
The projection operator that maps candidate states into the admissible window A.
- **Explicit Functional Form Candidate (LAW-002)**:
  $$\Pi_{A_\alpha}(y_\alpha) := \{ z_\alpha \in A_\alpha : d_A(z_\alpha, y_\alpha) = \inf_{u \in A_\alpha} d_A(u, y_\alpha) \}$$
- **Idempotence**: A core target for MT-001 validation.
  $$\Pi_{A_\alpha}(\Pi_{A_\alpha}(y_\alpha)) = \Pi_{A_\alpha}(y_\alpha)$$
- **Boundary Transition Law (LAW-005)**: Behavior at $\partial A_\alpha$ under projected transport.
  $$\partial A_\alpha := \{ z : \text{admissibility\_margin}_A(z) = 0 \}$$
  Transitions include interior stability (margin > 0), splitting, pruning, or failure (margin $\rightarrow$ 0).

## 2. NavT (Residue Transport)
The operator responsible for the transport of residue and orientation across the process domain.
- **Explicit Functional Form Candidate (LAW-003)**:
  $$NavT(\omega_\alpha, \omega_\beta) := W_{CSI}(\alpha, \beta) \cdot K_{orient}(\omega_\alpha, \omega_\beta) \cdot \tau(\omega_\beta \rightarrow \omega_\alpha)$$
  $$T_\alpha := \sum_{\beta \in CSI(\alpha)} NavT(\omega_\alpha, \omega_\beta)$$
- **Finite Flux Law (LAW-004)**: Aggregate transport must remain bounded.
  $$\Phi_\alpha := \sum_{\beta \in CSI(\alpha)} ||NavT(\omega_\alpha, \omega_\beta)|| < \infty$$
- **Null-Path Identity**: Formalized in MT-002.
- **Non-Invertibility**: A critical constraint in non-local transport scenarios. Preservation of reconstruction loss is fundamental.

## 3. Orientation and Reconciliation
Orientation governs the "directionality" of continuation and transport.
- **Orientation Array Distinction Law (LAW-006)**: Formally separates local orientation operators from distributed orientation topology.
  $$-(i)_\alpha := \text{local orientation-conditioned continuation operator}$$
  $$\{-(i)_\alpha\} := \text{distributed reconciliation topology over local orientation operators}$$
- **Operational Roles**: $-(i)_\alpha$ governs local mechanics; $\{-(i)_\alpha\}$ governs distributed reconciliation, recursion density, and ordering emergence.
- **Anti-Collapse**: Maintaining the distinction prevents the introduction of forced global orientation frames.

## 4. delta (Selection Operator)
The mechanism that selects the next state from the admissible candidate set.
- **Explicit Functional Form Candidate (LAW-001)**:
  $$\delta(E_\alpha > 0) := \{ x'_\alpha \in A_\alpha : x'_\alpha = x_\alpha + \Pi_{A_\alpha}(\sum_{\beta \in CSI(\alpha)} NavT(\omega_\alpha, \omega_\beta)), \text{ and } E_\alpha > \epsilon_{null} \}$$
- **Mismatch Minimization**: The governing principle of delta.
- **Non-Empty Image**: Existence condition formalized in MT-003.

## 4. Selection Rules
Specific rules (SR-001, etc.) that resolve multi-valued delta outputs in degenerate minima scenarios.

---
[Back to Master Index](codex_master_index.md)
