# Analysis Intake Department Agent Rules

This file provides local governance for agents working inside `departments/analysis_intake/`.

It is subordinate to:
- repository-root `AGENTS.md`
- repository-root `GEMINI.md`
- `registry/compliance_charter_v2_3.json`
- `governance/claim_policy.json`
- `registry/claim_scope_binding_registry.json`
- `registry/governance/semantic_projection_policy.json`
- `departments/analysis/AGENTS.md`
- `departments/analysis_intake/department_ssot.md`

## 1. Local Role

The Analysis Intake Department converts structured packets and raw human notes into classified governed work proposals.

**Canonical intake home:** This directory is the required local-governance home for submitted proposals, induction preservation, intake classification, provenance capture, and queue-routing analysis. Every intake-facing packet must point to this directory and its local SSOT, `department_ssot.md`.

**First-contact preservation:** Induction is completed only after the complete submitted artifact is preserved or captured through the approved source mode, hashed, and registered in the governed induction queue. Review summaries, classifications, or `HOLD_C1` dispositions do not substitute for preservation and must remain downstream references.

**Chat submission persistence:** For proposals pasted into chat, create a complete `CHAT_SEMANTIC_CAPTURE` in this directory before induction. Record the conversation channel, packet ID, capture time, canonical capture hash, and any capture limitations. Byte-for-byte equality is required only when the proposal was supplied as a file.

It is a read-only intake layer. It can propose artifacts for approval, but it does not execute, close, or promote authority.

## 2. Must

Agents working here must:
- preserve source provenance for every extracted item,
- distinguish structured JSON from provisional raw text,
- route ambiguous content to review instead of forcing a classification,
- keep proposed artifacts separate from authoritative registries,
- extract candidate claims, terms, operators, risks, and work items when present,
- preserve source excerpts and source paths for all routed items,
- keep intake results reproducible from the same input packet.

## 3. Must Not

Agents working here must not:
- modify authoritative registries directly,
- promote claims from raw text,
- execute or close work items,
- treat provisional input as authority,
- discard ambiguity by guessing,
- erase source context when normalizing a packet.

## 4. Working Boundary

Structured input may produce direct proposed patches.

Raw input must be treated as provisional and routed through extraction, classification, deduplication, and approval queuing before any downstream governed action.

If an input asks for execution or promotion, route it to the appropriate governed authority after intake classification.

## 5. Minimum Answer Structure

For substantive intake-facing outputs, include:
1. input class,
2. extracted candidates,
3. source provenance,
4. routing target,
5. what the intake does not authorize.
