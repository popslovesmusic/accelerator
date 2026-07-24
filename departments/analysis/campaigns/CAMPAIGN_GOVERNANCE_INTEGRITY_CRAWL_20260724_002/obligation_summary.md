# Obligation Summary: D-Semantics Proof Obligations

This crawl campaign analyzed the current status of D-semantics proof obligations following the recent type-level preservation updates.

## Analyzed Obligations

| Obligation ID | Title | Status | Completion | Evidence / Blocker |
| --- | --- | --- | --- | --- |
| **OBL-D-001A** | Eval_D domain and codomain | DISCHARGED | 100% | `0011_d_eval_domain_codomain_contract_candidate.md` |
| **OBL-D-001B** | Context threshold | DISCHARGED_BOUNDED | 100% | `0012_epsilon_a_context_threshold_candidate.md` |
| **OBL-D-001C** | Typed transition preservation | DISCHARGED_BOUNDED | 100% | `P126_d_typed_projection_type_preservation_scope_closure.md` (Approved in commit `00489ef56`) |
| **OBL-D-001D** | Representable distinction preservation | OPEN | 0% | Blocker for theorem promotion. Requires representable distinction definition and Pi_D preservation verification. |
| **OBL-D-001E** | Non-collapse boundary | OPEN | 0% | Blocker for theorem promotion. Requires non-collapse boundary specification and countermodel search. |

## Repository Validation Blockers
- **governance_integrity_validation**: Mismatched hashes for governance assets (`GEMINI.md`, `AGENTS.md`).
- **db_snapshot_freshness**: Database snapshot is stale relative to the active worktree commit.
