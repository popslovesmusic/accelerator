# Equivalence Relation Registry (MPF-FSUB-004)

## 1. Purpose
Define restricted equivalence relations used in MT-001, MT-002, and later local theorem candidates.

## 2. Equivalence Relations
### 2.1 Projection Equivalence
- **Relation ID**: `projection_equivalence`
- **Definition**: Two preimages are equivalent if they map to the same projected image $Im_A$.
- **Preserved**: observable image, admissibility status.
- **Discarded**: internal distinction detail.

### 2.2 Transport Equivalence
- **Relation ID**: `transport_equivalence`
- **Definition**: Two states are equivalent if they preserve relational identity under $NavT$ transport.
- **Preserved**: relational identity, orientation frame.
- **Discarded**: absolute coordinate, path history.

### 2.3 Trace Equivalence
- **Relation ID**: `trace_equivalence`
- **Definition**: Two artifacts are equivalent if they trace back to the same source-relation aspect role.
- **Preserved**: source pointer, non-separability metadata.

### 2.4 Residue Compatibility
- **Relation ID**: `residue_compatibility`
- **Definition**: Two residue states are equivalent if they provide the same admissibility-conditioning capability.

### 2.5 Orientation Compatibility
- **Relation ID**: `orientation_compatibility`
- **Definition**: Two orientation states are equivalent up to declared frame/deviation tolerance.

## 3. Mandatory Constraints
- **EQ-CON-001**: Equivalence is local and declared.
- **EQ-CON-002**: Equivalence does not imply identity.
- **EQ-CON-003**: Equivalence does not imply ontology sameness.

## 4. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Series Status**: FORMAL_SUBSTRATE_SCAFFOLD
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 5. Governance Rules
- **EQ-RULE-001**: Every equivalence relation must explicitly declare preserved and discarded features.
- **EQ-RULE-002**: Equivalence mappings remain strictly within the LOCAL_RESTRICTED_DOMAIN.

## 6. Forbidden Claims
- Formal equivalence proves physical identity.
- Equivalence relations derive universal symmetry laws.
- Relational equivalence eliminates projection loss.

## 7. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
