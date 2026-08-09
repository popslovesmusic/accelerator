#!/usr/bin/env python3
"""
AFDG Tier P0 Governor Schema Validator.
Validates the machine-readable schema closure for all 6 Tier P0 Appendix F gap patches:
- AFDG_PATCH_001_GOVERNOR_IO_SCHEMA_FROM_RT_CHAIN (Formal RT Chain Algebra)
- AFDG_PATCH_002_ADMISSIBILITY_CONTEXT_SCHEMA (OQ_001 Scalar Context x)
- AFDG_PATCH_003_CONDITIONING_COMPOSITION_PROTOCOL (OQ_COND_001 Composition Protocol)
- AFDG_PATCH_005_CONTINUATION_ADMISSIBILITY_GATE (OQ_RTM_002 Continuation Admissibility Gate)
- AFDG_PATCH_007_RRE_METRIC_DECLARATION (RRE Hardening Metric Schema)
- AFDG_PATCH_009_OBSERVER_FLOOR_MISMATCH_PLACEHOLDER (Observer-Floor Mismatch Contract)
"""

import os
import json
import sys

PATCHES_DIR = os.path.join(os.path.dirname(__file__), "..", "patches")

P0_PATCH_FILES = [
    "AFDG_PATCH_001_GOVERNOR_IO_SCHEMA_FROM_RT_CHAIN.json",
    "AFDG_PATCH_002_ADMISSIBILITY_CONTEXT_SCHEMA.json",
    "AFDG_PATCH_003_CONDITIONING_COMPOSITION_PROTOCOL.json",
    "AFDG_PATCH_005_CONTINUATION_ADMISSIBILITY_GATE.json",
    "AFDG_PATCH_007_RRE_METRIC_DECLARATION.json",
    "AFDG_PATCH_009_OBSERVER_FLOOR_MISMATCH_PLACEHOLDER.json"
]

def validate_p0_schemas():
    results = {
        "status": "success",
        "patches_validated": [],
        "errors": []
    }

    for patch_filename in P0_PATCH_FILES:
        patch_path = os.path.join(PATCHES_DIR, patch_filename)
        if not os.path.exists(patch_path):
            results["errors"].append(f"Missing required patch file: {patch_filename}")
            results["status"] = "error"
            continue

        try:
            with open(patch_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            patch_id = data.get("patch_id")
            schema = data.get("schema")

            if not patch_id:
                results["errors"].append(f"{patch_filename}: Missing patch_id")
                results["status"] = "error"
            if not schema or not isinstance(schema, dict):
                results["errors"].append(f"{patch_filename}: Missing or invalid schema block")
                results["status"] = "error"

            if "required" not in schema or not isinstance(schema["required"], list):
                results["errors"].append(f"{patch_filename}: Schema missing 'required' array")
                results["status"] = "error"

            results["patches_validated"].append({
                "file": patch_filename,
                "patch_id": patch_id,
                "status": "VALID",
                "required_fields_count": len(schema.get("required", []))
            })

        except Exception as e:
            results["errors"].append(f"Error parsing {patch_filename}: {str(e)}")
            results["status"] = "error"

    return results

if __name__ == "__main__":
    report = validate_p0_schemas()
    print(json.dumps(report, indent=2))
    if report["status"] != "success":
        sys.exit(1)
    sys.exit(0)
