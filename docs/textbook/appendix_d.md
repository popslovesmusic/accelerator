# Appendix D: Claim-Level Governance

This appendix summarizes the standards for classifying and promoting research claims within the framework.

### Classification Table
| Level | Name | Scope | Requirements |
| :--- | :--- | :--- | :--- |
| **C0** | Definition | Internal notation | Definition only. |
| **C1** | Model-Relative | Inside a scaffold | Logical consistency within a specific model. |
| **C2** | Simulation-Observed | Result of a run | Recoverable output + documented config/seed. |
| **C3** | Structural Comparison | Analogy/Resemblance | Comparison to external theory (e.g., "gravity-like"). |
| **C4** | Supported Internal | Multi-Model support | 2+ Mechanism Classes, 3+ Seeds, Falsification passed. |
| **C5** | Validate | External Alignment | Independent measurement, 4+ Falsification Vectors. |
| **C6** | Theorem | Formal Closure | Universal mechanism independence, formal proof. |

### Validation Mandates
1. **Falsification Vector (FV):** A targeted test designed to force a failure of the claim. A claim cannot reach C4 without passing at least two FVs.
2. **Mechanism Class Independence:** A claim is mechanism-independent if its behavior is reproduced by tools with different governing update rules (e.g., CA vs. PDE).
3. **Humility Prefix:** All conclusions for C1-C4 claims must begin with: **"Within these models..."** or **"Within this framework..."**.
4. **Residue Labels:** Any result that depends on a provisional operator or missing definition must be marked with a **residue label** (e.g., "[Residue: Provisional Arb_A]").

### Promotion and Downgrade Rules
- **Promotion:** Requires an evidence pack containing raw data, analysis, and falsification reports.
- **Downgrade:** Any failed falsification or contradictory measurement from an independent model class triggers an automatic downgrade to **NOT\_SUPPORTED** or **INCONCLUSIVE**.
- **Contradiction:** If a C4 simulation result contradicts a C6 theorem, the C6 status is suspended (moved to **CONTESTED**) until the derivation is re-audited.
