# Appendix F: Known Missing Definitions and Open Bridges

This appendix tracks the formal status of critical gaps identified during the drafting of this textbook. Items are categorized by their current status in the project registries.

### 1. Provisional / Scratch Defined
These items have candidate formalisms in the "Scratch Schema" (MS-SCRATCH-V1) or "Ordered Account" (Unity Math) but require canonical promotion.

- **Formal operational definition of $\mathcal{E}$:** Defined as mismatch functional $\mathcal{E} : \mathcal{X}\times\mathcal{C}\to \mathbb{R}_{\ge 0}$ [Source: MS-SCRATCH-V1 Sec 2.1].
- **Formal structure of $\mathcal{S}$ and $\mathcal{R}$:** Defined as state space $\mathcal{X}$ and residue carrier $\mathcal{R}$ [Source: MS-SCRATCH-V1 Sec 1.1, 4.1].
- **Update Law for $\Psi$:** Defined as $R_{t+1} = \Psi(R_t, x_t, x_{t+1}, \omega_t, \Pi_A)$ [Source: Unity Math Sec 2.2].
- **Definition of $\text{Arb}_A$:** Defined as selection rule $S$ pruning candidates [Source: MS-SCRATCH-V1 Sec 5.2].
- **Definition of $O^*$:** Defined as the mismatch-minimizing selection set $O^*(x;c)$ [Source: MS-SCRATCH-V1 Sec 7.3].
- **Formal definition of $\iff_m$:** Defined as measurement map $\mathrm{Meas} : \mathcal{X}\times\mathcal{C}\to \mathbb{R}^d$ [Source: MS-SCRATCH-V1 Sec 8.1].
- **Orientation Update Rule:** Defined via "Switching Events" and the switching stability predicate [Source: MS-SCRATCH-V1 Sec 7.5].

### 2. High-Priority Gaps (GAP_OPEN)
These items remain unsettled and are the primary targets for future induction and research runs.

- **Topology-to-Geometry Transform:** The operator that maps braid group invariants ($B_K$) to metric properties. (Ref: 11.3, 11.5)
- **Empirical Mapping Standards:** Mapping framework metrics ($\Omega_a$, $B_K$) to physical constants ($G, h, c$). (Ref: 12.5)
- **Formal definition of $\otimes$:** The composition and interference rules for composite directional coupling. (Ref: 9.1, 9.4)
- **Formal definition of $\iff_s$:** The exact mapping between mismatch intensity and statistical realization. (Ref: 7.3)

### 3. Open Theoretical Questions
- **Selection Uniqueness:** Does the process support selection degeneracy? (Discussed in MS-SCRATCH-V1 as set-valued $O^*$).
- **Residue Decay:** Does $R$ persist indefinitely? (Requirement for $\Psi$ [Source: Unity Math Sec 2.2]).
- **Asymmetry vs. Symmetry:** Rigorous proof that asymmetry generates orientation.

---
**Status:** Items in Section 1 are awaiting promotion to the Canonical Lexicon. Items in Section 2 are marked as **GAP_OPEN** in the lexicon gap queue.
