# Agent: Script Maintenance Scope

Applies to `scripts/**` only.

## Authority

This file governs validation, audit, governance, orchestration, and maintenance scripts.

Root `AGENTS.md` still applies unless this file explicitly grants narrower local maintenance permission.

## Allowed

- Inspect scripts.
- Run validation scripts.
- Patch scripts only when explicitly requested.
- Preserve CLI behavior and existing arguments unless a breaking change is explicitly approved.
- Add safer diagnostics, clearer error reporting, or read-only audit modes when requested.

## Forbidden

- Change governance thresholds without explicit approval.
- Silence validation failures.
- Convert warnings into passes without evidence.
- Make scripts mutate registries unless the user explicitly requests that behavior.
- Change output schemas without documenting the change.

## Required Verification

After any script edit:

- Run the relevant script with a safe test command if available.
- Run syntax validation or import check.
- Show `git diff -- scripts/`.
- Report changed paths and any behavior changes.

## Audit Rule

Scripts used for audit must distinguish current command evidence from historical residue.
