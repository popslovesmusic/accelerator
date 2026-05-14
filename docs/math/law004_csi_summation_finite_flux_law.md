# LAW-004: CSI Summation and Finite Flux Law

## Candidate Law Statement
### Informal
For each locus $\alpha$, aggregate transport is formed by summing $NavT$ contributions from $\beta$ inside $CSI(\alpha)$, but only under weighting and decay conditions that preserve finite flux.

### Symbolic Candidate
$$T_\alpha := \sum_{\beta \in CSI(\alpha)} W_{CSI}(\alpha, \beta) \cdot K_{orient}(\omega_\alpha, \omega_\beta) \cdot \tau(\omega_\beta \rightarrow \omega_\alpha)$$

### Finite Flux Condition
$$\Phi_\alpha := \sum_{\beta \in CSI(\alpha)} ||NavT(\omega_\alpha, \omega_\beta)|| < \infty$$

### Bounded Decay Condition
$W_{CSI}(\alpha, \beta)$ must be nonnegative, bounded, and decay or truncate sufficiently to prevent unbounded aggregate flux.

### Admissibility Embedding
$\Pi_{A_\alpha}(T_\alpha)$ must remain defined or explicitly fail into a preserved boundary/failure mode.

## Context & Objectives
Aggregate transport $T_\alpha$ is the driver for process continuation $\delta$. For this to be well-posed, the summation over the Causal Sphere of Influence ($CSI$) must be bounded. This law defines the requirements for $T_\alpha$ to remain finite and admissible.

The primary objectives are:
- **Convergence:** Establish the necessity of finite flux $\Phi_\alpha$ for any valid continuation.
- **Kernel Control:** Define requirements for the weighting kernel $W_{CSI}$ to ensure it properly decays or truncates the contribution of distant or weakly-coupled processes.
- **Constraint Integration:** Ensure the aggregate vector $T_\alpha$ remains a valid input for the admissibility projection $\Pi_A$.
- **Failure Visibility:** Preserving cases where flux diverges ensures that the framework does not "leak" unphysical global closure claims.

## Law Conditions
1. **CSI domain explicit:** The set of contributing processes must be identified.
2. **Summation index beta explicit:** The summation is over $\beta \in CSI(\alpha)$.
3. **CSI weighting explicit:** $W_{CSI}$ defines the contribution of each pair.
4. **Orientation kernel explicit:** $K_{orient}$ incorporates relational compatibility.
5. **Finite flux condition explicit:** The sum of magnitudes must be bounded.
6. **Decay or truncation condition explicit:** Mechanisms to ensure convergence must be present.
7. **Projection into A_alpha required or failure preserved:** $T_\alpha$ must satisfy the domain requirements of $\Pi_A$.
8. **No global convergence claim:** No assumption that the sum converges for all possible process configurations.

## Failure Modes to Preserve
- **Unbounded CSI Summation:** Divergence due to lack of decay or infinite $CSI$.
- **Transport Flux Divergence:** Numerical overflow in the accumulation of $T_\alpha$.
- **Weighting Kernel Collapse:** Loss of influence due to over-aggressive truncation.
- **Orientation Kernel Overconstraint:** Zeroing out all contributions.
- **Hidden Global Convergence Claim:** Assuming convergence without checking local conditions.
- **Projection Failure after Transport:** $T_\alpha$ lying in a region where $\Pi_A$ is undefined.
- **Nonlocal Transport Fragmentation:** Incoherent aggregate behavior.
- **Physics Claim Leakage:** Treating this summation as a physical field integral.

## Next Steps
Following the bounding of aggregate transport, the law program will address the behavior of transitions at the admissibility boundary (LAW-005).
