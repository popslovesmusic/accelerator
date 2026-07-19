# Lemma L126 — Sign as Generative Pathway

## 1. Statement
The sign state $\text{Sign}(\Delta P)_c \in \{+, -, 0\}$ uniquely tracks the net change in relational crossings, mapping positive signs to crossing addition (accumulation) and negative signs to crossing subtraction (exclusion). The algebraic sign multiplication rules are preserved through composition of accumulation and exclusion pathways.

## 2. Dependencies
- **Overview:** [08_sign_semantics_and_generative_pathways.md](../08_sign_semantics_and_generative_pathways.md)

## 3. Proof Sketch
We establish the validity of the generative sign mapping:
1.  **Exhaustive Partitioning:**
    Since the change in the number of crossing layers $\Delta_c \text{Crossings}$ is a real value, it must be either strictly positive, strictly negative, or zero. Thus, the mapping partitions all pathway steps into $\{+, -, 0\}$ uniquely.
2.  **Algebraic Sign Preservation:**
    *   Composition of two accumulation steps ($+$ and $+$) increases crossings, mapping to $+$.
    *   Composition of an accumulation and an exclusion step ($+$ and $-$) represents opposing dynamics. Under balanced composition, the sign rules map to the net difference.
    *   For product mappings (e.g. $(-)(-) = +$), two successive exclusions of boundary-front components result in a net inward shift of the boundary-front, which is structurally equivalent to an accumulation of external crossings. Thus, the algebraic parity rules are preserved. $\blacksquare$

## 4. Status
`provisional`
