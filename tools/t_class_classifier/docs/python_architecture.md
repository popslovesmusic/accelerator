# Python Reference Architecture

## 1. Overview
The Python reference architecture is an audit-friendly, readable, and schema-first implementation of the topology classifier. Its main role is to provide a reference design that prioritizes traceability, clear JSON I/O, debug reports, and validation fixtures.

## 2. Directory Structure
- `tools/t_class_classifier/python/`
  - `schemas.py`: Structural definitions using `pydantic` or standard dataclasses. Includes schemas for `T_sig` and `T_class`.
  - `ingest.py`: Parses input JSON files containing realized closure traces.
  - `sanitize.py`: Filters input dictionary and strips forbidden fields (`C_orient`, `-(i)`, `𝒪`, `S_closure`, etc.).
  - `feature_extract.py`: Computes topological indicators from trace (loop count, connectivity preservation, braid proxy index).
  - `t_signature.py`: Constructs the intermediate `T_sig` object.
  - `classify.py`: Implements the topological organization classification rules ($T_0 \to T_x$) based on `T_sig`.
  - `distribution.py`: Computes distribution summaries for batched traces.
  - `audit.py`: Generates the decision trace and outputs the audit report in Markdown format.
  - `main.py`: Command line entry point orchestrating the steps.

## 3. Strict Compliance Guidelines
- No imports from or coupling to orientation dynamics libraries.
- Verification logic must not utilize `C_orient` or its variants.
- Execution steps are strictly sequential and non-overlapping.
