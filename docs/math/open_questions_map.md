# Open Questions Map

This document tracks and categorizes open mathematical questions within the Mono-Process Framework, providing a human-readable counterpart to `registry/math/math_registry.json`.

## Categorized Open Questions

### Existence & Uniqueness
- **Q-EX-01**: How do specific selection rules interact with multi-branch retention?
- **Q-UN-01**: What conditions make selection locally unique in degenerate minima scenarios?

### Stability & Convergence
- **Q-ST-01**: Does stabilization survive infinite iteration in recursive transport?
- **Q-CV-01**: What exact decay rates are required for CSI summation to ensure flux convergence?

### Transport & Closure
- **Q-TR-01**: How to formalize residue conservation vs. dissipation in non-local transport?
- **Q-CL-01**: Definition of transport closure for infinite recursive systems.

### Operator Dynamics
- **Q-OP-01**: How does `delta` compose with `Pi_A` and `NavT` under selection constraints?
- **Q-OP-02**: Can selection be reconstructed from observed continuation events?

## Dependency Mapping
- **MT-001 Resilience** depends on resolution of **Q-UN-01**.
- **MT-002 Stability** depends on resolution of **Q-TR-01**.
- **MT-003 Validity** depends on resolution of **Q-EX-01**.

## Governance Note
Open questions are documented for research guidance. Resolution requires formal proof obligations and evidence-ladder satisfaction.
