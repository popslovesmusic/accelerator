# Reproducibility Report

## Reproducibility Audit Summary

This report evaluates the reproducibility of the attack campaigns (FAT-01 through FAT-24) contained in this independent attack workspace.

* **Audit Date:** 2026-08-04
* **Operating System:** Windows 11 (Powershell)
* **Python Version:** Python 3.12
* **Verification Status:** `PARTIAL` (FAT-22 has an immutable captured replay; historical legacy attacks and independent verification remain pending).

---

## Campaign Reproducibility Classifications

| Campaign ID | Status | Execution Command | Output Paths | Notes / Missing Metadata |
| :--- | :--- | :--- | :--- | :--- |
| **FAT-01 through FAT-13** | `PARTIAL` | `python campaigns/attack_01_axiom_1_2_1.py` etc. | None | Lack environment records, exit codes, and stdout/stderr logs. |
| **FAT-14** | `VERIFIED` | `python campaigns/attack_14_relational_cluster_5_z_1.py` | None | Replay verifies the reported clique boundary contradiction. |
| **FAT-15 through FAT-24** | `PARTIAL` | `python campaigns/attack_15_process_priority.py` etc. | `run_outputs/` | Run logger is integrated, but only FAT-22 currently has a captured validation run; same-script dual comparison is not independent verification. |

---

## Reproducibility Improvements Completed

1. **Run Logger Integration:** Created [run_logger.py](file:///d:/projects/RT%20calculus/campaigns/run_logger.py) to write run outputs to immutable, timestamped run directories under `run_outputs/` instead of overwriting historical files.
2. **Latest Pointer Configuration:** Introduced `latest_run_pointer.json` to point to the latest run directory for convenience without overwriting.
3. **Dependency Lock:** Added `requirements.lock`; new run records include its SHA-256 digest.
4. **Package Refresh:** Rebuilt the visible frozen snapshot after the reproducibility repairs. The package remains `NOT_SUBMITTED`.

---

## Validation Run Verification (GATE_RUN_CAPTURE_OPERATIONAL_001)

* **Date of Validation:** 2026-08-04
* **Validation Attack ID:** `FAT-22-ADMISSIBILITY-FIELD-CAUSAL-LIMIT`
* **Validation Run ID:** `RUN-FAT-22-ADMISSIBILITY-FIELD-CAUSAL-LIMIT-20260804164300-0462c3b6`
* **Validation Run Path:** [RUN-FAT-22-ADMISSIBILITY-FIELD-CAUSAL-LIMIT-20260804164300-0462c3b6](file:///D:/projects/RT%20calculus/run_outputs/FAT-22-ADMISSIBILITY-FIELD-CAUSAL-LIMIT/RUN-FAT-22-ADMISSIBILITY-FIELD-CAUSAL-LIMIT-20260804164300-0462c3b6)
* **Source SHA-256:** `41a87a3eb5ca2c87eeaa4ac786c3ac65e35c8ab0e1426ee95fdb2672e80ee807`
* **Configuration Status:** `NO_CONFIGURATION` (Hash: `0cf83551a03069efd7195a50d6127e206e0757d599ef762685f7c6326adb03b7`)
* **Input Status:** `NO_EXTERNAL_INPUTS` (Hash: `e3506c8da626a821a659c99bed410b4767da7e0f769de20b26b82c8988dd6b0a`)
* **Stdout SHA-256:** `9165cc1a88be080416cfb0b4763e0e7a2bcfc0e254fd267a14cc1c2541dd6b3f` (captured in `stdout.txt`)
* **Stderr SHA-256:** `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty `stderr.txt`)
* **Outputs Generated:** `outputs.json` (Hash: `d6780207e35d7a3111eae471265fa7d00e506a3c1afac7351e04ddd2677491ee`)
* **Exit Code:** `0`
* **Replay Comparison:** `MATCH` (output matches the historical packet structure and outcome classification `SURVIVED_SPECIFIED_ATTACK` exactly).
* **Overwrite Protection Test:** `PASSED` (subsequent attempt to initialize same run dir raises a `FileExistsError`).
* **Gate Status (GATE_RUN_CAPTURE_OPERATIONAL_001):** **PASSED**
* **Package Intake Status:** **NOT_SUBMITTED**
