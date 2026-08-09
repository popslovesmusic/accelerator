# Operator Signature Hardening (MPF-FSUB-005)

## 1. Purpose
Declare formal domains, codomains, preconditions, postconditions, and failure modes for core operators to prepare for local theorem work.

## 2. Hardened Signatures
### 2.1 Pi_A: Admissibility Projection
- **Symbol**: $\Pi_A$
- **Domain**: $X_\alpha \times A_\alpha$
- **Codomain**: $Im_A$
- **Preconditions**: $A_\alpha$ is non-empty, residue consistency.
- **Postconditions**: output $\equiv$ input under `projection_equivalence`.
- **Target Theorem**: MT-001 (Projection Idempotence).

### 2.2 NavT: Bounded Relational Transport
- **Symbol**: $NavT$
- **Domain**: $X_\alpha \times \Omega_\alpha$
- **Codomain**: $X_\beta \times \Omega_\beta$
- **Preconditions**: neighborhood accessibility, frame compatibility.
- **Postconditions**: relational identity preservation.
- **Target Theorem**: MT-002 (Transport Identity).

### 2.3 delta: Constrained Selection
- **Symbol**: $\delta$
- **Domain**: $X_\alpha \times A_\alpha \times R_\alpha$
- **Codomain**: $\delta\_space_\alpha$
- **Preconditions**: mismatch non-null ($\mathcal{E} \neq 0$), selection rule active.
- **Postconditions**: event is admissible within $Im_A$.
- **Target Theorem**: MT-003 (Non-empty Admissible Image).

### 2.4 CSI: Bounded Local Accessibility
- **Symbol**: $CSI$
- **Domain**: $\alpha \times restricted\_reach$
- **Codomain**: $CSI_\alpha$
- **Failure Modes**: reach overflow, neighborhood discontinuity.

### 2.5 minus_i: Local Orientation Reference
- **Symbol**: $-(i)$
- **Domain**: $\Omega_\alpha$
- **Codomain**: $A_{\alpha, ref}$
- **Failure Modes**: reference locking, unauthorized symmetry breaking.

## 3. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Series Status**: FORMAL_SUBSTRATE_SCAFFOLD
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 4. Governance Rules
- **OSH-RULE-001**: Every operator application must satisfy its declared preconditions.
- **OSH-RULE-002**: Failure to satisfy postconditions triggers mandatory failure-mode logging.

## 5. Forbidden Claims
- Hardened signatures prove physical interaction.
- Operator domains represent physical spacetime manifolds.
- Postcondition satisfaction derives physical conservation.

## 6. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
