from __future__ import annotations

import json
import subprocess
import sys

from ._helpers import load_json, sha256_file


def _run_query(*args: str) -> dict:
    cmd = [sys.executable, "-m", "scripts.query_governance", *args]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def test_patch_089_closes_only_amb_0744_with_exact_one_item_accounting():
    patch = load_json("patches/PATCH_GOVERNANCE_Q3_AMB_0744_PROSPECTIVE_CLOSURE_DISPOSITION_089.json")
    disposition = load_json("outputs/governance_inventory/q3_amb_0744_prospective_closure_disposition_089.json")
    active_queue = load_json("outputs/governance_inventory/q3_post_c02_active_queue_089.json")
    global_updates = load_json("outputs/governance_inventory/q3_amb_0744_global_updates_089.json")

    assert patch["resolved_global_ambiguity_ids"] == ["AMB-GOV-SURF-0744"]
    assert patch["counts"] == {
        "global_blocking_ambiguity_count_before": 459,
        "global_blocking_ambiguity_count_after": 458,
        "q3_nominal_queue_before": 51,
        "q3_nominal_queue_after": 50,
        "q3_live_unresolved_count_before": 49,
        "q3_live_unresolved_count_after": 48,
    }

    assert disposition["exact_closure_set"] == {
        "count": 1,
        "global_ambiguity_ids": ["AMB-GOV-SURF-0744"],
        "deferred_outside_set": ["AMB-GOV-SURF-0776", "AMB-GOV-SURF-0868"],
    }
    assert disposition["closure_disposition"] == {
        "global_ambiguity_id": "AMB-GOV-SURF-0744",
        "disposition": "PROSPECTIVELY_CLOSED",
        "authority_effect": "NONE_ON_DISPOSITION_RECORD_ONLY",
        "global_blocking_effect": -1,
        "q3_nominal_queue_effect": -1,
        "q3_live_unresolved_effect": -1,
        "note": "This disposition closes only the ambiguity record. PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055 remains PARTIAL and retains no inferred authority_effect value."
    }
    assert disposition["global_accounting_update"] == {
        "global_blocking_ambiguities_before": 459,
        "global_blocking_ambiguities_after": 458,
        "decrement_reason": "Exactly one individually proven ambiguity, AMB-GOV-SURF-0744, prospectively closed.",
        "double_count_prevented": True,
    }

    assert active_queue["queue_counts"] == {
        "q3_nominal_before": 51,
        "q3_nominal_after": 50,
        "q3_live_unresolved_before": 49,
        "q3_live_unresolved_after": 48,
        "q3_outside_scope_q5_unchanged": 2,
    }
    assert "AMB-GOV-SURF-0744" not in active_queue["remaining_live_q3_item_ids"]
    assert active_queue["unchanged_outside_scope_q5_item_ids"] == ["AMB-GOV-SURF-0776", "AMB-GOV-SURF-0868"]

    assert global_updates["count_delta"] == {
        "global_blocking_ambiguity_count_before": 459,
        "resolved_or_retired_in_this_patch": 1,
        "global_blocking_ambiguity_count_after": 458,
        "q3_group_count_before": 51,
        "q3_group_count_after": 50,
        "q3_live_unresolved_before": 49,
        "q3_live_unresolved_after": 48,
    }
    assert global_updates["updates"] == [
        {
            "global_ambiguity_id": "AMB-GOV-SURF-0744",
            "prior_queue_group": "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION",
            "final_queue_group": None,
            "final_resolution_status": "PROSPECTIVELY_CLOSED",
            "counts_toward_global_blocking_delta": True,
        }
    ]


def test_patch_089_preserves_patch_055_boundary_and_predecessor_authority():
    reaudit = load_json("outputs/governance_inventory/q3_amb_0744_post_boundary_reaudit_088.json")
    patch_055 = load_json("registry/governance/patches/PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055.json")

    assert reaudit["classification"] == "PROSPECTIVELY_CLOSABLE_AFTER_088"
    assert reaudit["independent_remaining_problem"] is None
    assert "authority_effect" not in patch_055
    assert patch_055["status"] == "PARTIAL"

    patch_query = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055.json",
        "--level",
        "summary",
        "--json",
    )
    assert patch_query["decision"] == "defer"
    assert "Closeout/work-package patch records" in patch_query["reason"]

    validate_query = _run_query(
        "authority",
        "--target",
        "scripts/global_validate.py",
        "--authority-role",
        "VALIDATION_INVOCATION_AUTHORITY",
        "--level",
        "summary",
        "--json",
    )
    assert validate_query["decision"] == "allow"

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


def test_patch_089_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["outputs/governance_inventory/q3_amb_0744_prospective_closure_disposition_089.json"] == (
        sha256_file("outputs/governance_inventory/q3_amb_0744_prospective_closure_disposition_089.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q3_post_c02_active_queue_089.json"] == (
        sha256_file("outputs/governance_inventory/q3_post_c02_active_queue_089.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q3_amb_0744_global_updates_089.json"] == (
        sha256_file("outputs/governance_inventory/q3_amb_0744_global_updates_089.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_GOVERNANCE_Q3_AMB_0744_PROSPECTIVE_CLOSURE_DISPOSITION_089.json"] == (
        sha256_file("patches/PATCH_GOVERNANCE_Q3_AMB_0744_PROSPECTIVE_CLOSURE_DISPOSITION_089.json").upper()
    )
    assert hash_registry["hashes"]["registry/governance/patches/PATCH_GOVERNANCE_Q3_AMB_0744_PROSPECTIVE_CLOSURE_DISPOSITION_089.json"] == (
        sha256_file("registry/governance/patches/PATCH_GOVERNANCE_Q3_AMB_0744_PROSPECTIVE_CLOSURE_DISPOSITION_089.json").upper()
    )
    assert hash_registry["hashes"]["tests/governance_validation/test_patch_089_q3_amb_0744_prospective_closure_disposition.py"] == (
        sha256_file("tests/governance_validation/test_patch_089_q3_amb_0744_prospective_closure_disposition.py").upper()
    )
