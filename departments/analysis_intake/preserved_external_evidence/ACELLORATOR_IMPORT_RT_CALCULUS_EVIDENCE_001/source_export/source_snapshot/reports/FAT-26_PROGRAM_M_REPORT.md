# Program M Falsification Report: FAT-26

## 1. Native Dependency Analysis

* **M1 (Reference without Orientation):** Symmetry Reference >S< remains unexpressed and lacks computational meaning without left/right orientation roles.
* **M2 (Orientation without Reference):** Orientation roles left/right collapse and are undefined without a declared symmetry reference.
* **M3 (Capacity without Orientation):** Distinction capacity remains unrealized.
* **M6 (Construction Permutation):** Non-commutative. Only the order:
  $$ I1 \to I2 \to I3 $$
  (Symmetry Reference $\to$ Orientation Roles $\to$ Distinction Capacity) generates a realizable computational triplet.
* **M7 (Pairwise Sufficiency):** No proper subset can generate the full triplet.
* **M12 (Primitive Status):** Triplet $T_R$ is the primitive; I1, I2, and I3 are OTM aspects rather than independent primitives.

## 2. Invariant Mutual Dependency Graph

The invariants form a mutually dependent closed loop under the whole expression:
$$ I1 \leftrightarrow I2 \leftrightarrow I3 $$
