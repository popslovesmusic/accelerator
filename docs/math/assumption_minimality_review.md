# Assumption Minimality Review (MPF-FRPR-007)

## 1. Purpose
Determine whether MT proof attempts rely on unnecessary, hidden, or over-strengthened assumptions to ensure restricted local derivation integrity.

## 2. Review Requirements
### 2.1 Hidden Globality
- **Check ID**: `hidden_globality`
- **Definition**: Search for universal assumptions (e.g., "for all $x$") that lack neighborhood restrictions.

### 2.2 Hidden Identity
- **Check ID**: `hidden_identity`
- **Definition**: Verify no step treats equivalence ($\sim$) as literal identity ($=$).

### 2.3 Undeclared Equivalence
- **Check ID**: `undeclared_equivalence`
- **Definition**: Ensure every check uses a registered equivalence relation.

### 2.4 Implicit Closure
- **Check ID**: `implicit_closure`
- **Definition**: Detect claims of self-completion or total recoverability.

### 2.5 Assumption Redundancy
- **Check ID**: `assumption_redundancy`
- **Definition**: Identify assumptions derivable from FSUB objects.

### 2.6 Assumption Strengthening
- **Check ID**: `assumption_strengthening`
- **Definition**: Detect assumptions broadened beyond candidate-review grants.

## 3. Governance Status
- **Theorem Status**: LOCAL_PROOF_REVIEW_ONLY
- **Series Status**: RESTRICTED_FORMAL_PROOF_CONSTRUCTION
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 4. Governance Rules
- **AMR-RULE-001**: Every proof attempt must pass the assumption minimality review.
- **AMR-RULE-002**: Over-strengthening triggers immediate proof-blocked status.

## 5. Forbidden Claims
- Assumption minimality proves that the theorem is 'universal'.
- Derivable assumptions justify physical substrate properties.
- Hidden globality is acceptable if the local result is 'strong'.

## 6. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
