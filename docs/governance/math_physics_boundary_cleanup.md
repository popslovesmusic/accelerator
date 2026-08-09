# Math-Physics Boundary Cleanup

This note records the cleanup rule in `MPF_CLEANUP_MATH_PHYS_BOUNDARY_001`.

It does not reorganize the SSOT. It clarifies routing, claim boundaries, and retrieval behavior between mathematics-facing and physics-facing material.

## Purpose

The purpose of this cleanup is to prevent:
- formal derivations from being read as physical claims,
- physical interpretations from being mistaken for mathematical theorems,
- failed physics mappings from being treated as failures of the formal calculus,
- retrieval systems from blending formal and empirical material without scope markers.

## Department Boundary

### Mathematics Department
Role:
Define and derive formal structure.

May claim:
- formal syntax,
- definitions,
- axioms,
- operators,
- lemmas,
- theorems,
- proofs,
- internal consistency,
- formal admissibility,
- formal closure.

May not claim without physics routing:
- physical reality,
- empirical validation,
- experimental prediction,
- particle identity,
- field identity,
- cosmological interpretation,
- energy interpretation.

### Physics Department
Role:
Interpret formal structure as a possible physical model.

Depends on:
- global core,
- mathematics department,
- claim governance.

May claim:
- physical interpretation,
- model correspondence,
- observable mapping,
- prediction,
- comparison to known physics,
- experimental proposal,
- validation status.

Must not:
- change core ontology,
- introduce new primitives by physical terminology,
- promote analogy to empirical proof,
- treat formal consistency as physical confirmation.

## Routing Policy

- Formal questions route to mathematics.
- Physical-meaning questions route to physics.
- Cross-domain questions retrieve the global core first and then the local department.
- Ambiguous questions must be answered with explicit claim class and department scope.

## Retrieval Policy

Required retrieval metadata:
- `department`
- `layer`
- `claim_class`
- `source_document`
- `ssot_location`
- `interpretation_status`
- `cross_reference_permissions`

Math chunks should be excluded from empirical-validation answers unless a physics correspondence rule is separately retrieved.

Physics chunks must declare:
- a math dependency,
- a correspondence rule,
- a claim class.

## Answer Policy

- When formal: state what the calculus defines or derives.
- When physical: state that the item is a physics interpretation of the formal structure.
- When uncertain: mark as provisional and prevent promotion.

Required phrase for physics-facing interpretive answers:

`Within the Physics Department interpretation...`

## Promotion Guard

- Formal derivation to physics claim: blocked without correspondence rule.
- Physics interpretation to empirical result: blocked without evidence.
- Analogy to identity: blocked.
- Successful model to universal truth: blocked.
