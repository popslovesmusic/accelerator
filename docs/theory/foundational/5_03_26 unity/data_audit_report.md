# Data audit — `5_03_26 unity` (recoverable outputs check)

Scope: `docs/theory/foundational/5_03_26 unity/`

Goal: Verify that “recoverable output” paths referenced by documents in this folder actually exist in the repo under `outputs/`, and flag gaps/mismatches.

Run context:
- Checked on: 2026-05-04
- Repo root: `D:\projects\acellorator`
- Note: This audit does **not** validate scientific correctness; it only checks path existence and obvious metadata completeness.

Excluded per instruction:
- `docs/theory/foundational/5_03_26 unity/continuation_and_constraint_integrated_charter_v2_3.docx`

---

## Summary

- ✅ Found: 6/8 referenced output files exist.
- ❌ Missing: 2/8 referenced output files do **not** exist at the referenced paths.
- ⚠️ Some documents contain empirical-style claims but do not declare `recoverable_outputs` (notably `paper2_empirical_characterization_phase_packets_p_deterministic_relational_pde_system.md`).

---

## Per-document checks (paths referenced → existence)

### `two_threshold_law_biased_transport_rectified.md`

- ✅ `outputs/runs/two_threshold_rectification_2026-05-03/summary_results.csv`
- ✅ `outputs/runs/two_threshold_rectification_2026-05-03/raw_results.csv`

### `engrammatic_handoff_law_biased_transport.md`

- ✅ `outputs/runs/handoff_window_2026-05-03/handoff_results.csv`

### `hysteresis_admissibility_path_dependent_barriers.md`

- ❌ `outputs/runs/hysteresis_admissibility_rectification_2026-05-03/summary_hysteresis.csv` (missing)
- ❌ `outputs/runs/hysteresis_admissibility_rectification_2026-05-03/raw_results.csv` (missing)

Observed nearby artifact in the referenced run directory:
- ✅ `outputs/runs/hysteresis_admissibility_rectification_2026-05-03/hysteresis_rectification_results.csv` (exists)

This suggests a **path/name mismatch** between the paper metadata and the actual emitted artifact filename(s).

### `hysteretic_phase_packets_paper.md`

- ✅ `outputs/runs/phase_packets_2026-05-03/results.csv`
- ⚠️ Metadata field `claim_gate_result` is `"pending"` in the paper; this audit did not check for gate artifacts, only output existence.

### `hysteretic_interference_paper.md`

- ✅ `outputs/runs/hysteretic_interference_2026-05-03/aggregated_results.csv`
- ✅ `outputs/runs/hysteretic_interference_abm_2026-05-03/results_abm_mismatch.csv`

---

## Documents without declared recoverable output paths (flag)

These files appear to function as narrative/theory/working-note material, or as empirical writeups without a standardized `recoverable_outputs` list in their header (at least not in a top-level metadata block):

- `paper2_empirical_characterization_phase_packets_p_deterministic_relational_pde_system.md` (⚠️ empirical writeup; no `recoverable_outputs` list found via string scan for `outputs/runs/` in this folder audit)
- `Phase Packets and M-Law Dynamics.txt`
- `Phase Packets, M-Laws, and Quantum-.txt`
- `The Statement.txt`
- `# Technical Note.txt`
- `MPF_Session_Capture_May2026.docx` (DOCX; not parsed)

This is not “wrong,” but if the intent is that these become book chapters with reproducible claims, they will eventually need either:
- a metadata block with explicit `recoverable_outputs`, or
- explicit references to the papers/runs that carry the evidence.

---

## Recommended fixes (non-destructive)

To resolve the concrete data gaps without changing engine code:

1. Update the paper metadata in `hysteresis_admissibility_path_dependent_barriers.md` to reference the actual emitted artifact(s), or
2. Add a copy/symlink-equivalent (Windows copy) of `hysteresis_rectification_results.csv` to the expected filenames:
   - `summary_hysteresis.csv`
   - `raw_results.csv`

Option (1) is cleaner editorially; option (2) preserves backward references if other documents already cite the older names.

