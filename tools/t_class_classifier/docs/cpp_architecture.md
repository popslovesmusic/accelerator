# C++ Performance Architecture

## 1. Overview
The C++ architecture realizes the performance implementation of the topology classifier. It is optimized for speed, determinism, large batch campaign runs, and binary/byte-stable output matching.

## 2. Directory Structure
- `tools/t_class_classifier/cpp/`
  - `schemas.hpp`: C++ Structs mapping trace representations and matching intermediate types defined in the Python schema.
  - `ingest.cpp`: High-performance JSON parser utilizing `nlohmann/json`.
  - `sanitize.cpp`: Code to filter incoming JSON objects and enforce the negative fixture policy.
  - `feature_extract.cpp`: Fast computation of graph connectivity, loop count, and crossing proxies.
  - `t_signature.cpp`: Constructs the intermediate `T_sig` representation.
  - `classify.cpp`: Decision-tree classifier evaluating `T_sig` parameters.
  - `distribution.cpp`: Generates high-efficiency statistical aggregates over large datasets.
  - `audit.cpp`: Serializes logic checks and verification outputs to the required audit output format.
  - `main.cpp`: CLI wrapper compiling to a standalone binary.

## 3. Strict Compliance Guidelines
- All classification steps must mirror the logic tree defined in `tools/t_class_classifier/python/classify.py`.
- Floating-point calculations must maintain double precision to avoid divergence.
