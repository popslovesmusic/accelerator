# Lexicon Detailed Audit v3 (2026-05-09T15:33:41.874567+00:00)

## Summary
- Canonical terms (unique): 953
- Alias entries: 824
- Gap queue entries: 41 (GAP_OPEN: 15)
- Validation registry terms: 53; roles: 72

## Built-in audit (scripts/lexicon_audit.py)
- Status: FAILED
- Errors: 1
- Missing charter-compliance terms: projection, Psi, observable
- Warnings: 8

## Charter-required terms (from lexicon_audit failure)
- projection: in_canonical=True, in_validation_registry=False
- Psi: in_canonical=True, in_validation_registry=False
- observable: in_canonical=True, in_validation_registry=False

## Alias integrity
- Alias targets missing from canonical: 0
- Aliases that collide with canonical term names: 795

## Gap queue
- Status counts: {"BLOCKED_PRIMITIVE": 1, "CHARTER_VERIFIED": 8, "EVIDENCE_L2": 4, "GAP_OPEN": 15, "MARK_AS_SURFACE_METAPHOR": 1, "RESOLVED_L1": 5, "RESOLVED_PENDING_PROMOTION": 2, "RESOLVED_TO_ALIAS": 3, "RESOLVED_TO_CANONICAL": 2}
- GAP_OPEN sample terms: Aligned Asymmetry, Relational Cluster, Symmetric Collapse, Mutually Stabilized Continuation, Existence Scalar, Residue-Conditioned Biconditional, Admissibility Window, Admissibility Projection, Coupling Neighborhood, Transport Operator, Mismatch-Minimizing Selection, Transport Residual Observable, Admissibility Outcome, Residue Update Operator, Residue Space

## Validation coverage
- Canonical terms missing validation entry: 936
- Role status counts: {"L0": 33, "L1": 5, "L2": 15, "L3": 19}

## Artifacts
- JSON: reports/lexicon_detailed_audit3_20260509_113341.json
- MD: reports/lexicon_detailed_audit3_20260509_113341.md
