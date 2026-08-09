# Lemma L108 — Ontological Classification of Arrays

## 1. Statement
Every array structure used within process-formalisms, updates, or simulation claims must be explicitly classified into one of four dynamic process-ontological types:
1. **Conditional Array:** Represents the local legality landscape (admissibility windows $\mathcal{A}_\alpha$).
2. **Projection Array:** Represents application-facing representation layers ($QM_{\text{app}}$, $GR_{\text{app}}$ layouts).
3. **Residue Array:** Represents accumulated constraint history (residue carrier $\mathcal{R}$).
4. **Participation Array:** Represents active coupling neighborhoods ($CSI(\alpha)$).

The default classification "state array" is strictly forbidden, as it introduces snapshot/substance ontology assumptions (hidden clocks or mutable objects) into the process-ontology framework.

## 2. Dependencies
- `L027`: Relational Orientation Array
- `L043`: Tertiary Node Structure ($I, O, R$ Partitioning)

## 3. Proof Sketch
By `L027` and `L043`, persistent process structures are projections of underlying relations, not static state containers. If array structures (such as simulation lattices or memory blocks) are treated as generic state arrays, they introduce hidden clock updates, coordinate geometry, or mutable object ownership by default (ontology leakage). Stratifying arrays into conditional, projection, residue, and participation types forces all array operations to be defined in terms of dynamic process relations (e.g. admissibility filtering, residue updates, or neighborhood accessibility). This preserves the monistic process ontology under recursion.

## 4. Status
provisional
