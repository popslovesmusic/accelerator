# Analysis Department Agent Rules

This file provides local governance for agents working inside `departments/analysis/`.

It is subordinate to:
- repository-root `AGENTS.md`
- repository-root `GEMINI.md`
- `registry/compliance_charter_v2_3.json`
- `governance/claim_policy.json`
- `registry/claim_scope_binding_registry.json`
- `registry/governance/semantic_projection_policy.json`
- `governance/live/work_reduction_framework.json`
- `governance/live/master_work_index.json`
- `departments/analysis/department_ssot.md`

## 1. Local Role

The Analysis Department converts governed state into deterministic recommendations.

It is a read-only analysis layer. It does not own promotion authority, execution authority, or registry mutation authority.

## 2. Must

Agents working here must:
- cite the governing artifact set behind every recommendation,
- preserve read-only handling of authoritative registries,
- distinguish source evidence from analytic inference,
- keep recommendation ordering reproducible from the same governed state,
- prefer live ledgers and audit artifacts over speculative reconstruction,
- report gaps, blockers, and mapping failures explicitly,
- keep recommendations bounded to the recorded program state.

## 3. Must Not

Agents working here must not:
- modify authoritative registries,
- execute work items,
- close queues or campaigns,
- promote theorem, proof, lemma, or governance state,
- invent missing evidence,
- treat analysis projections as executable truth,
- override source-ledger authority.

## 4. Working Boundary

Governed registries define current executable state.

The Analysis Department summarizes that state, identifies dependencies, and produces ordered recommendations only.

If a request asks for execution, repair, or promotion rather than analysis, route it to the appropriate governed authority.

## 5. Minimum Answer Structure

For substantive analysis-facing outputs, include:
1. source artifact set,
2. derived recommendation or dependency rule,
3. support level or confidence,
4. blocking condition if any,
5. what the recommendation does not authorize.
