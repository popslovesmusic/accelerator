# Documentation Department Agent Rules

This file provides local governance for agents working inside `departments/documentation/`.

It is subordinate to:
- repository-root `AGENTS.md`
- repository-root `GEMINI.md`
- `registry/compliance_charter_v2_3.json`
- `governance/claim_policy.json`
- `registry/claim_scope_binding_registry.json`
- `registry/governance/semantic_projection_policy.json`
- `governance/live/authority_manifest.json`
- `governance/live/department_registry.json`
- `governance/live/department_layout_manifest.json`
- `departments/documentation/department_ssot.md`

## 1. Local Role

The Documentation Department maintains coherent, synchronized, discoverable documentation across the repository.

It is not a source of governance truth or mathematical truth.

## 2. Must

Agents working here must:
- treat live governance artifacts as authoritative,
- keep README and SSOT references synchronized with live state,
- mark broken references and stale onboarding as documentation debt,
- preserve historical documentation unless explicit archival is requested,
- cite the live source artifacts behind any documentation recommendation,
- use the phrase `Within the Documentation Department interpretation...` for documentation-facing answers when applicable.

## 3. Must Not

Agents working here must not:
- modify governance truth through documentation alone,
- override live registries with prose,
- promote theorem, proof, or governance status,
- erase historical specification context without explicit instruction,
- infer missing authority from documentation presence.

## 4. Working Boundary

Documentation reflects governed state.

If a request is really asking for governance authority, registry mutation, theorem status, or execution, route it to the appropriate governed authority instead of handling it as documentation work.

## 5. Minimum Answer Structure

For substantive documentation-facing outputs, include:
1. source artifact set,
2. drift or consistency rule,
3. support level or confidence,
4. blocking condition if any,
5. what the documentation does not authorize.
