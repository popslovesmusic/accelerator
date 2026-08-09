# L058 — Orientation-Driven Ordering and the Elimination of Primitive Time

## Statement
Primitive time is not a fundamental variable of the Mono-Process Framework. It is replaced by **Admissible Continuation Ordering** ($\prec$). A process state $x'$ is "later" than $x$ ($x \prec x'$) if and only if $x'$ is reachable from $x$ through a sequence of local orientation-driven update steps. 
Formally, ordering emerges from the application of the global **Orientation Array** $I = \{-(i)_\alpha\}$, which maps local deviation pressure ($\varepsilon$) and residue ($R$) to admissible continuation directions ($\omega$).

## Dependencies
- Definitions: `orientation_array` ($I$), `local_orientation_operator` ($-(i)_\alpha$), `admissible_continuation_ordering` ($\prec$)
- Assumptions: No global master equation or universal time exists; dynamics are strictly local and path-dependent.
- Prior lemmas: L057 (Unified Admissibility), L033 (Relational Array), L042 (Directional Distinguishability Asymmetry).

## Proof sketch
1. From the MASRE constraint, no global potential $V$ exists such that $\partial_t u = -\delta u / \delta V$. This eliminates universal time and total ordering of states.
2. Define local ordering purely by admissible continuation: $x \prec x' \iff x' \in A(x; R, K)$.
3. The global orientation structure is an array of local operators $I = \{-(i)_\alpha\}$. Each local operator $-(i)_\alpha : (\varepsilon_\alpha, R_\alpha) \mapsto \omega_\alpha$ outputs an admissible orientation.
4. The local update rule $x'_\alpha = x_\alpha + \Pi_{A_\alpha}(\omega_\alpha)$ actualizes the next state in the ordering.
5. Ordering is the realized path under the orientation field. Since residue $R$ evolves non-commutatively ($R_{t+1} \neq R_t$), the ordering direction (arrow of ordering) is path-dependent.
6. Therefore, time is an emergent projection of the stabilized continuation ordering under the orientation array.

## Status
draft

## Supersedes / Superseded-by
- **Supersedes:** None (New core formalization).
- **Notes:** This lemma formally eliminates primitive time as per the SPM TECH NOTE "Orientation-Driven Continuation and the Elimination of Primitive Time".
