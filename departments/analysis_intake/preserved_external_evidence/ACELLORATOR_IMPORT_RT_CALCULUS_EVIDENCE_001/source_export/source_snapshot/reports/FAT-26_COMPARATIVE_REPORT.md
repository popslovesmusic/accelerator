# FAT-26 Comparative Falsification Report

## 1. Outcome Classification

- **Primary Outcome:** **WHOLE_EXPRESSION_PRIMITIVE_SUPPORTED**
- **Ruling Details:** Agreement located: Both Program M and Program S support the alternative hypothesis that the complete reference-centered triplet is primitive under closure. The candidate invariants {Symmetry Reference, Orientation Roles, Distinction Capacity} do not exist as independent primitives but arise only as OTM-exposed aspects of the whole closed relation. Any attempt to decompose or reduce the relation to independent binary pairs or scalar invariants erases the joint ternary dependency.

## 2. Program Comparison Matrix

* **Do both identify the same dependency edges?** Yes ($I1 \leftrightarrow I2 \leftrightarrow I3$)
* **Can any pair of invariants generate the third without semantic loss?** No, proper subsets are incomplete
* **Does construction order matter?** Yes, construction order is non-commutative ($I1 \to I2 \to I3$ is the only valid order)
* **Is joint whole-triplet dependency itself an additional invariant?** Yes
* **Are I1-I3 primitives, generators, or OTM aspects?** They are OTM-exposed aspects of the whole expression.
* **Does either program find a counterexample to the FAT-25 sufficiency claim?** No, FAT-25 sufficiency survives when whole-expression dependency is preserved.

## 3. Findings

The attack campaign successfully verified that:
1. Triplet identity depends on the complete relation among symmetry reference, orientation roles, and distinction capacity.
2. The complete reference-centered triplet:
   $$ T_R := \langle O[D(A|E)]_a, >S<, O[D(A|E)]_b \rangle $$
   is an irreducible whole-expression primitive under closure.
3. The candidate invariants $I1$, $I2$, and $I3$ arise only through OTM decomposition and do not retain independent meaning when detached.
