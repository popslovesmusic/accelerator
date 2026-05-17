# Semantic Persistence Registry (MPF-RSEM-002)

## 1. Purpose
Define bounded semantic persistence classes describing when meaning remains partially recoverable under projection transformations.

## 2. Persistence Classes
### 2.1 SP_LOCAL_RECOVERABLE
- **Class ID**: `SP_LOCAL_RECOVERABLE`
- **Definition**: Meaning that remains stable within a local projection neighborhood.

### 2.2 SP_PARTIAL_TRACE
- **Class ID**: `SP_PARTIAL_TRACE`
- **Definition**: Meaning that can be partially reconstructed through source-relation trace metadata.

### 2.3 SP_CONFLICT_DEPENDENT
- **Class ID**: `SP_CONFLICT_DEPENDENT`
- **Definition**: Semantic structures whose meaning is tied to the preservation of specific projection tensions.

### 2.4 SP_DEFORMATION_SENSITIVE
- **Class ID**: `SP_DEFORMATION_SENSITIVE`
- **Definition**: Meaning that degrades rapidly under projection deformation or flattening.

### 2.5 SP_NONRECOVERABLE
- **Class ID**: `SP_NONRECOVERABLE`
- **Definition**: Semantic artifacts that have lost all recoverable link to the source relation.

## 3. Metrics Definitions
### 3.1 Meaning Trace Retention
- **Metric ID**: `meaning_trace_retention`
- **Definition**: Measures the fraction of interpretive metadata preserved after projection transformation.

### 3.2 Projection Semantic Integrity
- **Metric ID**: `projection_semantic_integrity`
- **Definition**: Evaluates whether the semantic structure respects projection-domain constraints.

### 3.3 Interpretive Stability Density
- **Metric ID**: `interpretive_stability_density`
- **Definition**: Quantifies the clustering of stable interpretations within a semantic neighborhood.

### 3.4 Semantic Loss Visibility
- **Metric ID**: `semantic_loss_visibility`
- **Definition**: Measures the explicitness of documented semantic losses or abstractions.

## 4. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 5. Governance Rules
- **SP-RULE-001**: High semantic persistence scores do not imply truth or ontology identity.
- **SP-RULE-002**: Persistence analysis must explicitly declare projection-loss visibility.

## 6. Forbidden Claims
- Semantic persistence proves that a term is 'true'.
- High stability density derives physical semantic fields.
- Meaning recovery justifies the assumption of detached observer assignation.

## 7. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
