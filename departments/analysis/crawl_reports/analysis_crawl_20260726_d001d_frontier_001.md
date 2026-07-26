# Analysis Crawl — 2026-07-26

## Campaign purpose

Produce the required bounded, read-only Analysis Department synthesis of the current governed frontier, with special attention to the new OBL-D-001D evidence and its effect on the D-semantics promotion gate.

## Scope and source artifact set

Read-only inspection covered:

- `AGENTS.md`, `GEMINI.md`, `departments/analysis/AGENTS.md`, and `departments/analysis/department_ssot.md`;
- `governance/live/master_work_index.json`, `governance/live/research_debt_registry.json`, and `governance/live/induction_queue.json`;
- `departments/analysis/program_state_report.json`, `departments/analysis/recommended_action_queue.json`, and `outputs/audits/global_health_report.json`;
- `registry/math/d_semantics_obligation_registry.json` and `registry/research_debt_registry.json`;
- the OBL-D-001D typed representability campaign and semantic-review campaign dated 2026-07-25;
- relevant D-semantics passages in `docs/textbook/mono_process_textbook_complete.md` and the additive mathematics notes.

This crawl did not index artifacts, refresh SQLite, execute campaigns, modify canonical state, or alter claim/obligation status.

## Directly observed

- The governance runtime reports no runtime blockers, but its database snapshot is stale relative to the worktree; this prevents freshness-based closeout claims.
- The master work index records 91 items, with 90 completed and one archived; no active or unmapped work-index item is present.
- The live research-debt registry retains one substantive open debt: `DEBT_D_SEMANTICS_PROOF_001`.
- `OBL-D-001A` is `DISCHARGED`, `OBL-D-001B` is `DISCHARGED_BOUNDED`, and `OBL-D-001C` is `DISCHARGED_BOUNDED` within type-level scope.
- `OBL-D-001D` remains `OPEN` with `DEFINEDNESS_RELATION_UNRESOLVED`.
- The typed representability campaign passed 8/8 finite hand-authored fixtures. Its own report limits the result to candidate validation and claims no obligation discharge.
- Human review approved bounded qualification of `CLAIM_020_005` at `C1_DEFINED_PROVISIONAL`; theorem and axiom promotion remain unauthorized.
- `OBL-D-001E` remains open and downstream.
- The textbook contains an internal wording conflict: sections 1.2.2B.12 and the glossary state that projection preserves representable distinction, while the D-semantics summary states that semantic representable-distinction preservation remains unresolved.
- The latest global health report is warning-level, with degraded hygiene, math-program, and report-write stages, although no failed stage is reported.

## Inferred inside the framework

The current frontier has moved from defining the representability vocabulary toward independent acceptance of its component semantics and then a separate non-collapse analysis. The bounded evidence rejects projection-image-only and outcome-label-only proxies, but does not establish general preservation under `Pi_D`.

This is a bounded analysis inference, not a theorem, proof, physical claim, or promotion decision.

## Discovery records

### DISCOVERY_CRAWL_20260726_D001D_001

- Class: `PROOF_OBLIGATION`
- Epistemic status: `SOURCE_REPORTED`
- Proof status: `OBLIGATIONS_IDENTIFIED`
- Statement: A typed witness, compatible trace, and explicit history are required by the tested candidate representability predicate; finite fixtures support rejection of projection-only and outcome-label-only proxies.
- Support: 8/8 candidate fixtures passed; broader campaign records 216 finite fixtures and 594 matched-image counterexamples.
- Limitation: component semantics are not independently mechanized or formally accepted; general preservation remains unresolved.
- Falsification/reopen condition: an independently checked bounded model shows the predicate is either insufficient within its declared scope or that the proposed components do not determine representability.

### DISCOVERY_CRAWL_20260726_DOC_001

- Class: `CONTRADICTION`
- Epistemic status: `OBSERVED`
- Proof status: `OBLIGATIONS_IDENTIFIED`
- Statement: The textbook simultaneously uses unrestricted preservation wording and records semantic preservation as an open D-semantics obligation.
- Impact: documentation can overstate the current claim ceiling even though the live registry and campaign records retain the correct open status.
- Falsification/reopen condition: a later synchronized textbook revision removes the conflicting wording and is verified against the live registry.

## Obligation and debt inventory

| Item | Status | Blocking effect | Required next evidence |
|---|---|---|---|
| `DEBT_D_SEMANTICS_PROOF_001` | Open | Blocks D-semantics theorem promotion | Complete D and E with formal or independently checked bounded support |
| `OBL-D-001D` | Open | Blocks D promotion; E depends on it | Independent acceptance of predicate components and bounded preservation analysis |
| `OBL-D-001E` | Open | Blocks D promotion | Specify non-collapse boundary and produce bounded counterexample |
| Textbook preservation wording | Inconsistent | Risks claim escalation | Documentation reconciliation against live D status |
| DB snapshot | Stale | Blocks freshness-based closeout | Authorized snapshot refresh and freshness verification |

## Campaign assessment

`PARTIAL_SUCCESS`: the crawl identified a meaningful bounded reduction in uncertainty and a documentation contradiction, but no proof obligation was discharged and the repository is not freshness-clean.

Confidence: high for directly observed registry/campaign states; moderate for the cross-document contradiction because the textbook contains both current and stale wording.

## Executive recommendation

`FORMALIZE`: independently formalize and review the typed representability predicate, then reconcile the textbook wording before reassessing `OBL-D-001E`. Keep all D-semantics claims at `C1_DEFINED_PROVISIONAL` and preserve the promotion block.

## Required successor campaign

Use a finite, independently implemented predicate checker with explicit typed-witness, trace, history, and matched-image controls. Require a fixed pre-execution specification, independent review, negative controls, and a finite stopping rule. The successor must not modify canonical status without a separately authorized maintenance action.

## What this crawl does not authorize

It authorizes no registry mutation, textbook patch, theorem or axiom promotion, proof discharge, simulation execution, artifact indexing, SQLite refresh, production cutover, or external physical interpretation.

## Deliverable and closeout note

This Markdown report and its matching JSON report are the required non-canonical crawl deliverables. Canonical and authority-bearing files were not modified by the crawl analysis.

