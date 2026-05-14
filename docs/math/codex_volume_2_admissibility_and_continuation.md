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
- **Recursion Density and Ordering Law (LAW-007)**: Defines how distributed reconciliation density across $\{-(i)_\alpha\}$ generates ordered continuation without primitive time.
  $$D_R(U) := \frac{\# \text{ of admissible reconciliation events in region } U}{\mu_A(U)}$$
  $$R_\alpha \prec R_\beta \iff R_\alpha \text{ is admissibility-preconditioned for } R_\beta$$
- **Apparent Temporality**: Apparent time is a projection of ordered reconciliation density, not a primitive coordinate.
- **Array Topology and Accessibility Law (LAW-008)**: Defines interaction domains and reachability as orientation-array topology structures.
  $$\alpha \sim_A \beta \iff \beta \text{ is admissibly reachable from } \alpha \text{ under orientation array topology}$$
  $$CSI(\alpha) := \{ \beta : \alpha \sim_A \beta \text{ and } \Phi(\alpha, \beta) \text{ is finite} \}$$
  $$Reach(\alpha, \beta) \iff \text{admissibility compatibility} \land \text{finite flux} \land \text{non-collapsed } A_\alpha$$
- **Local Neighborhoods**: Neighborhoods are relational and defined by orientation relation $\omega_\alpha \rightarrow \omega_\beta$, not absolute spatial distance.
- **Apparent Temporality Projection Law (LAW-009)**: Formalizes apparent time as a derived projection of ordered reconciliation density.
  $$T_{app}(U) := Proj_{time}(O_U, D_R(U), \prec_U)$$
  - **No Primitive Time**: $T_{app}$ is a bookkeeping parameter, not a background coordinate.
  - **Density-Dependent Appearance**: High reconciliation density regions project to high update-density (fast apparent time); low density regions project to low update-density (slow apparent time).
- **Apparent Geometry Projection Law (LAW-010)**: Defines apparent geometry as a projection of stabilized reconciliation topology.
  $$Geom_{app}(U) := Proj_{geom}(G_U, D_R(U), Reach(U), Top_A(U))$$
  - **Non-Primitive Geometry**: Geometry is a derived appearance, not a primitive metric substrate.
  - **Topology-First**: Accessibility relations and admissibility topology determine geometric structure.
- **Stabilized Reconciliation Basin Law (LAW-011)**: Defines how persistent reconciliation structures stabilize into basin-like organizations.
  $$B_U := \{ \alpha \in U : R_\alpha \text{ recurs with bounded drift and finite transport flux} \}$$
  - **Non-Attractor Persistence**: Basins are stabilized recurrence organizations, not static attractors or fixed points.
  - **Bounded Drift**: Persistence requires $\sup_{\alpha \in B_U} drift_A(R_\alpha) < \eta_B$.
  - **Dynamic Stability**: Stability is maintained through active reconciliation recurrence rather than global equilibrium.
- **Law-Like Persistence Channel Law (LAW-012)**: Defines how repeated stabilized reconciliation basins reinforce persistent continuation channels.
  $$C_P := \{ \alpha \in \{-(i)_\alpha\} : \text{continuation repeatedly stabilizes along pathways } P \}$$
  - **Non-Primitive Law**: Law-like structure is an emergent stabilized continuation tendency, not a primitive governing substance.
  - **Preferential Propagation**: Future continuation preferentially propagates through reinforced channels, creating the appearance of "following a law."
  - **No Universal Necessity**: Channels are contingent on recursive reconciliation reinforcement and are not eternally fixed.
- **Channel Fracture and Transition Law (LAW-013)**: Defines how continuation channels evolve and destabilize.
  - **Fracture and Bifurcation**: Channels may split when multiple accessibility pathways stabilize.
  - **Merge and Redirection**: Channels may converge or redirect under admissibility-boundary pressure.
  - **Collapse**: Dissolution occurs when recursive reinforcement fails to maintain persistence.
  - **Topology-Conditioned Evolution**: Transitions are dynamic reconciliation events, not deterministic phase changes.
- **Channel Competition and Selection Law (LAW-014)**: Defines how multiple channels interact under finite resources.
  - **Finite Budget Constraint**: Channels draw from a shared budget of admissibility, transport flux, and reconciliation recurrence.
  - **Suppression and Co-Stabilization**: Reinforcement of one channel may suppress others or enable co-stabilization if compatible.
  - **Non-Unique Selection**: Selection is an emergent dynamic property, not a deterministic or globally optimal "winner-takes-all" rule.
- **Channel Memory and Reinforcement History Law (LAW-015)**: Defines how channels retain history without reifying memory or residue.
  - **Reinforcement History**: $H(C_P, n)$ is the record of recurrent reconciliation supporting a channel.
  - **Memory Projection**: $Mem_{app}(C_P)$ is the apparent memory projected from reinforcement history.
  - **Non-Primitive Trace**: Memory and residue are projections of reinforced continuation history, not independent substances.
  - **Asymmetric Retention**: History is subject to reconstruction asymmetry and active reconciliation recurrence.
- **Channel Reconstruction Asymmetry Law (LAW-016)**: Formalizes why present continuation-channel structure cannot generally reconstruct its full prior reinforcement history.
  - **Asymmetry Condition**: $\Xi(C_P)$ may yield multiple admissible prehistories or incomplete reconstruction under recursive continuation dynamics.
  - **Recursive Loss**: $Loss(C_P, n)$ accumulates when continuation events compress, merge, redirect, fracture, or suppress prior reinforcement structure.
  - **Non-Unique Prehistory**: Distinct reinforcement histories may project into observationally equivalent continuation-channel states.
  - **Reconstruction Asymmetry**: Irreversibility is treated as a limit on reconstruction ($\Xi$) rather than a primitive temporal arrow or entropy increase.
- **Continuation Compression and Equivalence Law (LAW-017)**: Formalizes how multiple distinct continuation histories compress into equivalent observable continuation structures.
  - **History Family**: $\mathcal{H}(C_P) := \{ H_i : H_i \text{ admissibly projects into observable channel state } C_P \}$
  - **Compression**: $Compress(H_i \rightarrow C_P)$ removes discriminating structure via reinforcement loss, topology transition, or admissibility filtering.
  - **Observational Equivalence**: $H_i \sim_{obs} H_j \iff \Xi(H_i)$ and $\Xi(H_j)$ produce observationally equivalent continuation structures.
  - **Bounded Equivalence**: Equivalence is local, projection-dependent, and constrained by finite reconstruction reachability.
- **Accessibility Horizon and Reachability Limit Law (LAW-018)**: Defines intrinsic reachability limits and accessibility horizons across the orientation array.
  - **Reachable Domain**: $D_A(\alpha)$ is the set of loci reachable under finite transport flux and defined admissibility.
  - **Accessibility Horizon**: $H_A(\alpha)$ is the limit beyond which continuation influence becomes inadmissible, too weak, or unreachable.
  - **Decay Condition**: Reachability decays with $W_{CSI}$ and reinforcement support.
  - **Non-Spacetime Horizon**: Horizons are topological and dynamic array-limits, not primitive physical lightcones.
- **Local Causality as Accessibility Order Law (LAW-019)**: Defines local causal structure as an emergent property of admissibility-conditioned accessibility ordering.
  - **Local Causality Candidate**: $Cause_A(\alpha, \beta)$ holds if $\beta \in D_A(\alpha)$, admissibility is preserved, and continuation ordering permits transport.
  - **Ordering Condition**: $\alpha \prec_A \beta$ is defined locally through recursive continuation density and admissibility-compatible propagation.
  - **Bounded Causality**: Causal accessibility is strictly bounded by finite transport flux, reinforcement stability, and admissibility thresholds.
  - **Non-Global Clause**: Local causality does not imply a global total ordering or universal causal closure.
  - **Non-Spacetime Clause**: Causal accessibility is a topology-conditioned continuation relation, not a primitive spacetime geometry.
- **Identity Persistence Under Mutation Law (LAW-020)**: Formalizes identity as an emergent operational continuity relation across channel mutation.
  - **Identity Relation Candidate**: $Id_A(C_P, C_P')$ holds if continuity metric, mutation drift, and reinforcement history overlap are within tolerance.
  - **Fork and Merge**: Identity may branch or merge based on partial continuity thresholds.
  - **Identity Collapse**: Occurs when drift, loss, or discontinuity exceeds tolerance.
  - **Non-Primitive Identity**: Identity is an operational persistence relation, not a primitive object substance.
- **Finite Admissibility Budget Law (LAW-021)**: Formalizes continuation as a budget-constrained process.
  - **Budget Condition**: Continuation is admissible only if its cost ($Cost_A$) remains within the local budget ($B_A$).
  - **Depletion and Recovery**: Budgets are consumed by transitions and recovered during stabilization.
  - **Saturation and Failure**: Exceeding the budget triggers pruning, delay, redirection, or collapse.
  - **No Energy Equivalence**: Admissibility budgets are operational constraints, not physical energy.
- **Perturbation and Error Dynamics Law (LAW-022)**: Defines how perturbations propagate and stabilization structures respond to disturbance.
  - **Propagation and Damping**: Perturbations propagate through accessibility links and may be dampened by stabilization basins.
  - **Amplification and Cascade**: Exceeding resilience limits triggers amplification and recursive destabilization cascades.
  - **Corruption**: Disturbances may corrupt history, reconstruction, and identity persistence.
  - **No Thermodynamic Equivalence**: Perturbation is modeled as topology turbulence, not thermodynamic entropy.
- **Reconstruction-Limited Observability Law (LAW-023)**: Formalizes local observability as bounded reconstruction over accessible continuation topology.
  - **Observable Subset**: Observation is limited to the subset of the array that remains accessible and reconstructible ($Obs_\alpha$).
  - **Fidelity and Ambiguity**: Observability decays with loss and corruption; indistinguishability creates ambiguity regions.
  - **Hidden Topology**: Process structures may exist beyond the reach of any local observation.
  - **Non-Observer Absolutism**: There is no universal or privileged observer standpoint.

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
