# Agent: Registry Maintenance Scope

Applies to `registry/**` only.

## Authority

This file governs registry schema, lexicon, claim, evidence-index, and compliance-registry maintenance.

Root `AGENTS.md` still applies unless this file explicitly grants narrower local maintenance permission.

## Allowed

- Edit registry files only when explicitly requested by the user.
- Validate JSON after any registry edit.
- Preserve existing schemas, IDs, canonical names, and evidence references.
- Report schema conflicts, missing files, duplicate authorities, and stale references.
- Classify historical reports as residue unless current command evidence confirms them.

## Forbidden

- Promote claim status without direct current evidence.
- Rewrite historical reports as current authority.
- Delete canonical terms without explicit approval.
- Rename canonical terms without explicit approval.
- Modify claim or evidence registries based only on narrative summaries.
- Treat `registry/reports/**` as current authority.

## Required Verification

After any registry edit:

- Run JSON parse validation on changed JSON files.
- Run available registry validation scripts if present.
- Show `git diff -- registry/`.
- Report every changed file path.

## Evidence Rule

Every registry maintenance claim must identify the source file and whether it is current authority or historical residue.
