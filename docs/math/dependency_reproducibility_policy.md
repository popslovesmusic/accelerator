# Dependency Reproducibility Policy (AUDIT-002)

This document defines the requirements and procedures for ensuring numerical and validation reproducibility within the Mono-Process Framework.

## 1. Objective
To prevent "silent numerical drift" caused by non-deterministic updates to core libraries (NumPy, SciPy, Pandas, etc.) and to ensure that validation results are consistent across different execution environments.

## 2. Dependency Locking
- **requirements.txt:** Maintains human-readable, high-level dependencies.
- **requirements.lock.txt:** Captures the exact version of every package in the validated research environment. 
- **Rule:** All research claims labeled `implementation_verified` or higher must specify the `requirements.lock.txt` version used.

## 3. Baseline Research Environment (May 13, 2026)
- **Python Version:** 3.14.4
- **Core Numerical Stack:**
  - `numpy==2.4.4`
  - `pandas==3.0.2`
  - `scipy==1.17.1`
  - `networkx==3.6.1`
  - `matplotlib==3.10.9`
- **Validation Stack:**
  - `pytest==9.0.3`
  - `jsonschema==4.26.0`

## 4. Environment Change Protocol
1. Any update to a numerical dependency requires a re-validation of the current math program stability baseline.
2. If numerical results drift beyond the current `operational_stability` thresholds, the change must be rejected or a new stability baseline must be established with explicit governance approval.
3. The `requirements.lock.txt` must be updated only after successful re-validation.

## 5. Governance Constraints
- **Blocking:** Claims of `implementation_verified` are blocked if the execution environment does not match the recorded lockfile or if no lockfile exists.
- **Humility:** Results produced in an un-locked environment must be classified as `provisional` or `exploratory`.
