from __future__ import annotations

import json
import subprocess
import sys

from ._helpers import load_json
from tools.runtime_authority import classify_patch_record_closeout_work_package


def _run_query(*args: str) -> dict:
    cmd = [sys.executable, "-m", "scripts.query_governance", *args]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def test_patch_088_artifacts_preserve_non_resolution_accounting():
    resolution = load_json("outputs/governance_inventory/q3_amb_0744_closeout_record_live_lookup_boundary_088.json")
    mechanism = load_json("outputs/governance_inventory/q3_amb_0744_closeout_record_mechanism_evidence_088.json")
    reaudit = load_json("outputs/governance_inventory/q3_amb_0744_post_boundary_reaudit_088.json")

    assert resolution["global_accounting_preservation"] == {
        "global_blocking_ambiguities_before": 459,
        "global_blocking_ambiguities_after": 459,
        "q3_nominal_queue_before": 51,
        "q3_nominal_queue_after": 51,
        "q3_live_unresolved_before": 49,
        "q3_live_unresolved_after": 49,
        "ambiguity_statuses_changed": False,
    }
    assert mechanism["target_contract_reconfirmation"]["global_ambiguity_id"] == "AMB-GOV-SURF-0744"
    assert reaudit["global_ambiguity_id"] == "AMB-GOV-SURF-0744"
    assert reaudit["classification"] == "PROSPECTIVELY_CLOSABLE_AFTER_088"


def test_patch_088_excludes_closeout_record_from_generic_live_lookup():
    target_query = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055.json",
        "--level",
        "summary",
        "--json",
    )
    assert target_query["decision"] == "defer"
    assert "Closeout/work-package patch records" in target_query["reason"]

    closeout_state = classify_patch_record_closeout_work_package(
        "registry/governance/patches/PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055.json"
    )
    assert closeout_state == {
        "target": "registry/governance/patches/PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055.json",
        "patch_id": "PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055",
        "status": "PARTIAL",
        "closeout_recommendation": "PARTIAL",
        "predecessor_patches": [
            "PATCH_ACCELERATOR_CANONICAL_CONTEXT_CAPSULE_050",
            "PATCH_ACCELERATOR_SEMANTIC_READOUT_CAPABILITY_GATE_051",
            "PATCH_ACCELERATOR_INFERENCE_NECESSITY_GATE_052",
            "PATCH_ACCELERATOR_DETERMINISTIC_DECISION_CACHE_053",
            "PATCH_ACCELERATOR_DETERMINISTIC_ROUTING_AND_CANDIDATE_BOUNDING_054",
        ],
        "patches_verified": {
            "050": "PASS",
            "051": "PASS",
            "052": "APPLIED",
            "053": "PASS",
            "054": "PASS",
        },
        "validation_results": {
            "tests_passed": True,
            "schemas_valid": True,
            "registries_valid": True,
            "static_scans_passed": True,
            "governance_validation_passed": True,
            "git_diff_check_passed": True,
            "rollback_proof_passed": True,
        },
        "live_lookup_eligible": False,
    }


def test_patch_088_preserves_patch_history_and_independent_surface_authority():
    patch_chain = _run_query(
        "patch-chain",
        "--patch-id",
        "PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055",
        "--level",
        "summary",
        "--json",
    )
    assert patch_chain["patch_id"] == "PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055"

    inventory_query = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/PATCH_GOVERNANCE_GLOBAL_INVENTORY_002.json",
        "--level",
        "summary",
        "--json",
    )
    assert inventory_query["decision"] == "defer"
    assert "authority_effect=NONE" in inventory_query["reason"]

    global_validate_query = _run_query(
        "authority",
        "--target",
        "scripts/global_validate.py",
        "--authority-role",
        "VALIDATION_INVOCATION_AUTHORITY",
        "--level",
        "summary",
        "--json",
    )
    assert global_validate_query["decision"] == "allow"

    query_surface = _run_query(
        "authority",
        "--target",
        "scripts/query_governance.py",
        "--authority-role",
        "ROLE_AWARE_AUTHORITY_QUERY_SURFACE",
        "--level",
        "summary",
        "--json",
    )
    assert query_surface["decision"] == "allow"

