# `oneproc` Lexicon Governance

`oneproc` implements a deterministic sidecar resolution system for the project lexicon. This ensures that every research claim is grounded in verified Process Primitives.

## 1. Resolution Rules (`lexicon_rules_sidecar.json`)
The CLI follows a strict priority order when resolving terms:
1.  **Exact Canonical Match:** Term matches an entry in `lexicon_canonical.json`.
2.  **Approved Alias Match:** Term matches an alias in `lexicon_alias_map.json`.
3.  **Primitive Rewrite Match:** (Proposed) Decomposes derived terms into core primitives.
4.  **New Gap Term:** Unknown terms are automatically routed to the `lexicon_gap_queue.json` as `GAP_OPEN`.

## 2. Claim Ceilings
Terminology validation level directly constrains the maximum claim rigor:

| Status | Claim Ceiling |
| :--- | :--- |
| **GAP_OPEN** | `proposed_interpretation` |
| **L0** | `provisional` |
| **L1** | `partially_supported` |
| **L2** | `partially_supported_with_limits` |
| **L3** | `supported` |

## 3. Lexicon Commands

### Resolve Terms
```bash
python -m oneproc lexicon resolve epsilon unknown_term
```

### Audit Registry
Detect orphan aliases or missing validation entries:
```bash
python -m oneproc lexicon audit
```

### Take Snapshot
Capture the current rolling state of the lexicon:
```bash
python -m oneproc lexicon snapshot --run-id "RUN-001"
```

## 4. History and Snapshots
- **`lexicon_latest_snapshot.json`**: Current resolved state.
- **`lexicon_run_history.jsonl`**: Append-only log of all lexicon snapshots and changes.
