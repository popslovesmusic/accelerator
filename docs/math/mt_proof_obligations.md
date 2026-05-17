# Proof Obligation Registry for MT Series (MPF-RPCR-002)

## 1. Purpose
Create explicit proof obligations for MT-001, MT-002, and MT-003 from FSUB dependencies to prepare for restricted local theorem-candidate work.

## 2. MT-001: Π_A Restricted Projection Idempotence
- **Target**: Derive $\Pi_A \circ \Pi_A \sim \Pi_A$.
- **Obligations**:
  - `MT-001-OB-01`: Formally define $\Pi_A$ application over $X_\alpha \times A_\alpha$.
  - `MT-001-OB-02`: Derive equivalence under `projection_equivalence`.
  - `MT-001-OB-03`: Identify stable neighborhood conditions for convergence.
- **Failure Criteria**: Non-idempotent stable neighborhood counterexample.

## 3. MT-002: NavT Restricted Transport Identity
- **Target**: Derive restricted identity behavior for transport.
- **Obligations**:
  - `MT-002-OB-01`: Declare formal orientation-space $\Omega_\alpha$ and transport equivalence.
  - `MT-002-OB-02`: Derive conditions for preserving relational identity across indices.
  - `MT-002-OB-03`: Map orientation locking failures to transport identity breakdown.
- **Failure Criteria**: Relational identity collapse during bounded traversal.

## 4. MT-003: δ Non-Empty Admissible Image
- **Target**: Prove $\delta(Im_A) \neq \emptyset$ under non-null mismatch.
- **Obligations**:
  - `MT-003-OB-01`: Formalize $\delta$ selection semantics.
  - `MT-003-OB-02`: Prove $\mathcal{E} \neq 0$ and $A_\alpha$ imply non-empty $Im_A$.
  - `MT-003-OB-03`: Establish tie-breaking policy for degeneracy.
- **Failure Criteria**: Actualization gap (undefined $\delta$) despite pressure.

## 5. Governance Status
- **Theorem Status**: PROOF_CANDIDATE_REVIEW_ONLY
- **Series Status**: RESTRICTED_LOCAL_THEOREM_REVIEW
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 6. Governance Rules
- **OB-RULE-001**: Every proof obligation must remain traceable to the FSUB formal substrate.
- **OB-RULE-002**: Obligations are considered 'satisfied' only after formal review.

## 7. Forbidden Claims
- Obligation mapping proves the theorem's validity.
- Targeted theorems derive physical laws.
- Failure criteria derive physical entropy.

## 8. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
