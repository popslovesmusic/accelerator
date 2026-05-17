# Admissibility Space Registry (MPF-FSUB-003)

## 1. Purpose
Define admissibility sets, admissibility distance or constraint measure, admissible image, and boundary behavior.

## 2. Definitions
### 2.1 A_alpha: Local Admissibility Set
- **Symbol**: $A_\alpha$
- **Role**: Local admissibility set or constraint region.
- **Definition**: The subset of state space satisfying local continuation constraints.
- **Locality**: `STRICTLY_LOCAL`.

### 2.2 d_A: Admissibility Distance
- **Symbol**: $d_A$
- **Role**: Candidate admissibility distance / violation measure.
- **Definition**: A measure of the distance of a state from the nearest admissible configuration.
- **Locality**: `STRICTLY_LOCAL`.

### 2.3 Im_A: Admissible Image
- **Symbol**: $Im_A$
- **Role**: Admissible image under projection.
- **Definition**: The projection of the local admissibility set into an observable domain.
- **Locality**: `PROJECTED`.

### 2.4 boundary_A: Admissibility Boundary
- **Symbol**: $boundary\_A$
- **Role**: Finite local admissibility boundary.
- **Definition**: The limit set of the admissibility region where continuation risk is critical.
- **Locality**: `STRICTLY_LOCAL`.

## 3. Mandatory Rules
- **AS-RULE-001**: Admissibility is local unless explicitly marked otherwise.
- **AS-RULE-002**: Non-empty admissible image (MT-003) is a theorem target, not an assumption.
- **AS-RULE-003**: Boundary behavior must explicitly include failure cases (e.g., orientation locking).

## 4. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Series Status**: FORMAL_SUBSTRATE_SCAFFOLD
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 5. Governance Rules
- **AS-RULE-004**: All admissibility objects must maintain NON_PHYSICAL and ANALOG_ONLY status.

## 6. Forbidden Claims
- Admissibility sets prove physical existence.
- Admissibility distance derives physical force laws.
- Boundary behavior justifies universal unification.

## 7. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
