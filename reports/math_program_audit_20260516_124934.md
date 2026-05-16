# Math Program Audit (Not Tooling)

- Repo: `D:\projects\acellorator`
- Audit date (local): 2026-05-16 (America/New_York)
- Mode: Audit (read-only inspection; no repairs performed)
- Scope: **Math program artifacts** (codex, theorems/lemmas/proofs, formal-object and math registries, math-program validation results). Tooling, runtime, and engine code are out of scope except where they directly impact the math program’s correctness/governance claims.

## 1. Executive Summary

The repository contains a **structured math program** built around:

1. A human-readable codex (`docs/math/*`) organized into volumes and atlases.
2. A registry-first formalization layer (`registry/math/*` plus several root registries like `formal_object_registry.json`, `lemma_registry.json`, `theorem_status_registry.json`).
3. A minimal theorem (MT) program with proof artifacts in `proofs/MT-001..003/` and registry bindings tying those artifacts to quantifiers, boundary cases, failure modes, and proof-strengthening criteria.

The program shows strong **governance discipline**: explicit scoping, explicit failure modes, explicit “must not promote” constraints, and a clear SSOT posture (JSON registries and compliance charter are canonical; DB is projection only).

However, there are **material consistency gaps** between:

- codex “status” labels vs registry “readiness/strengthening” labels,
- the presence of proof artifacts vs their registration in the *root* proof registry,
- multiple near-duplicate registry files with singular/plural naming,
- and a failing math-program validation gate tied to missing mandatory reconciliation governance rules.

These gaps don’t “break” the program’s intent, but they do weaken its ability to function as a reliably auditable, promotion-safe math stack.

## 2. Artifact Map (What Appears To Be The Math Program SSOT)

### 2.1 Human-facing codex

Primary index:
- `docs/math/codex_master_index.md`

Key volumes:
- `docs/math/codex_volume_1_foundations.md`
- `docs/math/codex_volume_2_admissibility_and_continuation.md`
- `docs/math/codex_volume_4_theorem_program.md`
- `docs/math/codex_volume_5_counterexample_and_open_frontiers.md`

### 2.2 Minimal theorem artifacts (MT program)

Proof artifacts:
- `proofs/MT-001/proof.md`, `proofs/MT-001/formal_verification.json`, `proofs/MT-001/verification_checklist.json`
- `proofs/MT-002/proof.md`, `proofs/MT-002/formal_verification.json`, `proofs/MT-002/verification_checklist.json`
- `proofs/MT-003/proof.md`, `proofs/MT-003/formal_verification.json`, `proofs/MT-003/verification_checklist.json`

Registry bindings (examples; non-exhaustive):
- `registry/math/theorem_quantifier_registry.json`
- `registry/math/theorem_boundary_condition_registry.json`
- `registry/math/theorem_promotion_blocker_registry.json`
- `registry/math/theorem_proof_strengthening_registry.json`
- `registry/math/formal_candidate_readiness_registry.json`

### 2.3 “Math registry” layer

The `registry/math/` directory is extensive and appears to encode:

- operator laws and functional forms,
- well-posedness conditions and failure modes,
- boundary case and failure-mode taxonomies,
- reduction chains and derivation closure tracking,
- counterexample obligations and incompleteness handling.

Examples:
- `registry/math/well_posedness_registry.json`
- `registry/math/boundary_case_registry.json`
- `registry/math/symbolic_reduction_chain_registry.json`
- `registry/math/symbolic_derivation_closure_registry.json`

### 2.4 Root registries that affect math program meaning

These are not under `registry/math/` but directly govern math-program semantics and promotion constraints:

- `registry/theorem_status_registry.json` (status taxonomy and promotion ceilings)
- `registry/lemma_registry.json`
- `registry/theorem_closure_registry.json`
- `registry/formal_object_registry.json` (formal object list and bindings)
- `registry/proof_registry.json` (general proof registry)
- `registry/compliance_charter_v2_3.json` (claim/promotion governance)

## 3. Key Evidence Excerpts (Load-Bearing)

### 3.1 Codex declares MT statuses as “Consolidated”

From `docs/math/codex_volume_4_theorem_program.md`:

```
## 1. MT-001: Projection Idempotence
- **Status**: Consolidated.
...
## 2. MT-002: Transport Identity
- **Status**: Consolidated.
...
## 3. MT-003: Non-Empty Admissible Image
- **Status**: Consolidated.
```

Note: In the same file, the symbol `∘` appears as mojibake (`âˆ˜`) under default PowerShell `Get-Content` decoding, suggesting a text-encoding mismatch for at least some readers/toolchains.

### 3.2 Registry-level readiness and strengthening do not call MT “consolidated”

From `registry/math/formal_candidate_readiness_registry.json`:

- MT-001 readiness: `symbolic_supported`, pending `PO-001`, with a note: “Awaiting formal property proof for admissibility_equivalence.”
- MT-002 readiness: `symbolic_supported`, pending `PO-002`.
- MT-003 readiness: `symbolic_supported`, pending `PO-003`.

From `registry/math/theorem_proof_strengthening_registry.json`:

- MT-001/002/003 current_status: `scaffolded`
- current_evidence_level: `symbolic_supported_candidate`
- active_blockers: subsets of `BLK-001..003`

Interpretation: codex labeling (“Consolidated”) is materially *stronger* than registry labeling (“scaffolded / symbolic supported candidate”).

### 3.3 Proof artifacts are explicitly non-promotable

From `proofs/MT-001/formal_verification.json`:

```
"verification_status": "symbolic_verified_under_assumptions",
...
"must_not_promote": true
```

This is healthy (promotion safety) but conflicts with any external narrative that might interpret “Consolidated” as “fully promoted/closed”.

### 3.4 Math program validation report is failing, with a concrete reason

From `validation/results/math_program_validation_report_sim_005.json`:

- Overall status: `fail`
- Timestamp: `2026-05-15T18:01:51.945209`
- Readiness summary:

```
{
  "ready_for_local_theorem_work": false,
  "ready_for_global_closure_claims": false,
  "ready_for_physics_claims": false
}
```

The only failing domain gate is `pi_a_reconciliation_atlas`:

```
"status": "fail",
"governance_violations": [
  "missing mandatory rule: reconciliation is not discharge",
  "missing mandatory rule: counterexamples are structural information"
]
```

This is a precise, governance-level failure and should be treated as a blocking issue for any “consolidated” language that implies readiness or promotion.

## 4. Audit Findings

### Finding A (High): Status drift between codex narrative and registry SSOT

Evidence:
- Codex Volume 4: MT-001/2/3 are “Consolidated”
- Registry readiness + strengthening: MT-001/2/3 are “scaffolded / symbolic_supported candidate” with active blockers and pending proof obligations
- MT formal verifications explicitly carry `must_not_promote: true`

Risk:
- A reader may treat codex narrative as SSOT and over-promote statements in downstream usage, violating the governance intent of the program.

Recommendation (non-patch):
- Align codex status language with registry status taxonomy (e.g., map “Consolidated” to a defined registry status or remove the label in favor of registry-derived status).

### Finding B (High): Validation fails due to missing reconciliation governance rules

Evidence:
- `validation/results/math_program_validation_report_sim_005.json` fails specifically on `pi_a_reconciliation_atlas` and lists missing mandatory rules.

Risk:
- Reconciliation workflows are where “math program” meets counterexample management. Missing “reconciliation is not discharge” and “counterexamples are structural information” invites exactly the kind of silent closure drift the governance framework is designed to prevent.

Recommendation (non-patch):
- Add/encode these mandatory rules into the reconciliation atlas governance layer (wherever that’s defined in the math registries or related docs), then re-run the math-program validation.

### Finding C (Medium): Root `proof_registry.json` does not register the MT proofs

Evidence:
- `registry/proof_registry.json` enumerates P001..P008 (and references theorems like `MST-001`, `OASSOC-001`) but does not include MT-001/2/3 proof artifacts.
- MT artifacts are registered under `registry/math/*` (formal proof artifacts registries, readiness, blockers), but not in the general proof registry.

Risk:
- Two competing “proof indices” can drift. If downstream tooling or audits rely on `registry/proof_registry.json` as the canonical proof list, MT proofs could be omitted from program-wide provenance checks.

Recommendation (non-patch):
- Decide whether MT proofs must be present in `registry/proof_registry.json` (single index) or whether MT proofs are intentionally “math-program local” and must never appear there. Then enforce that decision in validation.

### Finding D (Medium): Near-duplicate registries with singular/plural naming

Evidence:
- `registry/math/formal_proof_artifact_registry.json` and `registry/math/formal_proof_artifacts_registry.json` both exist and differ (line diff count 2).
- Similarly for `formal_verification_artifact_registry.json` vs `formal_verification_artifacts_registry.json`.

Risk:
- Naming collisions can cause inconsistent ingestion, validation confusion, or non-deterministic “which file did we mean?” behavior.

Recommendation (non-patch):
- Establish one canonical filename per concept (singular or plural) and treat the other as deprecated residue. If residue must remain, explicitly mark its orientation/status and enforce “do not ingest” rules.

### Finding E (Low/Medium): `registry/math/theorem_dependency_registry.json` appears incomplete

Evidence:
- The file lists only MT-001 dependencies.

Risk:
- Dependency-driven audits and retrieval will under-represent MT-002 and MT-003, despite their presence in other registries (quantifiers, boundary cases, strengthening).

Recommendation (non-patch):
- Ensure dependency mappings exist for MT-002 and MT-003 (or explicitly document why they are excluded).

### Finding F (Low): Text encoding/readability issues in codex

Evidence:
- `Pi_A âˆ˜ Pi_A` appears in codex output under default PowerShell decoding; the intended operator composition symbol is likely `∘`.

Risk:
- Not a mathematical correctness problem per se, but harms readability and can cause copy/paste or downstream parsing errors for symbolic expressions.

Recommendation (non-patch):
- Standardize encoding (UTF-8) for codex markdown, and ensure repo tooling reads it as UTF-8 consistently.

## 5. Overall Assessment

- The math program is **well-structured** and shows explicit governance around incompleteness, boundary handling, and promotion safety.
- The largest current weakness is **status drift**: narrative labels and validation readiness gates need tighter coupling to registry SSOT.
- The current math-program validation report (`sim_005`, timestamp 2026-05-15) is **fail** for a specific governance-rule omission related to reconciliation and counterexamples. That should be treated as a gating issue for “consolidated” status claims and any promotion language.

## 6. Commands Run (Audit Evidence)

These commands were used to gather evidence (representative subset):

- `Get-ChildItem -Force` (repo top-level inventory)
- `rg -n "(axiom|theorem|lemma|proof|...)" docs proofs registry validation -S`
- `Get-ChildItem registry\\math -File` (math registry inventory)
- `Get-Content -Raw ... | Select-Object -First N` (targeted excerpt reads)
- `ConvertFrom-Json` for targeted JSON introspection
- `Get-FileHash` and `Compare-Object` for near-duplicate registry comparison

