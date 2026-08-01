# Governance Notes Synchronization Report

- Overall status: `PASS_WITH_REPAIRS`
- Projected entries: `62`
- Canonical sources: global induction queue, induction registry, and intake queue registry
- Generated notes boundary: present and protected
- Traceability validation: `PASS`
- Reconciliation validation: `PASS`
- Idempotence validation: `PASS` (repeated generated-region hash: `2e6acb6c059d888139cc5c6ee98cdfea6dda25ec156cdd794c572240b6631a06`)
- Runtime refresh: not requested in this report

## Explicit pending links

Four queued records do not yet have canonical registry bindings. They remain visible in the generated notes projection as queued/pending rather than being silently discarded:

- `MPF_IND_PROJECTION_DOF_ARCHITECTURE_001`
- `RT_INDUCTION_ATOMIC_VALUE_PROJECTION_001`
- `RT_INDUCTION_RELATIONAL_NECESSITY_ALIGNMENT_002`
- `RT_PROCESS_SEMANTIC_INDEX_001`

These are governance integration conditions, not scientific dispositions. No review, promotion, source-content rewrite, or canonical mathematical change was performed.

## Protection checks

- Manual notes outside the generated markers were preserved byte-for-byte against the pre-sync backup.
- Generated content is deterministically ordered by canonical induction identifier.
- Repeated synchronization against unchanged inputs produces the same generated-region hash.
- The notes projection remains non-authoritative; canonical captures and registries remain authoritative.

Machine-readable details are in [sync_governance_20260801.json](./sync_governance_20260801.json).
