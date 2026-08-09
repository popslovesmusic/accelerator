# Proof Artifact: aRT Closure Preservation Lemma

**Proof ID:** P_ART_001
**Lemma ID:** MT-ART-001
**Target:** aRT Closure Preservation Lemma
**Classification:** LOCAL_LEMMA
**Status:** FORMAL_PROCEDURAL_ONLY

## 1. Lemma Statement
If an aRT satisfies its declared membership, distinction-preservation, admissible-ordering, and closure-support conditions, then an admissible update to one or more member RTs preserves aRT status provided those conditions remain satisfied after the update.

## 2. Formal Skeleton
* **Let** $A$ be an aRT defined by $aRT(S)$ over member set $S$.
* **Let** $Update(A)$ produce $A'$ with updated member set $S'$.
* **Assume** $distinction\_preservation(A')$ holds.
* **Assume** $admissible\_ordering(A')$ holds.
* **Assume** $closure\_support(A')$ holds (i.e. $C_{aRT}(S') \neq \emptyset$).
* **Then** $A'$ remains a lawful aRT.

## 3. Structural Preservation Steps

**Step 001: Expand aRT definition.**
A lawful $aRT(S)$ requires:
1. $RT_i \in S \implies Lawful(RT_i)$
2. Typed nonzero distinction preserved across participation.
3. Admissible ordering defined.
4. Shared closure support $C_{aRT}(S) \neq \emptyset$.

**Step 002: Assume Admissible Member Update.**
Let $Update(A)$ be an admissible transformation that maps $S \to S'$. By definition of an admissible update over member RTs, the operation does not introduce undefined operands.

**Step 003: Show distinction preservation remains satisfied.**
By the assumption $distinction\_preservation(A')$, the update maps distinction states to valid distinction states without total distinction collapse. Thus, $Failure\_Rule\_1$ (distinction collapse) is not triggered.

**Step 004: Show admissible ordering remains satisfied.**
By the assumption $admissible\_ordering(A')$, there remains a valid relational ordering over $S'$. Thus, $Failure\_Rule\_2$ (ordering collapse) is not triggered.

**Step 005: Show closure support remains satisfied.**
By the assumption $closure\_support(A')$, there exists non-empty $C_{aRT}(S')$. Thus, $Failure\_Rule\_3$ (closure-support loss) and $Failure\_Rule\_5$ (topology fracture) are not triggered.

**Step 006: Conclude membership conditions remain true.**
Because the admissibility conditions of the framework act as filters, any update that maintains distinction, ordering, and closure support inherently prevents admissibility collapse ($Failure\_Rule\_4$).

**Step 007: Conclude resulting structure.**
Since all conditions of Formal Principle 1.2.2C.1 are satisfied and no condition of Formal Candidate 1.2.2C.5 (Failure Rule) is triggered, $A'$ must be a lawful aRT.

## 4. Required Failure Analysis
* **FAIL_ART_001 (distinction collapse):** Blocked by explicit precondition assumption $distinction\_preservation(A')$.
* **FAIL_ART_002 (ordering collapse):** Blocked by explicit precondition assumption $admissible\_ordering(A')$.
* **FAIL_ART_003 (closure-support loss):** Blocked by explicit precondition assumption $closure\_support(A')$.
* **FAIL_ART_004 (admissibility collapse):** Prevented because closure-support requires admissibility limits to be respected. Without admissibility, $C_{aRT}(S')$ would necessarily be empty.

## 5. Conclusion
This lemma formally proves that aRT preservation is a strict consequence of the continuation of its necessary formal conditions, avoiding hidden assumptions of persistent identity without formal grounding. The claim is restricted to FORMAL_PROCEDURAL_ONLY.
