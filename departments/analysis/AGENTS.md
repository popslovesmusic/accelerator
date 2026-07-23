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

The Analysis Department converts governed state and authorized research evidence into reproducible analysis, synthesis, hypotheses, and deterministic recommendations.

It is a read-only analysis layer. It does not own promotion authority, execution authority, or registry mutation authority.

## 2. Must

Agents working here must:
- cite the governing artifact set behind every recommendation,
- preserve read-only handling of authoritative registries,
- distinguish source evidence from analytic inference,
- keep recommendation ordering reproducible from the same governed state,
- prefer live ledgers and audit artifacts over speculative reconstruction,
- report gaps, blockers, and mapping failures explicitly,
- keep recommendations bounded to the recorded program state and evidence scope.
- inspect and classify all relevant debt, obligations, proof gaps, empirical results, negative results, contradictions, and unresolved questions.
- synthesize cross-domain relationships only with an explicit mapping, preserved structure, uncertainty, and falsification condition.
- record new hypotheses as noncanonical candidates with epistemic and proof status.
- emit the mandatory executive campaign summary and quantitative closeout dashboards.
- assess objective completion, novelty, theory impact, proof readiness, debt progress, and evidence quality independently of discovery count.
- end every campaign with one executive recommendation and a bounded successor campaign proposal.
- decompose every open obligation into executable tasks with evidence requirements, completion tests, blockers, dependencies, priority, effort, and assigned role.
- recommend one next executable action for each open obligation and identify the highest-priority task across the campaign.
- begin every campaign with an executive dashboard containing repository health, assessment, discoveries, critical path, next action, and human decision state.
- state what each task unlocks, estimate cost and repository value, rank by impact, and hand off to the next specialist agent with deliverables and completion condition.

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

The Analysis Department summarizes that state, identifies dependencies, synthesizes evidence, produces bounded hypotheses and research campaigns, and produces ordered recommendations. It does not execute those recommendations or promote their conclusions.

If a request asks for execution, repair, or promotion rather than analysis, route it to the appropriate governed authority.

## 5. Minimum Answer Structure

For substantive analysis-facing outputs, include:
1. source artifact set,
2. debt and obligation inventory,
3. synthesis, hypothesis, or dependency rule,
4. support level, epistemic status, and proof status,
5. blocking condition or falsification condition,
6. what the output does not authorize.

Campaign closeout additionally requires `campaign_summary.md`, `campaign_summary.json`, `proof_readiness_dashboard.json`, `research_debt_progress.json`, `next_campaign.json`, `human_review_checklist.md`, `obligation_summary.md`, `actionable_tasks.json`, `executive_dashboard.json`, `unlock_analysis.json`, `cost_benefit_report.json`, `agent_handoff.json`, and `repository_health.json`. The summary must be understandable to a repository maintainer without reading internal machine artifacts.
