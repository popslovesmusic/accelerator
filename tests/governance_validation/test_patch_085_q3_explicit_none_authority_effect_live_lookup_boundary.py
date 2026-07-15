from __future__ import annotations

import json
import subprocess
import sys

from ._helpers import load_json
from tools.runtime_authority import classify_patch_record_explicit_none_authority_effect


def _run_query(*args: str) -> dict:
    cmd = [sys.executable, "-m", "scripts.query_governance", *args]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def test_patch_085_artifacts_preserve_non_resolution_accounting():
    resolution = load_json("outputs/governance_inventory/q3_explicit_none_authority_effect_live_lookup_boundary_085.json")
    mechanism = load_json("outputs/governance_inventory/q3_explicit_none_authority_effect_mechanism_evidence_085.json")
    reaudit = load_json("outputs/governance_inventory/q3_amb_0771_post_boundary_reaudit_085.json")

    assert resolution["global_accounting_preservation"] == {
        "global_blocking_ambiguities_before": 460,
        "global_blocking_ambiguities_after": 460,
        "q3_nominal_queue_before": 52,
        "q3_nominal_queue_after": 52,
        "q3_live_unresolved_before": 50,
        "q3_live_unresolved_after": 50,
        "ambiguity_statuses_changed": False,
    }
    assert mechanism["target_record_state"]["global_ambiguity_id"] == "AMB-GOV-SURF-0771"
    assert reaudit["global_ambiguity_id"] == "AMB-GOV-SURF-0771"
    assert reaudit["classification"] == "PROSPECTIVELY_CLOSABLE_AFTER_085"


def test_patch_085_excludes_explicit_none_authority_effect_from_generic_live_lookup():
    target_query = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/PATCH_GOVERNANCE_GLOBAL_INVENTORY_002.json",
        "--level",
        "summary",
        "--json",
    )
    assert target_query["decision"] == "defer"
    assert "authority_effect=NONE" in target_query["reason"]

    explicit_none = classify_patch_record_explicit_none_authority_effect(
        "registry/governance/patches/PATCH_GOVERNANCE_GLOBAL_INVENTORY_002.json"
    )
    assert explicit_none == {
        "target": "registry/governance/patches/PATCH_GOVERNANCE_GLOBAL_INVENTORY_002.json",
        "patch_id": "PATCH_GOVERNANCE_GLOBAL_INVENTORY_002",
        "status": "PARTIAL",
        "authority_effect": {
            "creates_new_governance": False,
            "modifies_live_governance": False,
            "supersedes_existing_governance": False,
            "activates_validation_department": False,
            "classification": "NONE",
        },
        "authority_effect_classification": "NONE",
        "live_lookup_eligible": False,
    }


def test_patch_085_preserves_patch_history_and_non_interference():
    patch_chain = _run_query(
        "patch-chain",
        "--patch-id",
        "PATCH_GOVERNANCE_GLOBAL_INVENTORY_002",
        "--level",
        "summary",
        "--json",
    )
    assert patch_chain["patch_id"] == "PATCH_GOVERNANCE_GLOBAL_INVENTORY_002"

    partial_without_explicit_none = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055.json",
        "--level",
        "summary",
        "--json",
    )
    assert partial_without_explicit_none["decision"] == "allow"

    live_surface_query = _run_query(
        "authority",
        "--target",
        "scripts/global_validate.py",
        "--authority-role",
        "VALIDATION_INVOCATION_AUTHORITY",
        "--level",
        "summary",
        "--json",
    )
    assert live_surface_query["decision"] == "allow"

