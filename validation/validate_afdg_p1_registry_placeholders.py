#!/usr/bin/env python3
"""
AFDG Tier P1 Lexicon & Registry Placeholder Validator.
Validates the registry placeholders and metadata schemas for all Tier P1 Appendix F gap patches:
- AFDG_PATCH_004_CONDITIONED_EQUIVALENCE_ROUTING (OQ_COND_002/003 Conditioned Equivalence)
- AFDG_PATCH_006_TRACE_INHERITANCE_METADATA (OQ_RTM_001 Trace Inheritance Metadata)
- AFDG_PATCH_008_RECOUPLING_BRIDGE_PLACEHOLDER (Asymmetric Recoupling & Emergence Placeholder)
- AFDG_PATCH_010_RELATIONAL_CONTROL_SURFACE_PLACEHOLDER (Relational Control Surfaces Placeholder)
"""

import os
import json
import sys

PATCHES_DIR = os.path.join(os.path.dirname(__file__), "..", "patches")

P1_PATCH_FILES = [
    "AFDG_PATCH_004_CONDITIONED_EQUIVALENCE_ROUTING.json",
    "AFDG_PATCH_006_TRACE_INHERITANCE_METADATA.json",
    "AFDG_PATCH_008_RECOUPLING_BRIDGE_PLACEHOLDER.json",
    "AFDG_PATCH_010_RELATIONAL_CONTROL_SURFACE_PLACEHOLDER.json"
]

def validate_p1_placeholders():
    results = {
        "status": "success",
        "patches_validated": [],
        "errors": []
    }

    for patch_filename in P1_PATCH_FILES:
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
    report = validate_p1_placeholders()
    print(json.dumps(report, indent=2))
    if report["status"] != "success":
        sys.exit(1)
    sys.exit(0)
