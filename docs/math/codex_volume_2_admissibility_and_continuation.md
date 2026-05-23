# Codex Volume 2: Admissibility and Continuation

*Note: All operators and topological bounds detailed in this volume are [stabilized process projections derived from the canonical core expression](derived_structure_doctrine.md) **(ℰ≠0) ⇔_x δ(ℰ>0)**, not independent primitives.*

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
- **Apparent Temporality\_app**: Apparent time (**time\_app**) is a projection of ordered reconciliation density, not a primitive coordinate.
- **Array Topology and Accessibility Law (LAW-008)**: Defines interaction domains and reachability as orientation-array topology structures.
  $$\alpha \sim_A \beta \iff \beta \text{ is admissibly reachable from } \alpha \text{ under orientation array topology}$$
  $$CSI(\alpha) := \{ \beta : \alpha \sim_A \beta \text{ and } \Phi(\alpha, \beta) \text{ is finite} \}$$
  $$Reach(\alpha, \beta) \iff \text{admissibility compatibility} \land \text{finite flux} \land \text{non-collapsed } A_\alpha$$
- **Local Neighborhoods**: Neighborhoods are relational and defined by orientation relation $\omega_\alpha \rightarrow \omega_\beta$, not absolute spatial distance (**distance\_obs**).
- **Apparent Temporality Projection Law (LAW-009)**: Formalizes apparent time (**time\_app**) as a derived projection of ordered reconciliation density.
  $$time\_app(U) \approx Proj_{time}(O_U, D_R(U), \prec_U)$$
  - **No Primitive Time**: **time\_app** is a bookkeeping parameter, not a background coordinate.
  - **Density-Dependent Appearance**: High reconciliation density regions project to high update-density (fast apparent **time\_app**); low density regions project to low update-density (slow apparent **time\_app**).
- **Apparent Geometry Projection Law (LAW-010)**: Defines apparent geometry (**geometry\_app**) as a projection of stabilized reconciliation topology, co-conditioned by accessibility.
  $$geometry\_app(U) \approx Proj_{geom}(G_U, D_R(U), Reach(U), Top_A(U))$$
  - **Non-Primitive Geometry**: Geometry (**geometry\_proj**) is a derived appearance, not a primitive metric substrate.
  - **Topology-Geometry Biconditional**: Geometry (**geometry\_proj**) is the operational accessibility of topology; topology (**topology\_proc**) is the stabilized memory of geometric continuation. They recursively co-condition each other (**topology\_proc ⇔_x geometry\_proj**).

### 3.1 Topology–Geometry Biconditional Coupling
The framework rejects a one-way derivation where topology linearly determines geometry. Instead, topology (**topology\_proc**) and geometry (**geometry\_proj**) are recursively co-conditioned under the admissibility grammar **x**.
- **Principle**: "No structure ⇒ No geometry\_proj."
- **Recursive Co-conditioning**: Topology constrains the active geometry\_app (accessibility) of a basin, while geometry\_app in turn constrains the domain where future topological ratchet events may occur.
- **Ratchet Discreteness**: (ℰ≠0) enforces conservation of asymmetry through the chain: 
  $$(ℰ≠0) \rightarrow \text{ratchet event} \rightarrow \text{residue } R \rightarrow \text{topology\_proc} \Leftrightarrow_x \text{geometry\_proj} \rightarrow \delta(ℰ>0)$$
  Ratchet events convert collapse-pressure into discrete stabilized residue, preventing terminal symmetry collapse.
- **Stabilized Reconciliation Basin Law (LAW-011)**: Defines how persistent reconciliation structures stabilize into basin-like organizations.
  $$B_U := \{ \alpha \in U : R_\alpha \text{ recurs with bounded drift and finite transport flux} \}$$
  - **Non-Attractor Persistence**: Basins are stabilized recurrence organizations, not static attractors or fixed points.
  - **Bounded Drift**: Persistence requires $\sup_{\alpha \in B_U} drift_A(R_\alpha) < \eta_B$.
  - **Dynamic Stability**: Stability is maintained through active reconciliation recurrence rather than global equilibrium.
- **Law-Like Persistence Channel Law (LAW-012)**: Defines how repeated stabilized reconciliation basins reinforce persistent continuation channels.
  $$C_P := \{ \alpha \in \{-(i)_\alpha\} : \text{continuation repeatedly stabilizes along pathways } P \}$$
  - **Non-Primitive Law**: Law-like structure is an emergent stabilized continuation tendency, not a primitive governing substance.
  - **Preferential Propagation**: Future continuation preferentially propagates through reinforced channels, creating the appearance of "following a law\_app."
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
  - **Reinforcement History**: $history\_proc(C_P, n)$ is the record of recurrent reconciliation supporting a channel.
  - **Memory Projection**: $memory\_app(C_P) \approx Proj_{mem}(history\_proc)$ is the apparent memory projected from reinforcement history.
  - **Non-Primitive Trace**: Memory and residue are projections of reinforced continuation history, not independent substances.
  - **Asymmetric Retention**: History is subject to reconstruction asymmetry and active reconciliation recurrence.
- **Channel Reconstruction Asymmetry Law (LAW-016)**: Formalizes why present continuation-channel structure cannot generally reconstruct its full prior reinforcement history.
  - **Asymmetry Condition**: $\Xi(C_P)$ may yield multiple admissible prehistories or incomplete reconstruction under recursive continuation dynamics.
  - **Recursive Loss**: $loss\_proc(C_P, n)$ accumulates when continuation events compress, merge, redirect, fracture, or suppress prior reinforcement structure.
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
  - **Non-Spacetime Horizon**: Horizons are topological and dynamic array-limits, not primitive physical lightcones\_analog.
- **Local Causality as Accessibility Order Law (LAW-019)**: Defines local causal structure (**causality\_app**) as an emergent property of admissibility-conditioned accessibility ordering.
  - **Local Causality Candidate**: $causality\_app(\alpha, \beta)$ holds if $\beta \in D_A(\alpha)$, admissibility is preserved, and continuation ordering permits transport.
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
- **Competitive Basin Ecology Law (LAW-024)**: Defines interaction dynamics among stabilization basins under finite continuation resources.
  - **Basin Overlap**: Interaction occurs when accessibility, channels, or budgets are shared.
  - **Competition and Starvation**: Basins compete for finite resources; depletion leads to starvation.
  - **Cannibalization**: One basin may stabilize by redirecting resources from another.
  - **Co-Stabilization**: Compatible basins may mutually reinforce stability.
  - **Collapse Propagation**: Failure of one basin may destabilize neighbors through shared constraints.
  - **Non-Biological Clause**: Basin ecology is a structural analogy, not a biological claim.
- **Persistence Decay and Forgetting Law (LAW-025)**: Defines the weakening, erosion, and eventual loss of reinforced continuation structures.
  - **Reinforcement Erosion**: Channels weaken when active reinforcement fails to offset intrinsic loss or budget depletion.
  - **Forgetting**: Prior history becomes inaccessible when reinforcement history falls below reconstruction thresholds.
  - **Basin Weakening**: Admissibility margin and accessibility coherence decline without active support.
  - **Transient Law-Like Persistence**: Channels are metastable and regime-dependent, not eternal.
  - **Non-Primitive Memory**: Forgetting is structural loss, not erasure of a memory substance.
- **Metastability and Temporary Law-Like Regime Law (LAW-026)**: Defines temporary law-like regimes as metastable continuation organizations.
  - **Metastable Regimes**: Coherent clusters of channels valid within bounded windows.
  - **Validity Windows**: Finite spans in the orientation array and continuation depth.
  - **Lifespan**: Depends on reinforcement renewal, decay, and perturbation load.
  - **Regime Transitions**: Structural reorganization between distinct metastable states.
  - **Temporary Law Clause**: Regimes are locally valid properties, not eternal governing rules.
- **Admissibility Phase Transition Law (LAW-027)**: Defines abrupt topology reorganization under admissibility-threshold crossing.
  - **Transition Pressure**: Instability load from boundary pressure, budget, and decay.
  - **Tipping Thresholds**: Limits beyond which regimes can no longer satisfy admissibility.
  - **Phase Transitions**: Sudden abrupt reorganization of continuation topology.
  - **Avalanches**: Cascading instability through shared resource or accessibility links.
  - **Regime Shifts**: Transitions between distinct metastable law-like organizations.
  - **No Physics Clause**: Phase transitions are topological reorganization events, not physical matter shifts.
- **Topological Invariants Under Continuation Law (LAW-028)**: Defines candidate invariants preserved across recursive continuation transformations.
  - **Invariant Families**: Relational properties preserved under admissibility-compatible transformations.
  - **Persistence and Accessibility Invariants**: Stability of basins and reachability-equivalence classes.
  - **Reinforcement and Reconstruction Invariants**: Preservation of history-overlap and observational equivalence.
  - **Bounded Invariance**: Preservation is valid only within declared tolerances.
  - **No Global Conservation Clause**: Invariants are local and conditional; no universal conservation is claimed.
- **Recursive Arbitration and Conflict Resolution Law (LAW-029)**: Defines local arbitration behavior among competing continuation possibilities.
  - **Arbitration Operator**: Resolves conflicts by selecting, deferring, splitting, merging, pruning, or collapsing candidates.
  - **Conflict Condition**: Triggered when simultaneous persistence exceeds local admissibility budgets or destabilizes invariants.
  - **Priority Scoring**: Operational measure based on admissibility margin, reinforcement, and perturbation resilience.
  - **Tie-Resolution**: Allows for multi-branch continuation, deferred selection, or persistent ambiguity.
  - **Recursive Feedback**: Arbitration outcomes reorganization local topology and influence future budgets.
  - **Non-Unique Clause**: Arbitration is not assumed unique, deterministic, or globally optimal.
- **Multi-Scale Coherence Transfer Law (LAW-030)**: Defines how locally stabilized structures coordinate across scale-like organization layers.
  - **Scale-Like Layers**: Emergent organization strata induced by coherent reconciliation structure.
  - **Coherence Transfer**: Alignment between local, regional, and higher-order continuation layers.
  - **Upward Transfer**: Local coherence reinforcing higher-order stabilization structures.
  - **Downward Constraint**: Higher-order coherence narrowing local admissible continuation options.
  - **Scale Decoupling**: Incompatibility between layers blocking effective coherence transfer.
  - **Non-Primitive Scale Clause**: Organization strata are emergent, not primitive background coordinates.
- **Discrete-Continuous Transition Mechanics Law (LAW-031)**: Defines how continuous gradients produce discrete continuation outcomes.
  - **Continuous Gradients**: Gradual variation in admissibility, reinforcement, or budget.
  - **Operational Thresholds**: Limits mediating the transition from continuous to discrete structure.
  - **Discrete Events**: Abrupt stabilization outcomes such as pruning, bifurcation, or regime shifts.
  - **Stabilization Quantization**: Emergent partitioning of process outcomes across threshold boundaries.
  - **Continuity Preservation**: Gradient structure persists underlying the discrete appearance.
  - **Non-Physical Clause**: Discreteness is an operational outcome, not a physical quantization claim.
- **Recursive Failure Mode Taxonomy Law (LAW-032)**: Defines a unified taxonomy of failure states in recursive continuation.
  - **Failure Families**: Runaway, deadlock, fragmentation, reinforcement lock, admissibility collapse, budget exhaustion, perturbation cascade, and reconstruction failure.
  - **Structural Failure**: Failure is a governed transition into an unstable or non-reconstructible state, not a simple "end."
  - **Cascades**: Local failures propagate regional instability through shared dependencies.
  - **Non-Suppression Clause**: Failures must be explicitly recorded and preserved as structural outcomes.
  - **Constraint Dependency**: Failures emerge from the violation of admissibility, budget, or reconstruction limits.
- **Hidden Topology and Inaccessible Continuation Domains Law (LAW-033)**: Defines stable continuation structures existing outside local reconstruction reach.
  - **Hidden Domains**: Loci that are topologically unreachable or reconstructively opaque.
  - **Inaccessibility Conditions**: Arise from finite-flux decay, horizons, fragmentation, or compression loss.
  - **Partial Traces**: Hidden structures influence accessible domains through indirect residues and distortions.
  - **Non-Absolute Hiddenness**: Hiddenness is a local relational property, not an absolute metaphysical state.
  - **Non-Observer Completion**: No domain or process is capable of complete global topology recovery.
- **Continuation Grammar and Compositional Structure Law (LAW-034)**: Defines rules governing the combination and simplification of continuation-law objects.
  - **Bounded Grammar**: Composition is restricted to admissibility-preserving and budget-aware operations.
  - **Symbol Set**: Irreducible and emergent objects from which higher-order constructions are built.
  - **Composition Rules**: Rules for combining operators, channels, and basins under reconstruction limits.
  - **Invalid Composition**: Operations that hide failure modes or force artificial uniqueness are blocked.
  - **Reduction Rules**: Admissibility-preserving simplification of complex process expressions.
  - **Grammar Scope Clause**: The grammar is local and provisional, not a universal formal logic.

## 4. delta (Continuation/Deviation Operator)
The mechanism that generates or exposes candidate continuation under nonzero distinguishability.
- **Explicit Functional Form Candidate (LAW-001)**:
  $$\delta(E_\alpha > 0) := \{ x'_\alpha \in A_\alpha : x'_\alpha = x_\alpha + \Pi_{A_\alpha}(\sum_{\beta \in CSI(\alpha)} NavT(\omega_\alpha, \omega_\beta)), \text{ and } E_\alpha > \epsilon_{null} \}$$
- **Role Correction**: $\delta$ is the continuation/deviation event operator. It identifies valid transitions within the admissible domain.
- **Joint Selection**: Selection of the specific next state is produced jointly by $\delta$ operating inside the deformation regime specified by the operator family **⇔_x**.
- **Mismatch Minimization**: The governing principle driving the evolution of $\delta$.
- **Non-Empty Image**: Existence condition formalized in MT-003.

## 5. Selection Rules
Specific rules (SR-001, etc.) that resolve multi-valued delta outputs in degenerate minima scenarios, further constrained by the active deformation regime **x**.

---
[Back to Master Index](codex_master_index.md)
