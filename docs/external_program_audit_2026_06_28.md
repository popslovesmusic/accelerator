# External Program Audit

Date: 2026-06-28
Mode: manual repository audit only
Scope: governance, SSOT/docs, tooling, lexicon, departments, task/debt tracking, operational hygiene
Constraint: no validators were run for this audit

## Executive Summary

The program has substantial governance material, a large machine-readable registry surface, a living textbook, and a real tooling stack. The main problem is not lack of artifacts. The main problem is convergence. Several important governance systems exist in concept but are not yet operational as live canonical ledgers. Department induction is only partially executed. The lexicon has grown faster than its classification discipline. Tool approval exists, but the routing metadata is still too thin for clean external governance.

Overall external ruling:

- Governance architecture: strong in intent, partial in enactment
- SSOT discipline: present, but fragmented
- Tooling: substantial, but incompletely governed at the routing layer
- Lexicon: rich, but under-classified
- Department system: promising, but not constitutionally complete
- Research debt visibility: defined, not yet operationalized

## Method

This audit was based on manual inspection of repository structure and selected authority files, including:

- [README.md](/abs/path/D:/projects/acellorator/README.md:13)
- [AGENTS.md](/abs/path/D:/projects/acellorator/AGENTS.md:25)
- [GEMINI.md](/abs/path/D:/projects/acellorator/GEMINI.md:25)
- [governance/claim_policy.json](/abs/path/D:/projects/acellorator/governance/claim_policy.json:1)
- [registry/compliance_charter_v2_3.json](/abs/path/D:/projects/acellorator/registry/compliance_charter_v2_3.json:1)
- [registry/db/README.md](/abs/path/D:/projects/acellorator/registry/db/README.md:8)
- [docs/textbook/mono_process_textbook_complete.md](/abs/path/D:/projects/acellorator/docs/textbook/mono_process_textbook_complete.md:2538)
- [registry/lexicon_canonical.json](/abs/path/D:/projects/acellorator/registry/lexicon_canonical.json:14837)
- [registry/tool_manifest.json](/abs/path/D:/projects/acellorator/registry/tool_manifest.json:4)
- [departments/department_registry.json](/abs/path/D:/projects/acellorator/departments/department_registry.json:2)
- [governance/program_task_registry.json](/abs/path/D:/projects/acellorator/governance/program_task_registry.json:2)
- [registry/research_debt_registry.json](/abs/path/D:/projects/acellorator/registry/research_debt_registry.json:4)

## Findings

### 1. Governance ledgers are still proposal-shaped rather than operational

Severity: high

Three important governance artifacts are framed as patch/proposal documents rather than live operational ledgers:

- [departments/department_registry.json](/abs/path/D:/projects/acellorator/departments/department_registry.json:2) begins with `patch_id` and `status: "proposed"`, and includes `initial_registry_seed` rather than a clean live registry model.
- [governance/program_task_registry.json](/abs/path/D:/projects/acellorator/governance/program_task_registry.json:2) also begins with `patch_id` and `status: "proposed"`, and currently contains `initial_backfill_tasks` rather than an actual maintained task ledger.
- [registry/research_debt_registry.json](/abs/path/D:/projects/acellorator/registry/research_debt_registry.json:4) is also `status: "proposed"`.

Why this matters:

- Governance cannot rely on “future registry shape” forever.
- External reviewers cannot easily tell whether these are constitutional authorities or pending patch specs.
- AI/RAG routing will treat these files as authoritative unless a stronger separation exists.

Gap:

- The repo lacks a clean distinction between `patch specification` and `live registry instance`.

### 2. Department induction is constitutionally incomplete

Severity: high

The textbook states that departments are first-class governed peers under `departments/` and require a local SSOT plus `AGENTS.md` before entering the claim lifecycle: [mono_process_textbook_complete.md](/abs/path/D:/projects/acellorator/docs/textbook/mono_process_textbook_complete.md:2538).

Current repo state does not fully satisfy that:

- Mathematics is still only planned: [departments/department_registry.json](/abs/path/D:/projects/acellorator/departments/department_registry.json:96)
- Economics content exists elsewhere, not under `departments/`: [departments/department_registry.json](/abs/path/D:/projects/acellorator/departments/department_registry.json:154)
- Theology governance files still live under `docs/theology/`, not `departments/theology/`: [departments/department_registry.json](/abs/path/D:/projects/acellorator/departments/department_registry.json:183)
- Physics is inducted, but still uses `physics_ssot.md` instead of the normalized `department_ssot.md`: [departments/department_registry.json](/abs/path/D:/projects/acellorator/departments/department_registry.json:125)

Why this matters:

- The constitutional story and filesystem reality diverge.
- Retrieval and routing become ambiguous when some departments are “real” and others are still documentary.
- Cross-department bridge governance cannot fully stabilize until department roots are real.

### 3. The repo entry-point documentation is stale

Severity: medium

The main README still directs users to a governance file that does not exist:

- README points to `docs/governance/AGENTS.md`: [README.md](/abs/path/D:/projects/acellorator/README.md:35)
- The actual file present is `docs/AGENTS.md`, while `docs/governance/AGENTS.md` is absent.

This is a direct onboarding defect.

Why this matters:

- New contributors or external auditors hit broken governance paths immediately.
- It reduces trust in the repo’s claim that governance is first-class.

### 4. Lexicon authority exists, but classification discipline is weak

Severity: high

The lexicon is large and machine-readable, but its statistics show weak normalization:

- Canonical terms: [registry/lexicon_canonical.json](/abs/path/D:/projects/acellorator/registry/lexicon_canonical.json:14837)
- `unclassified` ontology count: [registry/lexicon_canonical.json](/abs/path/D:/projects/acellorator/registry/lexicon_canonical.json:14840)
- `unclassified` definition mode count: [registry/lexicon_canonical.json](/abs/path/D:/projects/acellorator/registry/lexicon_canonical.json:14869)

Observed values:

- 912 canonical terms
- 841 unclassified ontology assignments
- 868 unclassified definition modes

Why this matters:

- The canonical lexicon is serving as semantic authority while most of it is not fully typed.
- Governance cannot reliably distinguish primitive, operator, metaphor, or projection at scale if the canonical store is mostly unclassified.
- This increases AI confusion and human review load.

### 5. Tool governance exists, but the manifest is too thin for deterministic routing

Severity: high

The approved tool registry is real, but the main manifest only exposes:

- tool name
- mechanism class
- rigor level

Examples:

- [registry/tool_manifest.json](/abs/path/D:/projects/acellorator/registry/tool_manifest.json:4)
- [registry/tool_manifest.json](/abs/path/D:/projects/acellorator/registry/tool_manifest.json:24)
- [registry/tool_manifest.json](/abs/path/D:/projects/acellorator/registry/tool_manifest.json:69)

What is missing from the main tool manifest:

- filesystem path
- owner
- invocation contract
- accepted input schema
- output schema
- allowed use class
- forbidden use class
- evidence ceiling
- deprecation/review status

Why this matters:

- “Approved tool” is not enough for a router or external reviewer.
- There is no single authoritative manifest that answers “what can this tool do, how is it called, and what claims may it support?”

### 6. Research debt is formally defined but not operationally populated

Severity: high

The debt registry says all intentional incompleteness must be registered: [research_debt_registry.json](/abs/path/D:/projects/acellorator/registry/research_debt_registry.json:9).

But the registry itself remains:

- proposed: [research_debt_registry.json](/abs/path/D:/projects/acellorator/registry/research_debt_registry.json:4)
- zeroed out in metrics: [research_debt_registry.json](/abs/path/D:/projects/acellorator/registry/research_debt_registry.json:105)

This is inconsistent with the visible amount of open debt in:

- Appendix F bridge debt: [mono_process_textbook_complete.md](/abs/path/D:/projects/acellorator/docs/textbook/mono_process_textbook_complete.md:3162)
- Appendix F lexicon debt: [mono_process_textbook_complete.md](/abs/path/D:/projects/acellorator/docs/textbook/mono_process_textbook_complete.md:3200)

Why this matters:

- The program conceptually accepts debt, but the live debt book is empty.
- That makes governance visibility weaker than the textbook narrative suggests.

### 7. Program task tracking is not yet a live operational backlog

Severity: medium

The Program Task Registry is still a proposed patch artifact with backfill tasks rather than a live program board:

- proposed artifact status: [program_task_registry.json](/abs/path/D:/projects/acellorator/governance/program_task_registry.json:2)
- backfill-only task list: [program_task_registry.json](/abs/path/D:/projects/acellorator/governance/program_task_registry.json:129)

Why this matters:

- The repo has many active structural gaps, but no clearly maintained program-level ledger that external reviewers can trust.
- Dependencies remain descriptive instead of operational.

### 8. Encoding hygiene is degraded in governance-facing files

Severity: medium

Visible mojibake appears in active governance files, for example:

- [GEMINI.md](/abs/path/D:/projects/acellorator/GEMINI.md:25)
- [GEMINI.md](/abs/path/D:/projects/acellorator/GEMINI.md:48)

Why this matters:

- Governance text is a control surface for both humans and AI.
- Encoding corruption in core expressions and evidence-class language can lead to parsing errors, retrieval noise, and subtle misinterpretation.

### 9. SSOT authority is defined, but the actual SSOT surface is fragmented

Severity: medium

The repo has a clear SSOT boundary rule for the DB:

- [registry/db/README.md](/abs/path/D:/projects/acellorator/registry/db/README.md:8)
- [registry/db/README.md](/abs/path/D:/projects/acellorator/registry/db/README.md:266)

But the actual semantic authority is spread across:

- textbook
- charter
- lexicon
- claim registries
- department SSOTs
- patch records
- multiple historical math schema versions under `docs/`

The prior audit already flagged schema fragmentation: [docs/audit.json](/abs/path/D:/projects/acellorator/docs/audit.json:298).

Why this matters:

- The SSOT concept exists, but the repo still behaves like a federated archive.
- That is workable for humans with context, but brittle for tooling and external review.

### 10. Worktree state is operationally noisy

Severity: medium

Manual inspection of the current worktree shows a large number of modified generated artifacts and several untracked governance files. This is not a theoretical defect, but it is an operational audit risk because:

- it complicates provenance review
- it makes “current state” harder to summarize externally
- it increases the chance of stale generated outputs being mistaken for endorsed state

This finding is based on current repository state observed during the audit, not on a registry line reference.

## System Assessment

### Governance

Assessment: conceptually strong, operationally partial

Strengths:

- clear humility and claim-gating language
- explicit non-DB SSOT boundary
- strong compliance charter
- active Appendix F debt framing

Gaps:

- live governance ledgers are still proposal-shaped
- department induction incomplete
- debt ledger not populated

### Tooling

Assessment: technically substantial, governance metadata incomplete

Strengths:

- large approved tool surface
- mechanism diversity
- explicit rigor levels

Gaps:

- tool manifest too thin for deterministic routing
- no single canonical “allowed tool action manifest” for non-simulation governance work

### Lexicon

Assessment: rich corpus, under-disciplined canonicalization

Strengths:

- explicit gap queue
- canonical lexicon exists
- promotion governance concept is present

Gaps:

- most canonical terms are still unclassified
- definition modes are largely unset
- canonical authority is therefore weaker than it appears

### SSOT / Textbook

Assessment: strong living core, but still carrying integration debt

Strengths:

- textbook is clearly the living center of the program
- Appendix F functions as a visible frontier/debt queue

Gaps:

- constitutional claims about departments exceed actual filesystem realization
- some repo-facing references are stale

### Departments

Assessment: promising architecture, incomplete rollout

Strengths:

- physics and ethics induction has begun
- constitutional framing is coherent

Gaps:

- mathematics missing as an actual department root
- economics and theology not yet peer-inducted under `departments/`
- filename normalization not complete

## Governance Gap List

These are the main governance gaps exposed by the audit:

1. No clean separation between patch proposal artifacts and live canonical registries.
2. Department constitution is declared more strongly than it is implemented.
3. Research debt policy exists without a populated debt ledger.
4. Program task governance exists without a live maintained backlog.
5. Tool approval exists without a sufficient routing/invocation contract layer.
6. Canonical lexicon authority is undermined by large-scale under-classification.
7. Governance-facing encoding hygiene is not fully controlled.
8. Onboarding/governance entry-point docs contain stale paths.

## Smallest Rational Next Steps

This is not a patch plan, only an external audit judgment. The smallest rational next steps would be:

1. Convert the department, program task, and research debt artifacts from patch/proposal form into live operational registry form.
2. Finish the minimum peer department layout or explicitly downgrade the constitutional language until the layout exists.
3. Add routing metadata to the tool manifest: path, invocation, schema, evidence ceiling, allowed uses.
4. Run a lexicon typing pass focused only on ontology class and definition mode completion.
5. Repair stale onboarding/governance links.
6. Fix encoding corruption in governance-facing markdown/json sources.

## Final Ruling

The program is real, structured, and materially governed. It is not governance-empty. But it is still in a transitional architecture phase where several of its most important governance systems are defined more clearly than they are enacted. The core weakness is not lack of doctrine. It is incomplete conversion of doctrine into live operational ledgers and normalized repository structure.

External audit ruling:

- Not governance-failed
- Not governance-complete
- Most important present risk: governance fragmentation between declared authority and live operational state
