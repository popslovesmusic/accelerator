# D-Semantics Relation Witness Foundational Draft Summary

## Scope and Purpose
This summary provides a high-level review of the candidate foundational draft specifying the semantic and algebraic structure of relation witnesses in context `C`.

---

## Established Statements
- **Obligation Status**: `OBL-D-001D` remains `OPEN_BLOCKED`.
- **Preceding Obligations**: `OBL-D-001A`, `OBL-D-001B`, and `OBL-D-001C` (type-level only) are discharged.

---

## Human-Approved Constraints
- **Witness Abstraction (DEC-SEM-001)**: `TypedWitness_C` is a semantic witness abstraction. Trace certificates, Lean proof terms, and executable artifacts are representations of the witness, not the witness itself.
- **Context Indexation (DEC-SEM-002)**: `TraceCompatible_C` is explicitly indexed by context `C`. Context-free variants are rejected.

---

## Proposals
- **Candidate Signatures**: Proposed signatures for context `C`, relation `Rel_C`, distinction `Dist_C`, representable distinction `RepDist_C`, witness typing `TypedWitness_C`, realization mapping `Realizes_C`, trace compatibility `TraceCompatible_C`, and witness transport `Transport_C`.
- **Candidate Axioms**: Proposed axioms `AX-WITNESS-REPDIST`, `AX-REALIZATION-WITNESS`, and `AX-TRANSPORT-PRESERVATION` to bridge relation witness validity to representability preservation.

---

## Rejected Alternatives
- **Context-Free Trace Compatibility**: Rejected. Trace compatibility must vary depending on admissibility thresholds and relational indices of the context.
- **Conflating Witness with Realization**: Rejected. Restricting witnesses to trace certificates or proof terms violates implementation independence.

---

## Unknowns
- **Algebraic Identity**: Intensional identity is proposed, but extensional and relational equivalence criteria remain open.
- **Composition Associativity**: Whether witness composition is associative in all admissible contexts remains unresolved.

---

## Smallest Next Task
The smallest next task is to formally register the signature of `TYPE_WITNESS_C` and the witness mapping `project_w` in the math type registry to resolve the blocker.
