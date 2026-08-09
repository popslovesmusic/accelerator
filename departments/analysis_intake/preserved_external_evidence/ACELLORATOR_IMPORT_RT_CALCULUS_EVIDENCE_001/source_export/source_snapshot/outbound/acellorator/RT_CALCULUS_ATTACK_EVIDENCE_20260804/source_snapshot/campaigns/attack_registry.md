# Falsification Attack Registry

This registry tracks the status and outcomes of all falsification attacks run against the RT Calculus framework.

## Summary of Attacks

| Attack ID | Target Concept | Target File | Script | Status | Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FAT-01-AXIOM-1.2.1** | Primary Axiom: The Statement | [01_foundations...md](../chapters/01_foundations_process_distinction_and_continuation.md) | [attack_01_axiom_1_2_1.py](attack_01_axiom_1_2_1.py) | **Completed** | **Survived** |
| **FAT-02-TRACE-PRIORITY-1.2.6** | Trace Priority Over Projection | [01_foundations...md](../chapters/01_foundations_process_distinction_and_continuation.md) | [attack_02_trace_priority_1_2_6.py](attack_02_trace_priority_1_2_6.py) | **Completed** | **Survived** |
| **FAT-03-UNIVERSAL-SCHEMA-1.3.2** | Universal Law Schema ($U_{\Omega}$) | [01_foundations...md](../chapters/01_foundations_process_distinction_and_continuation.md) | [attack_03_universal_schema_1_3_2.py](attack_03_universal_schema_1_3_2.py) | **Completed** | **Survived** |
| **FAT-04-REGIME-BOUNDARY-1.2.2b.6** | L/NL Regime Boundary and Transition | [01_foundations...md](../chapters/01_foundations_process_distinction_and_continuation.md) | [attack_04_regime_boundary_1_2_2b_6.py](attack_04_regime_boundary_1_2_2b_6.py) | **Completed** | **Survived** |
| **FAT-05-TRACE-ADMISSIBILITY-1.2D.1** | Trace-Admissibility & Recoupling | [01_foundations...md](../chapters/01_foundations_process_distinction_and_continuation.md) | [attack_05_trace_admissibility_1_2d_1.py](attack_05_trace_admissibility_1_2d_1.py) | **Completed** | **Survived** |
| **FAT-06-CONDITIONED-DISTINCTION-1.2.2F** | Conditioning Directionality & Primitiveness | [01_foundations...md](../chapters/01_foundations_process_distinction_and_continuation.md) | [attack_06_conditioned_distinction_1_2_2f.py](attack_06_conditioned_distinction_1_2_2f.py) | **Completed** | **Survived** |
| **FAT-07-CONTINUATION-COMPOSITION-2.3.2** | Continuation Composition & Guards | [02_residue...md](../chapters/02_residue_memory_and_recursive_closure.md) | [attack_07_continuation_composition_2_3_2.py](attack_07_continuation_composition_2_3_2.py) | **Completed** | **Survived** |
| **FAT-08-RATE-ELIGIBILITY-2.8.7** | Rate-Type Eligibility Predicate | [02_residue...md](../chapters/02_residue_memory_and_recursive_closure.md) | [attack_08_rate_eligibility_2_8_7.py](attack_08_rate_eligibility_2_8_7.py) | **Completed** | **Survived** |
| **FAT-09-RESIDUE-UPDATE-2.2.1** | Residue Update Operator & Inscription | [02_residue...md](../chapters/02_residue_memory_and_recursive_closure.md) | [attack_09_residue_update_2_2_1.py](attack_09_residue_update_2_2_1.py) | **Completed** | **Survived** |
| **FAT-10-DIRECTED-DISTINCTION-3.1.1** | Directed Distinction & Asymmetry | [03_distinction...md](../chapters/03_distinction_relations_and_directed_difference.md) | [attack_10_directed_distinction_3_1_1.py](attack_10_directed_distinction_3_1_1.py) | **Completed** | **Survived** |
| **FAT-11-FLOOR-CONSTRAINT-3.4.1** | Floor Constraint (Epsilon Floor) | [03_distinction...md](../chapters/03_distinction_relations_and_directed_difference.md) | [attack_11_floor_constraint_3_4_1.py](attack_11_floor_constraint_3_4_1.py) | **Completed** | **Survived** |
| **FAT-12-TRIADIC-CLOSURE-4.X.1** | Asymmetric Triadic Closure | [04_symmetry...md](../chapters/04_symmetry_and_asymmetry_domains.md) | [attack_12_triadic_closure_4_x_1.py](attack_12_triadic_closure_4_x_1.py) | **Completed** | **Survived** |
| **FAT-13-ORIENTATION-COHERENCE-5.1.5** | Orientation Coherence Metric Candidate | [05_orientation...md](../chapters/05_orientation_and_direction.md) | [attack_13_orientation_coherence_5_1_5.py](attack_13_orientation_coherence_5_1_5.py) | **Completed** | **Survived** |
| **FAT-11-FLOOR-CONSTRAINT-DS** | Floor Constraint (DS Attractor) | [03_distinction...md](../chapters/03_distinction_relations_and_directed_difference.md) | [attack_11_floor_constraint_ds.py](attack_11_floor_constraint_ds.py) | **Completed** | **Falsified** |
| **FAT-12-TRIADIC-CLOSURE-CT** | Asymmetric Triadic Closure (Identity Axiom) | [04_symmetry...md](../chapters/04_symmetry_and_asymmetry_domains.md) | [attack_12_triadic_closure_ct.py](attack_12_triadic_closure_ct.py) | **Completed** | **Falsified** |
| **FAT-13-ORIENTATION-COHERENCE-IT** | Orientation Coherence (Shannon Entropy) | [05_orientation...md](../chapters/05_orientation_and_direction.md) | [attack_13_orientation_coherence_it.py](attack_13_orientation_coherence_it.py) | **Completed** | **Falsified** |
| **FAT-14-RELATIONAL-CLUSTER-5.Z.1** | Relational Cluster (Topological Clique) | [05_orientation...md](../chapters/05_orientation_and_direction.md) | [attack_14_relational_cluster_5_z_1.py](attack_14_relational_cluster_5_z_1.py) | **Completed** | **Falsified** |
| **FAT-15-PROCESS-PRIORITY** | Process Priority (Ontological Dependency) | [01_foundations...md](../chapters/01_foundations_process_distinction_and_continuation.md) | [attack_15_process_priority.py](attack_15_process_priority.py) | **Completed** | **Falsified** |
| **FAT-16-OTM-CAPACITY-PRIMITIVE** | OTM Capacity Primitive (Relational Capacity) | [03_distinction...md](../chapters/03_distinction_relations_and_directed_difference.md) | [attack_16_otm_capacity_primitive.py](attack_16_otm_capacity_primitive.py) | **Completed** | **Projection Falsified** |
| **FAT-17-PRIMITIVE-SLOT** | Primitive OTM Slot (Relational Capacity Slot) | [03_distinction...md](../chapters/03_distinction_relations_and_directed_difference.md) | [attack_17_primitive_slot.py](attack_17_primitive_slot.py) | **Completed** | **Falsified** |
| **FAT-18-CAUSAL-CLOSURE** | Causal Closure (Admissibility Basins) | [11_topology...md](../chapters/11_topology_knots_braids_and_projection.md) | [attack_18_causal_closure.py](attack_18_causal_closure.py) | **Completed** | **Survived** |
| **FAT-19-DOMAIN-COUPLING** | Domain Coupling (Domain-Relative Activity) | [05_orientation...md](../chapters/05_orientation_and_direction.md) | [attack_19_domain_coupling.py](attack_19_domain_coupling.py) | **Completed** | **Survived** |
| **FAT-20-RELATIONAL-ORDERING** | Relational Ordering (Absolute Primitive) | [03_distinction...md](../chapters/03_distinction_relations_and_directed_difference.md) | [attack_20_relational_ordering.py](attack_20_relational_ordering.py) | **Completed** | **Projection Falsified** |
| **FAT-21-ADMISSIBILITY-COMPUTATION** | Admissibility Gated Computation | [03_distinction...md](../chapters/03_distinction_relations_and_directed_difference.md) | [attack_21_admissibility_computation.py](attack_21_admissibility_computation.py) | **Completed** | **Projection Falsified** |
| **FAT-22-ADMISSIBILITY-FIELD-CAUSAL-LIMIT** | Admissibility Field & Causal Limit | [03_distinction...md](../chapters/03_distinction_relations_and_directed_difference.md) | [attack_22_admissibility_field_causal_limit.py](attack_22_admissibility_field_causal_limit.py) | **Completed** | **Survived** |
| **FAT-23-REFERENCE-CENTERED-ORDERED-RELATION** | Reference Centered Ordered Relation | [03_distinction...md](../chapters/03_distinction_relations_and_directed_difference.md) | [attack_23_reference_centered_ordered_relation.py](attack_23_reference_centered_ordered_relation.py) | **Completed** | **Projection Falsified** |
| **FAT-24-TRIPLET-IDENTITY-EQUIVALENCE** | Triplet Identity Equivalence | [03_distinction...md](../chapters/03_distinction_relations_and_directed_difference.md) | [attack_24_triplet_identity_equivalence.py](attack_24_triplet_identity_equivalence.py) | **Completed** | **Projection Falsified** |

---

## Detailed Attack Logs

### FAT-01-AXIOM-1.2.1: Attack on Primary Axiom

- **Target Concept:** Axiom 1.2.1 (The Statement): $(\mathcal{E} \neq 0) \iff_R \delta_a(\mathcal{E} > 0)$
- **Attack Vector:** We test if we can construct a simulated continuation system where continuation transitions ($\Delta$) can occur or stabilize under a zero-distinction condition ($\mathcal{E} = 0$), or conversely, if admissibility evaluation ($\delta_a$) can produce valid continuation states when there is zero mismatch.
- **Python Script:** `campaigns/attack_01_axiom_1_2_1.py`
- **Verification Method:** Run a process simulation where we force the distinction array $\chi_D$ to collapse to a single state (meaning all difference is erased, $\mathcal{E}=0$) and attempt to transition the system to a new state or check if the update rules permit non-trivial progress.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that when distinction is forced to zero ($\mathcal{E} = 0$), the legality gate immediately triggers a transition to the Zero-State, causing continuation to cease. Spontaneous recovery or generation of new distinctions from the Zero-State was impossible without an external mismatch source. The primary axiom's necessity and sufficiency conditions hold under the simulation boundary.

### FAT-02-TRACE-PRIORITY-1.2.6: Attack on Trace Priority Over Projection

- **Target Concept:** Formal Principle 1.2.6: Trace Priority Over Projection: $P(H_1) = P(H_2) \not\implies H_1 = H_2$
- **Attack Vector:** We test if we can construct a system or a regime where the history (trace) of continuation events can be uniquely reconstructed from the final-state projection, which would mean that process identity is NOT trace-prior but is instead projection-determined.
- **Python Script:** `campaigns/attack_02_trace_priority_1_2_6.py`
- **Verification Method:** Simulate two distinct process histories $H_1 \neq H_2$, mapping them through a projection $P$. Test if there exists a projection mapping $P$ that is injective (meaning $P(H_1) = P(H_2) \implies H_1 = H_2$), and evaluate whether this falsifies the general principle.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that while a simplified, linear state-accumulator model is injective and permits full historical reconstruction, any realistic RT system with non-linear admissibility gating is non-injective. We successfully demonstrated a collision where two distinct process histories ($H_1 \neq H_2$) resulted in identical final observable states and residue mappings. Thus, process identity is trace-prior, and the principle survived.

### FAT-03-UNIVERSAL-SCHEMA-1.3.2: Attack on Universal Law Schema ($U_{\Omega}$)

- **Target Concept:** Formal Principle 1.3.2: Universal Rule $U_{\Omega}$ (The Master Process Chain)
- **Attack Vector:** We test the necessity of the admissibility filter $\delta_a$ and mismatch optimization in preserving the non-null difference condition $\mathcal{E} > 0$ and structural stability.
- **Python Script:** `campaigns/attack_03_universal_schema_1_3_2.py`
- **Verification Method:** Simulate three variants of the process loop over 10000 steps: (1) full $U_{\Omega}$ compliance, (2) randomized selection (ablating $\delta_a$), (3) ignoring mismatch optimization. Compare structural stability and check for collapse.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that the admissibility filter $\delta_a$ is strictly necessary for stable process persistence. In 10,000-step simulations across 50 seeds, 100% of the runs with an ablated filter diverged and collapsed, whereas 100% of the $U_{\Omega}$-compliant runs achieved stable persistence. Thus, the master schema survived.

### FAT-04-REGIME-BOUNDARY-1.2.2b.6: Attack on L/NL Regime Boundary and Transition

- **Target Concept:** Governed Clarification 1.2.2B.6: L/NL Regime Boundary and Transition: $RT_{operational\_regime} \to L \lor NL$
- **Attack Vector:** Attempt to construct a process that accumulates high residue feedback ($R_t \gg 0, k > 0$) but remains strictly linear and composable (low fitting error under a linear operator representation), trying to falsify the claim that residue feedback inevitably deforms local composition.
- **Python Script:** `campaigns/attack_04_regime_boundary_1_2_2b_6.py`
- **Verification Method:** Run a process simulation where we introduce high residue feedback ($k=0.5$). Fit a linear matrix operator to predict state updates and measure the fitting error (R2 score). If the linear fit remains highly accurate ($R^2 > 0.99$), the boundary transition logic is falsified.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that residue feedback successfully deforms state composition, introducing non-linearities that make linear operators inaccurate. With $k = 0.0$ (no feedback), a linear operator fit the transition updates perfectly ($R^2 = 1.0$), confirming the system is in the linear regime ($L$). However, with $k = 0.5$ (high feedback), the linear fit quality dropped to $R^2 = 0.8028$, failing the linearity threshold ($R^2 \ge 0.99$), confirming the transition to the nonlinear regime ($NL$) and verifying the survival of the concept.

### FAT-05-TRACE-ADMISSIBILITY-1.2D.1: Attack on Trace-Admissibility & Recoupling

- **Target Concept:** Formal Principle 1.2D.1: Trace-Admissibility (PRIN_001) & 1.2D.2: Typed Zero-Condition Recoupling Admissibility
- **Attack Vector:** Attempt to compose same-sign zero residues (e.g. $[0_{minus} \langle g \rangle_y 0_{minus}]$) in a nested trace and check if they can achieve a valid, non-null continuation without opposite-sign recoupling, which would falsify the necessity of oppositely typed recoupling.
- **Python Script:** `campaigns/attack_05_trace_admissibility_1_2d_1.py`
- **Verification Method:** Simulate nested trace composition. Force a local collapse and attempt to compose it: (1) same-sign zero residues ($0_{minus} \circ 0_{minus}$), (2) opposite-sign zero residues ($0_{minus} \circ 0_{plus}$). Check if same-sign collapse halts the system (as required by the rule) or persists.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that nested same-sign collapses ($0_{minus} \circ 0_{minus}$) lead to an undifferentiated null condition lacking directional provenance, failing the legality check and halting the system. Opposite-sign collapses ($0_{minus} \circ 0_{plus}$) successfully recoupled asymmetrically, restoring a non-zero relational tension (mismatch) and allowing the continuation process to proceed. Thus, the recoupling rules survived.

### FAT-06-CONDITIONED-DISTINCTION-1.2.2F: Attack on Conditioning Directionality & Primitiveness

- **Target Concept:** Formal Principle 1.2.2F: Primitive Conditioning Principle & 1.2.2E: Conditioning Directionality
- **Attack Vector:** Challenge the assertion that conditioning is strictly non-commutative ($\langle a \rangle_b \neq \langle b \rangle_a$) and directional. We attempt to construct a stable process loop using commutative (order-erasing) conditioning composition and evaluate if it collapses.
- **Python Script:** `campaigns/attack_06_conditioned_distinction_1_2_2f.py`
- **Verification Method:** Simulate process updates where the conditioning of distinction $a$ under context $b$ is: (1) directional/non-commutative ($\langle a \rangle_b = a + 0.1/b$), (2) commutative ($\langle a \rangle_b = a \cdot b$). Measure if the commutative system collapses due to order-erasure.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that commutative conditioning composition causes immediate distinction collapse. Under a commutative update rule, the distinction and context variables became mathematically symmetric and identical within 1 step ($E = 0$), halting the process due to a zero-mismatch collapse. Directional, non-commutative updates maintained stable persistence ($E > 0$). Thus, the conditioning directionality principle survived.

### FAT-07-CONTINUATION-COMPOSITION-2.3.2: Attack on Continuation Composition & Guards

- **Target Concept:** Formal Block 2.3.2: Continuation Composition & 2.3.2A: Typed Continuation Composition Guards
- **Attack Vector:** Attempt to compose incompatible endpoints or mismatching types without composition guards and evaluate whether the system can proceed stably or collapses/diverges.
- **Python Script:** `campaigns/attack_07_continuation_composition_2_3_2.py`
- **Verification Method:** Run a process composition loop. Composing $C(A,B) \circ C(D,E)$ where $B \neq D$. Compare: (1) compliant run (blocks incompatible composition, preserving stability of current active lineage), (2) ablated run (ignores guards, composing incompatible domains). Verify if the ablated system collapses or diverges.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that the continuation composition guards are strictly necessary for process stability. Composing incompatible endpoints in the ablated run caused a discontinuous state jump, which immediately exploded the relational mismatch and collapsed the process. The compliant run correctly blocked incompatible compositions, preserving trace integrity. Thus, the composition guards survived.

### FAT-08-RATE-ELIGIBILITY-2.8.7: Attack on Rate-Type Eligibility Predicate

- **Target Concept:** Governed Clarification 2.8.7: Rate-Type Eligibility Predicate
- **Attack Vector:** Attempt to evaluate a rate-based metric-bridge on a zero-DOF decoupled state without checking eligibility, trying to show that a valid metric bridge can be obtained without checking the predicate.
- **Python Script:** `campaigns/attack_08_rate_eligibility_2_8_7.py`
- **Verification Method:** Simulate metric-bridge evaluation on a zero-DOF state. Compare: (1) compliant run (predicate checks `DOF(x) > 0`, blocking evaluation and returning a clean failure signal), (2) ablated run (evaluates rate formula directly, leading to runtime division by zero or NaN).
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that the rate-type eligibility predicate `RATE_TYPE_ELIGIBLE` is strictly necessary to prevent singular/undefined calculations in metric bridge evaluations. Evaluating the bridge on a zero-DOF state without checking eligibility resulted in an immediate runtime division-by-zero crash. Checking eligibility cleanly blocked the evaluation, preserving system integrity. Thus, the predicate survived.

### FAT-09-RESIDUE-UPDATE-2.2.1: Attack on Residue Update Operator & Inscription

- **Target Concept:** Formal Block 2.2.1: The Inscription Operator $\Psi$ & Definition 2.7.8: Residue Update Operator
- **Attack Vector:** Test if the process can achieve stable persistence under random walk perturbations without updating the residue space (static, memoryless residue).
- **Python Script:** `campaigns/attack_09_residue_update_2_2_1.py`
- **Verification Method:** Simulate the process loop over 1000 steps with: (1) compliant run (residue updates dynamically), (2) ablated run (static residue, representing memoryless updates). Evaluate whether the ablated run collapses or diverges.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that the residue update operator $\Psi$ is strictly necessary to stabilize the process against random walk drift. Bypassing residue updates in the ablated run disabled the history-dependent corrective feedback loop, causing the state to drift and collapse at step 831. The compliant run dynamically updated its residue context, successfully persisting over all 1000 steps. Thus, the residue update operator survived.

### FAT-10-DIRECTED-DISTINCTION-3.1.1: Attack on Directed Distinction & Asymmetry

- **Target Concept:** Formal Statement 3.1.1: Directed Distinction
- **Attack Vector:** Attempt to run an update loop under a strictly symmetric distinction relation ($D(S_1|S_2) = D(S_2|S_1)$), evaluating if it can drive transitions without halting.
- **Python Script:** `campaigns/attack_10_directed_distinction_3_1_1.py`
- **Verification Method:** Simulate state updates directed toward a target state. Compare: (1) compliant run (asymmetric distinction relation generates non-zero update gradient), (2) ablated run (symmetric distinction relation, e.g. absolute difference, yielding zero update gradient).
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that a directed, asymmetric distinction relation is strictly necessary to generate the relational gradients that drive state updates. In the ablated run, using a symmetric distinction relation ($D(S_1|S_2) = |S_1 - S_2|$) caused the forward and reverse updates to cancel out, resulting in a zero-gradient condition that froze the state updates at step 1. The compliant run (using asymmetric updates) converged to the target state. Thus, the directed distinction concept survived.

### FAT-11-FLOOR-CONSTRAINT-3.4.1: Attack on Floor Constraint (Epsilon Floor)

- **Target Concept:** Formal Block 3.4.1: The Floor Constraint
- **Attack Vector:** Attempt to run the process with $\epsilon = 0.0$ (ablated floor), evaluating whether the system halts on degeneracy.
- **Python Script:** `campaigns/attack_11_floor_constraint_3_4_1.py`
- **Verification Method:** Simulate orientation-based state updates. Compare: (1) compliant run (floor $\epsilon = 0.01$ blocks distinction from falling to zero, preserving orientation gradient calculations), (2) ablated run (floor $\epsilon = 0.0$ allows distinction to become exactly zero, causing a division-by-zero crash or NaN degeneracy).
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that the floor constraint is strictly necessary to prevent orientation degeneracies (division-by-zero or NaN values) in state updates when the state matches the target. In Test 2 (starting at the target state), the ablated run (with $\epsilon = 0.0$) crashed immediately due to a zero division. The compliant run (with $\epsilon = 0.01$) stabilized successfully. Thus, the floor constraint survived.

### FAT-12-TRIADIC-CLOSURE-4.X.1: Attack on Asymmetric Triadic Closure

- **Target Concept:** Formal Statement 4.X.1: Asymmetric Triadic Closure Theorem
- **Attack Vector:** Perform Ablation M1 (orientation-removal/randomization) to test if triadic closure can stabilize the system without oriented restoring forces.
- **Python Script:** `campaigns/attack_12_triadic_closure_4_x_1.py`
- **Verification Method:** Simulate coupled triadic updates. Compare: (1) compliant run (updates oriented dynamically, providing negative feedback), (2) ablated run (updates using randomized orientations, representing Ablation M1). Evaluate if the ablated triad diverges and collapses.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that orientation alignment is strictly necessary to stabilize asymmetric triadic closure. While 100% of the compliant oriented runs converged stably to their average, 42.0% of the ablated runs (Ablation M1, randomized orientations) diverged past the admissibility boundary and collapsed. Thus, the triadic closure theorem survived.

### FAT-13-ORIENTATION-COHERENCE-5.1.5: Attack on Orientation Coherence Metric Candidate

- **Target Concept:** Formal Statement 5.1.5: Orientation Coherence Metric Candidate
- **Attack Vector:** Perform the four validation checks (`PO001_VT_001` through `PO001_VT_004`) on the implemented $C_{\text{orient}}$ metric.
- **Python Script:** `campaigns/attack_13_orientation_coherence_5_1_5.py`
- **Verification Method:** Implement the candidate metric: $C_{\text{orient}}(\chi_D) = 1 - \text{Var}_{\text{norm}}(\{ -(i)_k \})$. Test: (1) Input isolation (only uses $\chi_D$ and orientations), (2) Topology blindness (invariant under $T_{\text{class}}$ removal), (3) Closure blindness (invariant under $S_{\text{closure}}$ removal), (4) Shuffling sensitivity (lower score for random patterns).
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that the Orientation Coherence Metric Candidate $C_{\text{orient}}$ satisfies the non-circularity constraint. The metric successfully passed all 4 validation checks: (1) Input Isolation (runs purely on $\chi_D$ and orientation assignments), (2) Topology Blindness (invariant under $T_{\text{class}}$ modifications), (3) Closure Stability Blindness (invariant under $S_{\text{closure}}$ modifications), and (4) Shuffling Sensitivity (coherent score of $0.9951$ dropped to $0.1316$ when shuffled). Thus, the metric candidate survived.

---

## Detailed Attack Logs

### FAT-01-AXIOM-1.2.1: Attack on Primary Axiom

- **Target Concept:** Axiom 1.2.1 (The Statement): $(\mathcal{E} \neq 0) \iff_R \delta_a(\mathcal{E} > 0)$
- **Attack Vector:** We test if we can construct a simulated continuation system where continuation transitions ($\Delta$) can occur or stabilize under a zero-distinction condition ($\mathcal{E} = 0$), or conversely, if admissibility evaluation ($\delta_a$) can produce valid continuation states when there is zero mismatch.
- **Python Script:** `campaigns/attack_01_axiom_1_2_1.py`
- **Verification Method:** Run a process simulation where we force the distinction array $\chi_D$ to collapse to a single state (meaning all difference is erased, $\mathcal{E}=0$) and attempt to transition the system to a new state or check if the update rules permit non-trivial progress.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that when distinction is forced to zero ($\mathcal{E} = 0$), the legality gate immediately triggers a transition to the Zero-State, causing continuation to cease. Spontaneous recovery or generation of new distinctions from the Zero-State was impossible without an external mismatch source. The primary axiom's necessity and sufficiency conditions hold under the simulation boundary.

### FAT-02-TRACE-PRIORITY-1.2.6: Attack on Trace Priority Over Projection

- **Target Concept:** Formal Principle 1.2.6: Trace Priority Over Projection: $P(H_1) = P(H_2) \not\implies H_1 = H_2$
- **Attack Vector:** We test if we can construct a system or a regime where the history (trace) of continuation events can be uniquely reconstructed from the final-state projection, which would mean that process identity is NOT trace-prior but is instead projection-determined.
- **Python Script:** `campaigns/attack_02_trace_priority_1_2_6.py`
- **Verification Method:** Simulate two distinct process histories $H_1 \neq H_2$, mapping them through a projection $P$. Test if there exists a projection mapping $P$ that is injective (meaning $P(H_1) = P(H_2) \implies H_1 = H_2$), and evaluate whether this falsifies the general principle.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that while a simplified, linear state-accumulator model is injective and permits full historical reconstruction, any realistic RT system with non-linear admissibility gating is non-injective. We successfully demonstrated a collision where two distinct process histories ($H_1 \neq H_2$) resulted in identical final observable states and residue mappings. Thus, process identity is trace-prior, and the principle survived.

### FAT-03-UNIVERSAL-SCHEMA-1.3.2: Attack on Universal Law Schema ($U_{\Omega}$)

- **Target Concept:** Formal Principle 1.3.2: Universal Rule $U_{\Omega}$ (The Master Process Chain)
- **Attack Vector:** We test the necessity of the admissibility filter $\delta_a$ and mismatch optimization in preserving the non-null difference condition $\mathcal{E} > 0$ and structural stability.
- **Python Script:** `campaigns/attack_03_universal_schema_1_3_2.py`
- **Verification Method:** Simulate three variants of the process loop over 10000 steps: (1) full $U_{\Omega}$ compliance, (2) randomized selection (ablating $\delta_a$), (3) ignoring mismatch optimization. Compare structural stability and check for collapse.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that the admissibility filter $\delta_a$ is strictly necessary for stable process persistence. In 10,000-step simulations across 50 seeds, 100% of the runs with an ablated filter diverged and collapsed, whereas 100% of the $U_{\Omega}$-compliant runs achieved stable persistence. Thus, the master schema survived.

### FAT-04-REGIME-BOUNDARY-1.2.2b.6: Attack on L/NL Regime Boundary and Transition

- **Target Concept:** Governed Clarification 1.2.2B.6: L/NL Regime Boundary and Transition: $RT_{operational\_regime} \to L \lor NL$
- **Attack Vector:** Attempt to construct a process that accumulates high residue feedback ($R_t \gg 0, k > 0$) but remains strictly linear and composable (low fitting error under a linear operator representation), trying to falsify the claim that residue feedback inevitably deforms local composition.
- **Python Script:** `campaigns/attack_04_regime_boundary_1_2_2b_6.py`
- **Verification Method:** Run a process simulation where we introduce high residue feedback ($k=0.5$). Fit a linear matrix operator to predict state updates and measure the fitting error (R2 score). If the linear fit remains highly accurate ($R^2 > 0.99$), the boundary transition logic is falsified.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that residue feedback successfully deforms state composition, introducing non-linearities that make linear operators inaccurate. With $k = 0.0$ (no feedback), a linear operator fit the transition updates perfectly ($R^2 = 1.0$), confirming the system is in the linear regime ($L$). However, with $k = 0.5$ (high feedback), the linear fit quality dropped to $R^2 = 0.8028$, failing the linearity threshold ($R^2 \ge 0.99$), confirming the transition to the nonlinear regime ($NL$) and verifying the survival of the concept.

### FAT-05-TRACE-ADMISSIBILITY-1.2D.1: Attack on Trace-Admissibility & Recoupling

- **Target Concept:** Formal Principle 1.2D.1: Trace-Admissibility (PRIN_001) & 1.2D.2: Typed Zero-Condition Recoupling Admissibility
- **Attack Vector:** Attempt to compose same-sign zero residues (e.g. $[0_{minus} \langle g \rangle_y 0_{minus}]$) in a nested trace and check if they can achieve a valid, non-null continuation without opposite-sign recoupling, which would falsify the necessity of oppositely typed recoupling.
- **Python Script:** `campaigns/attack_05_trace_admissibility_1_2d_1.py`
- **Verification Method:** Simulate nested trace composition. Force a local collapse and attempt to compose it: (1) same-sign zero residues ($0_{minus} \circ 0_{minus}$), (2) opposite-sign zero residues ($0_{minus} \circ 0_{plus}$). Check if same-sign collapse halts the system (as required by the rule) or persists.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that nested same-sign collapses ($0_{minus} \circ 0_{minus}$) lead to an undifferentiated null condition lacking directional provenance, failing the legality check and halting the system. Opposite-sign collapses ($0_{minus} \circ 0_{plus}$) successfully recoupled asymmetrically, restoring a non-zero relational tension (mismatch) and allowing the continuation process to proceed. Thus, the recoupling rules survived.

### FAT-06-CONDITIONED-DISTINCTION-1.2.2F: Attack on Conditioning Directionality & Primitiveness

- **Target Concept:** Formal Principle 1.2.2F: Primitive Conditioning Principle & 1.2.2E: Conditioning Directionality
- **Attack Vector:** Challenge the assertion that conditioning is strictly non-commutative ($\langle a \rangle_b \neq \langle b \rangle_a$) and directional. We attempt to construct a stable process loop using commutative (order-erasing) conditioning composition and evaluate if it collapses.
- **Python Script:** `campaigns/attack_06_conditioned_distinction_1_2_2f.py`
- **Verification Method:** Simulate process updates where the conditioning of distinction $a$ under context $b$ is: (1) directional/non-commutative ($\langle a \rangle_b = a + 0.1/b$), (2) commutative ($\langle a \rangle_b = a \cdot b$). Measure if the commutative system collapses due to order-erasure.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that commutative conditioning composition causes immediate distinction collapse. Under a commutative update rule, the distinction and context variables became mathematically symmetric and identical within 1 step ($E = 0$), halting the process due to a zero-mismatch collapse. Directional, non-commutative updates maintained stable persistence ($E > 0$). Thus, the conditioning directionality principle survived.

### FAT-07-CONTINUATION-COMPOSITION-2.3.2: Attack on Continuation Composition & Guards

- **Target Concept:** Formal Block 2.3.2: Continuation Composition & 2.3.2A: Typed Continuation Composition Guards
- **Attack Vector:** Attempt to compose incompatible endpoints or mismatching types without composition guards and evaluate whether the system can proceed stably or collapses/diverges.
- **Python Script:** `campaigns/attack_07_continuation_composition_2_3_2.py`
- **Verification Method:** Run a process composition loop. Composing $C(A,B) \circ C(D,E)$ where $B \neq D$. Compare: (1) compliant run (blocks incompatible composition, preserving stability of current active lineage), (2) ablated run (ignores guards, composing incompatible domains). Verify if the ablated system collapses or diverges.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that the continuation composition guards are strictly necessary for process stability. Composing incompatible endpoints in the ablated run caused a discontinuous state jump, which immediately exploded the relational mismatch and collapsed the process. The compliant run correctly blocked incompatible compositions, preserving trace integrity. Thus, the composition guards survived.

### FAT-08-RATE-ELIGIBILITY-2.8.7: Attack on Rate-Type Eligibility Predicate

- **Target Concept:** Governed Clarification 2.8.7: Rate-Type Eligibility Predicate
- **Attack Vector:** Attempt to evaluate a rate-based metric-bridge on a zero-DOF decoupled state without checking eligibility, trying to show that a valid metric bridge can be obtained without checking the predicate.
- **Python Script:** `campaigns/attack_08_rate_eligibility_2_8_7.py`
- **Verification Method:** Simulate metric-bridge evaluation on a zero-DOF state. Compare: (1) compliant run (predicate checks `DOF(x) > 0`, blocking evaluation and returning a clean failure signal), (2) ablated run (evaluates rate formula directly, leading to runtime division by zero or NaN).
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that the rate-type eligibility predicate `RATE_TYPE_ELIGIBLE` is strictly necessary to prevent singular/undefined calculations in metric bridge evaluations. Evaluating the bridge on a zero-DOF state without checking eligibility resulted in an immediate runtime division-by-zero crash. Checking eligibility cleanly blocked the evaluation, preserving system integrity. Thus, the predicate survived.

### FAT-09-RESIDUE-UPDATE-2.2.1: Attack on Residue Update Operator & Inscription

- **Target Concept:** Formal Block 2.2.1: The Inscription Operator $\Psi$ & Definition 2.7.8: Residue Update Operator
- **Attack Vector:** Test if the process can achieve stable persistence under random walk perturbations without updating the residue space (static, memoryless residue).
- **Python Script:** `campaigns/attack_09_residue_update_2_2_1.py`
- **Verification Method:** Simulate the process loop over 1000 steps with: (1) compliant run (residue updates dynamically), (2) ablated run (static residue, representing memoryless updates). Evaluate whether the ablated run collapses or diverges.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that the residue update operator $\Psi$ is strictly necessary to stabilize the process against random walk drift. Bypassing residue updates in the ablated run disabled the history-dependent corrective feedback loop, causing the state to drift and collapse at step 831. The compliant run dynamically updated its residue context, successfully persisting over all 1000 steps. Thus, the residue update operator survived.

### FAT-10-DIRECTED-DISTINCTION-3.1.1: Attack on Directed Distinction & Asymmetry

- **Target Concept:** Formal Statement 3.1.1: Directed Distinction
- **Attack Vector:** Attempt to run an update loop under a strictly symmetric distinction relation ($D(S_1|S_2) = D(S_2|S_1)$), evaluating if it can drive transitions without halting.
- **Python Script:** `campaigns/attack_10_directed_distinction_3_1_1.py`
- **Verification Method:** Simulate state updates directed toward a target state. Compare: (1) compliant run (asymmetric distinction relation generates non-zero update gradient), (2) ablated run (symmetric distinction relation, e.g. absolute difference, yielding zero update gradient).
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that a directed, asymmetric distinction relation is strictly necessary to generate the relational gradients that drive state updates. In the ablated run, using a symmetric distinction relation ($D(S_1|S_2) = |S_1 - S_2|$) caused the forward and reverse updates to cancel out, resulting in a zero-gradient condition that froze the state updates at step 1. The compliant run (using asymmetric updates) converged to the target state. Thus, the directed distinction concept survived.

### FAT-11-FLOOR-CONSTRAINT-3.4.1: Attack on Floor Constraint (Epsilon Floor)

- **Target Concept:** Formal Block 3.4.1: The Floor Constraint
- **Attack Vector:** Attempt to run the process with $\epsilon = 0.0$ (ablated floor), evaluating whether the system halts on degeneracy.
- **Python Script:** `campaigns/attack_11_floor_constraint_3_4_1.py`
- **Verification Method:** Simulate orientation-based state updates. Compare: (1) compliant run (floor $\epsilon = 0.01$ blocks distinction from falling to zero, preserving orientation gradient calculations), (2) ablated run (floor $\epsilon = 0.0$ allows distinction to become exactly zero, causing a division-by-zero crash or NaN degeneracy).
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that the floor constraint is strictly necessary to prevent orientation degeneracies (division-by-zero or NaN values) in state updates when the state matches the target. In Test 2 (starting at the target state), the ablated run (with $\epsilon = 0.0$) crashed immediately due to a zero division. The compliant run (with $\epsilon = 0.01$) stabilized successfully. Thus, the floor constraint survived.

### FAT-12-TRIADIC-CLOSURE-4.X.1: Attack on Asymmetric Triadic Closure

- **Target Concept:** Formal Statement 4.X.1: Asymmetric Triadic Closure Theorem
- **Attack Vector:** Perform Ablation M1 (orientation-removal/randomization) to test if triadic closure can stabilize the system without oriented restoring forces.
- **Python Script:** `campaigns/attack_12_triadic_closure_4_x_1.py`
- **Verification Method:** Simulate coupled triadic updates. Compare: (1) compliant run (updates oriented dynamically, providing negative feedback), (2) ablated run (updates using randomized orientations, representing Ablation M1). Evaluate if the ablated triad diverges and collapses.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The simulation verified that orientation alignment is strictly necessary to stabilize asymmetric triadic closure. While 100% of the compliant oriented runs converged stably to their average, 42.0% of the ablated runs (Ablation M1, randomized orientations) diverged past the admissibility boundary and collapsed. Thus, the triadic closure theorem survived.

### FAT-11-FLOOR-CONSTRAINT-DS: Falsification of Floor Constraint (Dynamical Systems)

- **Target Concept:** Formal Block 3.4.1: The Floor Constraint
- **Attack Vector:** Model state tracking using standard continuous dynamical systems gradient descent (which scales with distance), verifying that it converges smoothly without any floor constraint or singularity. Compare this to the RT floor constraint, which creates high-frequency boundary oscillations (chattering) or instability near the attractor when step size $\alpha > \epsilon$.
- **Python Script:** `campaigns/attack_11_floor_constraint_ds.py`
- **Outcome:** **Falsified**
- **Findings:** The campaign successfully falsified the fundamental necessity of the floor constraint. Standard smooth gradient descent converged asymptotically to the attractor without any floor constraint or coordinate singularity. In contrast, the RT floor formulation introduced a discontinuous boundary projection that caused high-frequency chattering (9 sign changes in the final 10 steps), showing that the floor constraint is an artifact of a singular coordinate projection choice rather than a fundamental process requirement.

### FAT-12-TRIADIC-CLOSURE-CT: Falsification of Asymmetric Triadic Closure (Category Theory)

- **Target Concept:** Formal Statement 4.X.1: Asymmetric Triadic Closure Theorem
- **Attack Vector:** Model asymmetric updates as morphisms in a category. Test if they satisfy the Category Theory identity axiom.
- **Python Script:** `campaigns/attack_12_triadic_closure_ct.py`
- **Outcome:** **Falsified**
- **Findings:** The campaign successfully falsified the categorical consistency of asymmetric triadic closure. In Category Theory, every object must possess an identity morphism that permits composition without state change. However, in the RT framework, any identity morphism must represent a transition with zero distinction ($D = 0$). By Axiom 1.2.1, a zero-distinction condition halts the process and collapses the state to the Zero-State, preventing the existence of any valid identity morphisms for active states.

### FAT-13-ORIENTATION-COHERENCE-IT: Falsification of Orientation Coherence Metric (Information Theory)

- **Target Concept:** Formal Statement 5.1.5: Orientation Coherence Metric Candidate
- **Attack Vector:** Compare the variance-based $C_{\text{orient}}$ metric with an information-theoretic coherence metric based on Shannon Entropy ($C_{\text{entropy}}$) under a bimodal structured state (bipolar alignment).
- **Python Script:** `campaigns/attack_13_orientation_coherence_it.py`
- **Outcome:** **Falsified**
- **Findings:** The campaign successfully falsified the variance-based $C_{\text{orient}}$ metric. Under a bimodal structured state (bipolar alignment at $0$ and $\pi$), the orientation distribution is highly ordered and has very low Shannon entropy ($C_{\text{entropy}} = 0.8066$). However, because the orientations point in opposite directions, their mean resultant length cancels out completely, causing the variance-based metric to yield $C_{\text{orient}} = 0.0000$, misclassifying a highly structured state as completely incoherent/random.
### FAT-14-RELATIONAL-CLUSTER-5.Z.1: Attack on Relational Cluster

- **Target Concept:** Formal Block 5.Z.1: Relational Cluster
- **Attack Vector:** Perform a topological and graph-theoretic analysis of a connected chain of processes to show that Betti-0 connectedness does not imply the pairwise alignment clique condition required by the definition.
- **Python Script:** `campaigns/attack_14_relational_cluster_5_z_1.py`
- **Verification Method:** Simulate a 3-process chain $A - B - C$ where $A$ and $B$ are oriented/aligned, and $B$ and $C$ are oriented/aligned, but $A$ and $C$ are out of phase. Compute Betti-0 and check if the pairwise alignment clique condition holds.
- **Outcome:** **Falsified**
- **Findings:** The campaign successfully falsified the topological definition of a Relational Cluster. A 3-process chain $A - B - C$ forms a single connected component in the phase field (Betti-0 count $\beta_0 = 1$), but the end processes $A$ and $C$ are not mutually aligned, violating the definition's requirement that all cluster members must be pairwise aligned (clique condition). This proves that Betti-0 connectedness is topologically distinct from pairwise alignment, exposing an inconsistency in the definition.

### FAT-15-PROCESS-PRIORITY: Attack on Process Priority (Ontological Dependency)

- **Target Concept:** Formal Reduction 1.1A.1: Process-First Dependency
- **Attack Vector:** Perform Dual Falsification: (1) Program M (Native MTO-OTM) attempts to decompose Process, remove the Distinction aspect, and recompose it to see if identity is preserved, (2) Program S (Standard Mathematics) formalizes state spaces in set theory/topology to verify if a non-trivial process can be defined without pre-existing distinguishability (distinction).
- **Python Script:** `campaigns/attack_15_process_priority.py`
- **Verification Method:** Compare Program M loss of identity and Program S set-theoretic boundary checks.
- **Outcome:** **Falsified**
- **Findings:** The campaign successfully falsified the ontological dependency assumption $Process \succ_{ont} Distinction$ using the Dual Falsification Program. Program M (Native MTO-OTM) showed that OTM-decomposition of Process cannot occur without including the Distinction aspect; removing it collapses MTO-recomposition to the Zero-State (loss of identity). Program S (Standard Mathematics) showed that any non-trivial state transition system (Process) mathematically requires a distinguishability relation (Distinction) to define a state space with cardinality $> 1$, proving that Distinction is a prerequisite for Process rather than a derivative.

### FAT-16-OTM-CAPACITY-PRIMITIVE: Attack on OTM Capacity Primitive

- **Target Concept:** Section 3.1E: Relational Capacity and the $n$ Subscript
- **Attack Vector:** Perform Dual Falsification: (1) Program M (Native MTO-OTM) tests if OTM can allocate $n$ capacity channels without active distinctions, and if distinction is only needed during MTO realization, (2) Program S (Standard Mathematics) tests if a set-theoretic index set representing capacity $n > 1$ can be defined without a distinguishability relation (distinction).
- **Python Script:** `campaigns/attack_16_otm_capacity_primitive.py`
- **Verification Method:** Compare Program M procedural allocation and Program S cardinal representation.
- **Outcome:** **PROJECTION_FALSIFIED**
- **Findings:** The campaign successfully executed the Dual Falsification Program. Program M (Native MTO-OTM) survived: it verified that OTM successfully instantiates capacity $n$ as empty coordinate slots/channels without requiring any active distinction values, and that distinction only becomes necessary during MTO realization. However, Program S (Standard Mathematics) failed: representing any cardinal capacity $n > 1$ in set theory mathematically requires a pre-existing distinguishability relation to define the index set. This represents a projection failure (representation loss) where standard mathematics cannot represent coordinate dimension without presupposing value distinguishability, while the native calculus successfully treats Capacity as primitive.

### FAT-17-PRIMITIVE-SLOT: Attack on Primitive OTM Slot

- **Target Concept:** Section 3.1E: Relational Capacity Slots
- **Attack Vector:** Perform Dual Falsification: (1) Program M (Native MTO-OTM) tests if removing slot labels (identity ablation) causes multiple slots to collapse into a single degree of freedom, (2) Program S (Standard Mathematics) tests if multiple coordinates/variables in a product space can exist without an indexing/distinguishability relation.
- **Python Script:** `campaigns/attack_17_primitive_slot.py`
- **Verification Method:** Compare Program M slot labels ablation and Program S product space coordinates indexing.
- **Outcome:** **Falsified**
- **Findings:** The campaign successfully falsified the primitive OTM slot concept using the Dual Falsification Program. Program M (Native MTO-OTM) failed: it demonstrated that when slot labels (identity) are ablated, multiple slots cannot maintain independent values. Any update is applied symmetrically to all slots, collapsing the 3 degrees of freedom to 1. Program S (Standard Mathematics) also failed: in set theory and coordinate systems, multiple variables cannot be defined in a product space without a distinguishability relation (index set) to keep them distinct. This proves that capacity slots inherently import distinction, meaning Distinction remains the absolute primitive.

### FAT-18-CAUSAL-CLOSURE: Attack on Causal Closure

- **Target Concept:** Section 11.1A: Relational Basin Signatures
- **Attack Vector:** Perform Dual Falsification: (1) Program M (Native MTO-OTM) tests if local closure emerges purely from causal propagation limits on a relational graph without geometric boundaries, (2) Program S (Standard Mathematics) tests if a propagation-limited closure operator can be defined as the least fixed point of a monotone update operator.
- **Python Script:** `campaigns/attack_18_causal_closure.py`
- **Verification Method:** Compare Program M graph propagation simulation and Program S monotone operator fixed-point analysis.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The campaign verified that the concept of Causal Closure successfully survived. Both the native procedure (Program M) and standard mathematical formalization (Program S) agree that local closure (stable basins of activity) can emerge purely from distinction propagation limits (attenuation and thresholding) on a graph without requiring spatial or geometric boundaries. Standard mathematics rigorously models this as the least fixed point of a monotone reachability operator (Knaster-Tarski theorem), which defines a valid algebraic closure operator (equivalent to an Alexandroff topology).

### FAT-19-DOMAIN-COUPLING: Attack on Domain Coupling

- **Target Concept:** Section 5.ZZ / Chapter 9: Domain Coupling
- **Attack Vector:** Perform Dual Falsification: (1) Program M (Native MTO-OTM) tests if complete decoupling reduces activity to zero, if selective decoupling creates domain-relative activity, and if propagation/closure fail without coupling, (2) Program S (Standard Mathematics) represents coupling as domain-relative adjacency matrices and category-theoretic subcategory embeddings.
- **Python Script:** `campaigns/attack_19_domain_coupling.py`
- **Verification Method:** Compare Program M multi-domain simulation and Program S category-theoretic composition analysis.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The campaign verified that the concept of Domain Coupling successfully survived. Both the native procedure (Program M) and standard mathematical analysis (Program S) agree that coupling is the necessary and sufficient primitive relation for domain-relative causal participation. Program M demonstrated that decoupling a node from a domain reduces its causal activity to zero in that domain while preserving it in other coupled domains, and that propagation/closure depend entirely on active coupling. Program S formalized coupling as domain-relative adjacency matrices and category morphisms, confirming that uncoupled nodes have zero composability/influence.

### FAT-20-RELATIONAL-ORDERING: Attack on Relational Ordering

- **Target Concept:** Section 3.2A: Ordering as Structural Information
- **Attack Vector:** Perform Dual Falsification: (1) Program M (Native MTO-OTM) tests if relational ordering can define coupling and propagation without metric, temporal, or adjacency assumptions, (2) Program S (Standard Mathematics) tests if standard posets/preorders collapse mutual feedback loops due to antisymmetry, if category theory collapses under identity morphisms, and if information theory is order-free.
- **Python Script:** `campaigns/attack_20_relational_ordering.py`
- **Verification Method:** Compare Program M poset representation and Program S mathematical collapse checks.
- **Outcome:** **PROJECTION_FALSIFIED**
- **Findings:** The campaign successfully executed the Dual Falsification Program. Program M (Native MTO-OTM) survived: it verified that native relational ordering successfully traces reciprocal cycles, derives coupling, and supports propagation without requiring graph adjacency matrices, metrics, or temporal succession. However, Program S (Standard Mathematics) failed: standard partial orders (posets) collapse reciprocal cycles to a single element due to antisymmetry, categories collapse under identity morphisms (zero distinction loops under Axiom 1.2.1), and information theory lacks ordering. This represents a projection failure where standard mathematical representations cannot formalize reciprocal ordering primitives without collapse, validating native Relational Ordering as a primitive.

### FAT-21-ADMISSIBILITY-COMPUTATION: Attack on Admissibility Gated Computation

- **Target Concept:** Section 3.1: The Admissibility Filter
- **Attack Vector:** Perform Dual Falsification: (1) Program M (Native MTO-OTM) tests if removing/saturating admissibility collapses computation, and if changing reference or dynamic gating yields different structured slices, (2) Program S (Standard Mathematics) represents admissibility as constraint satisfaction on rewrite rules and compares it with Turing machines/lambda calculus which lack observer-relative gating.
- **Python Script:** `campaigns/attack_21_admissibility_computation.py`
- **Verification Method:** Compare Program M computational trajectory simulation and Program S constraint satisfaction analysis.
- **Outcome:** **PROJECTION_FALSIFIED**
- **Findings:** The campaign successfully executed the Dual Falsification Program. Program M (Native MTO-OTM) survived: it verified that admissibility gating is strictly necessary to stabilize orientation trajectories into structured computation, and that changing or dynamically shifting observer references yields different structured slices. However, Program S (Standard Mathematics) failed: representing admissibility as constraint satisfaction on rewrite rules is valid, but conventional models of computation (Turing machine, lambda calculus) fail to represent observer-relative gating as a primitive. This confirms a representation loss in conventional computation rather than a native defect, validating native observer-relative Admissibility as a computational primitive.

### FAT-22-ADMISSIBILITY-FIELD-CAUSAL-LIMIT: Attack on Admissibility Field and Causal Limit

- **Target Concept:** Section 3.1: The Admissibility Filter
- **Attack Vector:** Perform Dual Falsification: (1) Program M (Native MTO-OTM) tests if varying coupling relations shifts the causal limit while keeping the admissibility field fixed, if local closure emerges naturally from coupling loss, and if domain-relative inertness/influence are preserved, (2) Program S (Standard Mathematics) formalizes the admissibility field as a global accessibility relation (or preorder) and active coupling as a subgraph.
- **Python Script:** `campaigns/attack_22_admissibility_field_causal_limit.py`
- **Verification Method:** Compare Program M multi-domain simulation and Program S directed graph reachability analysis.
- **Outcome:** **Survived (Falsification Failed)**
- **Findings:** The campaign verified that the concept of Admissibility Field and Causal Limit successfully survived. Both the native procedure (Program M) and standard mathematical formalization (Program S) agree that the admissibility field (possible transitions) and the causal limit (active reach) are mathematically distinct structures. Program M showed that varying active coupling shifts the causal limit while the global admissibility field remains fixed, and that local closure emerges naturally from coupling loss without external boundaries. Program S successfully represented the admissibility field as a global graph and active coupling as a subgraph, where reachability components define local closures without metric/geometric boundaries.

### FAT-23-REFERENCE-CENTERED-ORDERED-RELATION: Attack on Reference Centered Ordered Relation

- **Target Concept:** Section 3.2A: Ordering as Structural Information
- **Attack Vector:** Perform Dual Falsification: (1) Program M (Native MTO-OTM) tests if reference ablation destroys ordered comparability, if orientation ablation destroys ordering, if identical terms remain distinct through roles alone, and if degenerate symmetry collapses the triplet, (2) Program S (Standard Mathematics) tests if standard set theory collapses identical terms without indexing, and if binary reduction of the triplet to pairs loses whole-triplet dependency.
- **Python Script:** `campaigns/attack_23_reference_centered_ordered_relation.py`
- **Verification Method:** Compare Program M triplet simulation and Program S mathematical collapse checks.
- **Outcome:** **PROJECTION_FALSIFIED**
- **Findings:** The campaign successfully executed the Dual Falsification Program. Program M (Native MTO-OTM) survived: it verified that reference-centered ordered relations successfully keep identical terms distinct through relational roles alone (without collapse or indexing) and operate as an irreducible ternary unit. However, Program S (Standard Mathematics) failed: representing the relation in standard set theory collapses identical terms without numbering/indexing (which introduces external structure), and binary reduction to pairs loses the joint complementary dependency relative to the reference. This represents a projection failure in standard mathematics, validating the native Reference-Centered Triplet as a primitive computational unit.

### FAT-24-TRIPLET-IDENTITY-EQUIVALENCE: Attack on Triplet Identity Equivalence

- **Target Concept:** Section 3.2A: Ordering as Structural Information
- **Attack Vector:** Perform Dual Falsification: (1) Program M (Native MTO-OTM) tests structural replay, orientation reversal, reference substitution/reorientation, admissibility deformation, projection aliases, binary decomposition, and closure many-to-one mapping, (2) Program S (Standard Mathematics) tests if standard observational-equivalence and bisimulation collapse distinct triplets that have different pre-closure phase signatures.
- **Python Script:** `campaigns/attack_24_triplet_identity_equivalence.py`
- **Verification Method:** Compare Program M equivalence relation and Program S observational collapse check.
- **Outcome:** **PROJECTION_FALSIFIED**
- **Findings:** The campaign successfully executed the Dual Falsification Program. Program M (Native MTO-OTM) survived: it verified that the native triplet identity equivalence rule successfully distinguishes structural aliases (different internal triplets that yield identical slices) and pre-closure phase signatures (different triplets that reduce to the same RT) using whole-relation invariants. However, Program S (Standard Mathematics) failed: conventional observational-equivalence and bisimulation models collapse structural aliases and pre-closure signatures because they equate behavioral outputs to structural identity. This represents a projection failure where standard equivalence models suffer from representation collapse, validating the native Triplet Identity Equivalence rule.
