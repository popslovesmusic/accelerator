# Program S Falsification Report: FAT-26

## 1. Mathematical Dependency Analysis

* **S1 (Functional Dependency):** No single invariant can be derived as a function of the other two.
* **S2 (Matroid Independence):** The invariants are dependent under ternary pointed closure.
* **S4 (Non-Commutative Construction):** Changing the construction order in pointed relational structures alters the resulting structure.
* **S5 (Whole-Relation Countermodel):** Confirmed. Two structures can preserve the same isolated invariant values but differ in ternary organization.
* **S7 (Circular Definition Audit):** The definitions of Symmetry Reference, Roles, and Capacity are mutually recursive but well-founded.

## 2. Representation Losses

Reducing the pointed ternary structure $T_R$ to independent scalar invariants erases the reference-centered structure.
