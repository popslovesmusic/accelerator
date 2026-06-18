# Proof Artifact: otimes Non-Identity Composition Lemma

**Proof ID:** P_OTIMES_001
**Lemma ID:** MT-OTIMES-001
**Target:** otimes Non-Identity Composition Lemma
**Classification:** LOCAL_LEMMA
**Status:** FORMAL_PROCEDURAL_ONLY

## 1. Lemma Statement
If $X$ and $Z$ are typed lawful process operands and $X \otimes_Y Z$ is defined under context $Y$, then the composition creates a lawful typed coupling without implying $X = Z$, $X = X \otimes_Y Z$, or $Z = X \otimes_Y Z$, unless a separate identity-preserving rule is explicitly declared.

## 2. Formal Skeleton
* **Let** $X$ and $Z$ be typed operands (e.g., RT, aRT).
* **Let** $Y$ be a declared composition context mapping the coupling.
* **Assume** $X \otimes_Y Z$ is defined (i.e. operands are contextually compatible).
* **Assume** distinction preservation: $D(X|Z) > \epsilon$.
* **Assume** admissibility non-empty: $\delta_a(X \otimes_Y Z) \neq \emptyset$.
* **Assume** closure-class compatibility under $Y$.
* **Then** $X \otimes_Y Z$ is a typed coupling structure.
* **And** the result does not imply $X = Z$, nor $X = X \otimes_Y Z$, nor $Z = X \otimes_Y Z$.

## 3. Structural Preservation Steps

**Step 001: Expand the otimes definition.**
$\otimes$ is a typed partial composition operator. It requires:
1. Typed operands $X$ and $Z$.
2. A governing context $Y$ defining the interaction constraints.

**Step 002: Show requirement of typed operands and declared composition context.**
If $X$ or $Z$ lack type definitions, or if $Y$ is undeclared, the partiality condition of $\otimes$ renders the expression $X \otimes_Y Z$ undefined.

**Step 003: Distinction preservation firewall.**
By assumption, $D(X|Z) > \epsilon$. This explicit difference bounds the operands from equivalence. Therefore, the relation cannot collapse to $X = Z$.

**Step 004: Apply the typed coupling rule.**
Under context $Y$, the coupling forms a new hierarchical expression $X \otimes_Y Z$. By the axioms of relational extension, the operands $X$ and $Z$ become participation components within the structure, distinguishing them structurally from the composite itself.

**Step 005: Apply the anti-reification rule.**
The resulting composition $X \otimes_Y Z$ cannot be simplified via scalar multiplication, nor does it denote physical fusion. Untyped algebraic joining is explicitly forbidden by the framework. The composition merely specifies relational participation.

**Step 006: Conclude distinct preservation.**
Thus, a lawful composition preserves role distinction. The composed structure $X \otimes_Y Z$ retains $X$ and $Z$ as constituents without establishing equivalence among them. Without a declared identity rule, no implicit equivalences are licensed.

## 4. Required Failure Analysis
* **FAIL_OTIMES_ID_001 (operand typing missing or invalid):** Handled by the partiality of $\otimes$; composition is undefined.
* **FAIL_OTIMES_ID_002 (D(X|Z) <= epsilon):** Results in distinction collapse. The identity firewall fails because the operands are indistinguishable. Thus, bounded by the assumption $D(X|Z) > \epsilon$.
* **FAIL_OTIMES_ID_003 (closure-class compatibility absent):** The context $Y$ rejects the coupling. The typed coupling is unsupported.
* **FAIL_OTIMES_ID_004 (composition result treated as scalar product):** Explicitly prevented by the anti-reification rule. Illegal reification is not licensed.
* **FAIL_OTIMES_ID_005 (projection equivalence used as process identity):** Denied by the distinction between statistical/projected mapping and process identity. Trace-priority violation.
* **FAIL_OTIMES_ID_006 (unproven commutativity or associativity assumed):** $\otimes$ defaults to non-commutative. Unproven associativity is an illegal algebraic strengthening explicitly prohibited here.

## 5. Conclusion
This lemma establishes the strict non-identity conditions for $\otimes$ composition. It constructs an explicit firewall against algebraic overreach (e.g. implicit fusion or scalar products), ensuring structured interaction does not collapse distinction. The claim is restricted to FORMAL_PROCEDURAL_ONLY.
