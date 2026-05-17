# State Space Registry (MPF-FSUB-002)

## 1. Purpose
Define the spaces in which core variables live, including process state, orientation state, residue state, and local index structure.

## 2. Definitions
### 2.1 x_alpha: Local Process State
- **Symbol**: $x_\alpha$
- **Space**: $X_\alpha$
- **Informal Role**: Local process state.
- **Allowed Operations**: transport, projection, selection.
- **Forbidden Interpretations**: physical particle position, absolute coordinate.

### 2.2 omega_alpha: Local Orientation State
- **Symbol**: $\omega_\alpha$
- **Space**: $\Omega_\alpha$
- **Informal Role**: Local orientation state.
- **Allowed Operations**: minimization, alignment, rotation_analog.
- **Forbidden Interpretations**: physical spin, literal spatial orientation.

### 2.3 R_alpha: Local Residue State
- **Symbol**: $R_\alpha$
- **Space**: $R\_space_\alpha$
- **Informal Role**: Local residue state.
- **Allowed Operations**: accumulation, decay, conditioning.
- **Forbidden Interpretations**: physical mass, literal energy density.

### 2.4 alpha: Local Index
- **Symbol**: $\alpha$
- **Space**: $I_{restricted}$
- **Informal Role**: Local index over restricted finite domain.
- **Allowed Operations**: indexing, neighborhood_traversal.
- **Forbidden Interpretations**: universal coordinate index, infinite continuum.

### 2.5 CSI_alpha: Local Neighborhood
- **Symbol**: $CSI_\alpha$
- **Space**: $Neighborhood_\alpha$
- **Informal Role**: Bounded local interaction/accessibility neighborhood.
- **Allowed Operations**: coupling, reach_calculation.
- **Forbidden Interpretations**: physical force field, non-local entanglement.

## 3. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Series Status**: FORMAL_SUBSTRATE_SCAFFOLD
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 4. Governance Rules
- **SS-RULE-001**: Spaces are mathematical scaffolds for restricted analysis, not physical containers.
- **SS-RULE-002**: All state variables must explicitly acknowledge non-separability from the source relation.

## 5. Forbidden Claims
- State spaces prove the existence of physical dimensions.
- Variable stabilization derives physical matter properties.
- Indexing implies a literal discrete spacetime grid.

## 6. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
