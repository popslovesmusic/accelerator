# Appendix C: Induction Checklist

This checklist defines the rigorous steps required to promote a **Candidate Operator** or **Induced Domain** to **Verified/Core** status.

### 1. Conceptual Rewriting
- [ ] Can the target be rewritten as a **process activity** rather than a static object?
- [ ] Does it decompose into $\epsilon, R, \rho, K/CSI, \Delta, \text{ or } -(i)$?
- [ ] Does it avoid prohibited primitives (e.g., field-as-primitive, fixed location)?

### 2. Trace-to-Core
- [ ] Is there an explicit derivation tracing the target back to $(\mathcal{E} \neq 0) \iff_R \delta_a(\mathcal{E} > 0)$?
- [ ] Are all intermediate assumptions marked and justified?

### 3. Operational Binding
- [ ] Are there defined **observables** that can be extracted via $\iff_m$ or $\iff_s$?
- [ ] Is there a proposed **measurement protocol**?
- [ ] Is there a clear **falsification condition**?

### 4. Mechanism Independence
- [ ] Does the behavior hold across at least two independent **mechanism classes** (e.g., Agent-based and PDE)?
- [ ] Has the target been tested in at least three different parameter/seed regimes?

### 5. Algebraic Stability
- [ ] Does the target maintain invariant properties under recursive continuation?
- [ ] Are the composition and associativity rules defined and tested?
- [ ] Does the floor $\epsilon$ prevent singularities in the target's operation?

### 6. Governance Approval
- [ ] Has the target been registered in the `lexicon_validation_registry.json`?
- [ ] Has the evidence pack been reviewed and assigned an L-level (L2 or higher required for non-provisional use)?
