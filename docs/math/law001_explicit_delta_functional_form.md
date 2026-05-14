# LAW-001: Explicit Delta Functional Form

## Candidate Law Statement
### Informal
Given a non-null local mismatch $E_\alpha > 0$, $\delta$ returns the admissible set of continuation candidates available to locus $\alpha$ under local projection, transport coupling, and selection constraints.

### Symbolic Candidate
$$\delta(E_\alpha > 0) := \{ x'_\alpha \in A_\alpha : x'_\alpha = x_\alpha + \Pi_{A_\alpha}(\sum_{\beta \in CSI(\alpha)} NavT(\omega_\alpha, \omega_\beta)), \text{ and } E_\alpha > \epsilon_{null} \}$$

### Multi-Valued Form
$$\delta(E_\alpha > 0) \subseteq C_\alpha$$

### Selection Form
$$Sel_\alpha(\delta(E_\alpha > 0)) \rightarrow \text{one or more admissible continuation branches}$$

## Context & Objectives
This candidate functional form represents the first step in the explicit law program for the process $\delta$. It moves the operator from a scaffolded symbolic definition toward a testable candidate law that explicitly incorporates:
- **Participation Threshold:** delta is only defined when E_alpha > epsilon_null.
- **Admissibility Constraint:** Continuation must lie within the local admissibility window A_alpha via projection Pi_A.
- **Transport Coupling:** The magnitude and direction of continuation are driven by integrated transport from the Causal Sphere of Influence (CSI).
- **Multi-Valued Branching:** The law preserves the possibility of multi-valued continuation, explicitly rejecting forced uniqueness or deterministic collapse at this stage.

## Law Conditions
1. **Delta defined only for non-null participation:** $\delta$ maps from the domain where $E_\alpha > \epsilon_{null}$.
2. **Epsilon-null threshold explicit:** The requirement for non-zero mismatch is fundamental.
3. **Admissibility window projection explicit:** $\Pi_{A_\alpha}$ ensures all candidates are valid process updates.
4. **NavT transport input explicit:** Continuation is driven by the transport operator.
5. **CSI domain explicit:** Interaction is limited to the causally coupled set.
6. **Multi-valued continuation preserved:** No assumption of single-valued output.
7. **Selection not forced unique:** Selection rules may yield multiple branches.
8. **Non-invertibility preserved:** NavT transport does not imply global state reconstructability.

## Failure Modes to Preserve
- **Deterministic Delta Collapse:** Prematurely assuming $\delta$ must yield a single result.
- **Unique Continuation Overclaim:** Claiming unique trajectories without selection-rule evidence.
- **Global Operator Closure Overclaim:** Claiming $\delta$ is closed over all process states.
- **Implicit Invertibility:** Assuming $\delta$ or NavT can be inverted to recover prior states.
- **Epsilon-null Boundary Ambiguity:** Undefined behavior exactly at the threshold.
- **Empty Continuation Image:** Cases where no admissible candidates exist despite mismatch.
- **Unbounded CSI Sum:** Divergence of integrated transport.
- **Physics Claim Leakage:** Treating this candidate form as an established physical law.

## Next Steps
Following the formalization of $\delta(E > 0)$, the law program will proceed to define the explicit behavior of the admissibility projection $\Pi_A$ (LAW-002).
