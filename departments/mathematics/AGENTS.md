# Mathematics Department Agent Rules

This file provides local governance for agents working inside `departments/mathematics/`.

It is subordinate to:
- repository-root `AGENTS.md`
- repository-root `GEMINI.md`
- `registry/compliance_charter_v2_3.json`
- `governance/claim_policy.json`
- `registry/claim_scope_binding_registry.json`
- `registry/governance/semantic_projection_policy.json`
- `docs/textbook/mono_process_textbook_complete.md`

## 1. Local Role

The Mathematics Department defines and maintains the formal relational calculus, theorem status, proof structure, and operator laws used across governed departments.

Its live design authority is the textbook SSOT at `docs/textbook/mono_process_textbook_complete.md`.

## 2. Must

Agents working here must:
- treat mathematics as the local design authority for mathematics-owned artifacts,
- parse `docs/textbook/mono_process_textbook_complete.md` before proposing or applying any mathematics-owned change,
- distinguish formal definition from application-domain interpretation,
- distinguish proof scaffolding from formal closure,
- preserve current textbook content unchanged unless a governed patch explicitly authorizes an update,
- keep registry updates traceable to the current textbook SSOT and live validation state,
- use the phrase `Within the Mathematics Department interpretation...` only when making a bounded mathematics-facing interpretive statement.

## 3. Must Not

Agents working here must not:
- rewrite the textbook SSOT during registration-only governance updates,
- treat application-domain projections as mathematical primitives,
- promote scaffolded or provisional results as formally proven without registry support,
- infer missing governance from informal context,
- collapse execution state into design intent.

## 4. Working Boundary

Mathematics defines the formal source language.

Governed registries, validators, and audit artifacts define executable state.

If a request is really asking for formal definition, theorem status, proof structure, or operator law, answer from the mathematics SSOT and cite the relevant registry or proof artifact.

## 5. Minimum Answer Structure

For substantive mathematics-facing outputs, include:
1. formal source term,
2. theorem, lemma, or proof relation,
3. claim class or status,
4. validation status,
5. what the statement does not prove.
