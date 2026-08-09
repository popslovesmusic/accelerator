# Proof Strength Classification Registry (MPF-RPCR-008)

## 1. Purpose
Classify each MT candidate by proof strength without promotion inflation, ensuring that local derivation status remains strictly governed and non-physical.

## 2. Classification Levels
### 2.1 NOT_REVIEWED
- Candidate exists but has not undergone RPCR audit.

### 2.2 REVIEW_BLOCKED
- Review is halted due to missing dependencies or critical drift.

### 2.3 COUNTEREXAMPLE_ACTIVE
- Candidate is contested by one or more active counterexamples.

### 2.4 SUPPORTED_UNDER_ASSUMPTIONS
- Candidate is derivable only if explicitly declared assumptions are granted.

### 2.5 LOCAL_PROOF_CANDIDATE
- Candidate has satisfied all proof obligations within a restricted neighborhood.

### 2.6 READY_FOR_FORMAL_PROOF_REVIEW
- Candidate has passed stress-testing and is ready for formal review.

## 3. Forbidden Escalations
- **PROVEN**: Blocked until formal series closure.
- **PHYSICALLY_VALIDATED**: Formally prohibited.
- **GLOBAL_THEOREM**: Extension to global domains is prohibited.
- **UNIFICATION_SUPPORT**: Use as evidence for QM/GR unification is prohibited.

## 4. Governance Status
- **Theorem Status**: PROOF_CANDIDATE_REVIEW_ONLY
- **Series Status**: RESTRICTED_LOCAL_THEOREM_REVIEW
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 5. Governance Rules
- **PSC-RULE-001**: No candidate may bypass the classification hierarchy.
- **PSC-RULE-002**: Promotion requires satisfaction of all lower-level preconditions.

## 6. Forbidden Claims
- Classification level represents the 'truthfulness' of the framework.
- Ready for review status justifies physical substrate claims.
- Counterexample active status can be bypassed.

## 7. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
