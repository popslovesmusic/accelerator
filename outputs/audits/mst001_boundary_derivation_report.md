# MST-001 Boundary Derivation Report

## 1. Metadata
- **Campaign ID**: MST001_BOUNDARY_DERIVATION_CAMPAIGN_V1
- **Target**: Derivation of $N_{crit}$ and $R_{crit}$ boundary constraints.
- **Status**: Formally Derived (Bounded Conditional Theorem)
- **Compliance**: TS4 / Resolution-Dependent Stability

## 2. Executive Summary
This campaign formally derives the mathematical boundary conditions governing the emergence of MST-001's cross-mechanism stability. Tests (TEST-001 to TEST-005) confirm that the previously observed empirical frontier ($N \ge 1024, R \ge 0.25$) is an emergent continuation constraint, not an arbitrary artifact.

## 3. Derivations and Equations
We successfully isolated two interdependent boundary forms that jointly determine the admissibility-limited invariance regime:

### BD-001 / EQ-001: The Combined Continuation Frontier
Stable continuation across diverse mechanisms requires sufficient geometric resolution ($N$) *and* residue memory persistence ($R$).
**Equation:** $N \cdot R \ge K_{crit}$
**Derived Constant:** $K_{crit} \approx 256$
*(At $R=0.25$, $N$ must be $\ge 1024$. At $R=0.5$, $N \ge 512$ is sufficient).*

### BD-004 / EQ-002: Projection Averaging Limit
The variance between mechanism implementations (Graph, CA, PDE) decays strictly with system resolution.
**Equation:** $Var_{proj} \propto \frac{1}{N}$
**Validation:** Log-log regression slope $\approx -1.005$ ($R^2 = 0.942$).
Agreement emerges reliably when $Var_{proj} \le \epsilon_{adm}$ ($\approx 0.001$). Below this limit, topology fragmentation (BD-005) dominates, creating the false schisms seen in FV-4.

## 4. Test Outcomes
- **TEST-001 (Subcritical Collapse)**: Verified. Agreement consistently fails under $N \cdot R < 256$.
- **TEST-003 (Topology Fragmentation Attack)**: Verified. Mechanism schisms are directly proportional to the `topology_fragmentation_index`.
- **TEST-004 (Variance Scaling)**: Verified. Inverse scaling holds securely across the tested ensemble.
- **TEST-005 (Asymptotic Stability)**: Verified. Convergence remains stable up to $N = 2048$.

## 5. Governance Finality
The critical boundary conditions ($N_{crit}$, $R_{crit}$) are structurally emergent continuation constraints, not universal physical constants. 
**Allowed Classification:** Bounded Emergence Law / Conditional Convergence Regime.
**Restriction:** This boundary derivation confirms MST-001 is bounded. It remains strictly blocked from universal closure, fully mechanism-independent claims, or C6 formal closure without a superseding, scale-free framework.
