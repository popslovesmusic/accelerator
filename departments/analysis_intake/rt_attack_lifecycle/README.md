# RT Calculus attack evidence lifecycle

This directory defines the governed receiving-side contract for a future RT Calculus
attack bundle. It is infrastructure only. The current RT bundle remains outside
Analysis Intake until a separate human submission decision is made.

## State separation

```text
RT frozen package
  -> one-way transfer validation
  -> Analysis Intake preservation
  -> one record per FAT attack
  -> replay and review lanes
  -> cross-attack findings
  -> candidate RT actions
  -> separate human RT-induction decision
```

These are distinct states. Intake does not promote a claim, mutate an RT registry,
or execute a campaign. Every preserved file retains its source SHA-256 and the
transfer manifest remains the provenance anchor.

## Receiving contract

The transfer manifest must declare:

- `source_program: RT_CALCULUS`
- `destination_program: ACELLORATOR`
- `direction: RT_CALCULUS_TO_ACELLORATOR_ONLY`
- `reverse_channel: DISABLED`
- an explicit intake status
- a complete relative-path file inventory with SHA-256 and byte size

The validator rejects path traversal, backslashes, hash/size mismatches, reverse
channel declarations, and a missing source manifest. It is read-only and does not
create an intake record.

## Decomposition and review

Each `FAT-N` becomes an independent attack record. Program M observations, Program
S observations, comparative observations, unresolved claims, and blockers remain
separate. A blanket disposition for the whole package is not permitted.

Review records use four lanes:

1. reproducibility — source, environment, inputs, outputs, and hashes;
2. mathematical — standard mathematics and counterexamples;
3. native semantic — fidelity to the frozen RT formulation;
4. independence — separate derivation, implementation, or reviewer.

The claim ceiling is conservative: internal observations are not external claims.
The `C5_external_claim` class is intentionally unavailable to the finding schema.

## Findings and RT-facing actions

Findings synthesize multiple reviewed attack records and remain provisional until
their blockers are resolved. Candidate actions cite findings and are always marked
`NO_AUTOMATIC_RT_MUTATION`.

The successor-attack field is an Acellorator-local research obligation. It may tell
a human what should be tested next, but Acellorator has no automatic write or sync
path back to RT. A new RT run must be created and exported by a human from the RT
workspace under its own provenance and authorization.

## Current boundary

No current RT package, FAT record, finding, or candidate action is inducted by this
infrastructure change. Before a future submission, the RT workspace must freeze a
new package version that includes any later FAT artifacts and produce a new transfer
manifest. An older export must not silently absorb later uncommitted RT changes.
