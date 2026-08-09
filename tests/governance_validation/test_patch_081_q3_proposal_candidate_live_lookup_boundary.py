from __future__ import annotations

import json
import subprocess
import sys

from ._helpers import load_json
from tools.runtime_authority import (
    classify_patch_record_explicit_none_authority_effect,
    classify_patch_record_lifecycle,
)


def _run_query(*args: str) -> dict:
    cmd = [sys.executable, "-m", "scripts.query_governance", *args]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def test_patch_081_preserves_non_resolution_accounting_and_reaudit_set():
    patch = load_json("patches/PATCH_GOVERNANCE_Q3_PROPOSAL_CANDIDATE_LIVE_LOOKUP_BOUNDARY_081.json")
    resolution = load_json("outputs/governance_inventory/q3_proposal_candidate_live_lookup_boundary_081.json")
    mechanism = load_json("outputs/governance_inventory/q3_proposal_candidate_live_lookup_mechanism_evidence_081.json")
    reaudit = load_json("outputs/governance_inventory/q3_proposal_candidate_reaudit_candidate_set_081.json")

    assert patch["counts"] == {
        "global_blocking_ambiguity_count_before": 483,
        "global_blocking_ambiguity_count_after": 483,
        "q3_live_unresolved_count_before": 73,
        "q3_live_unresolved_count_after": 73,
        "q3_nominal_queue_before": 75,
        "q3_nominal_queue_after": 75,
    }
    assert patch["resolved_global_ambiguity_ids"] == []
    assert patch["selected_component"] == "Q3-078-C01"

    assert resolution["global_accounting_preservation"] == {
        "global_blocking_ambiguities_before": 483,
        "global_blocking_ambiguities_after": 483,
        "ambiguity_statuses_changed": False,
        "q1_local_queue": 0,
        "q2_local_queue": 0,
        "q3_nominal_queue": 75,
        "q3_live_unresolved_items": 73,
        "full_project_validation_status": "SUSPENDED_PENDING_VALIDATOR_DEPARTMENT_COMPLETION",
    }
    assert mechanism["proposal_candidate_state_inventory"]["candidate_count"] == 23
    assert reaudit["candidate_count"] == 23


def test_patch_081_excludes_proposal_and_candidate_records_from_generic_live_lookup():
    proposal_query = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/DEBT_VALIDATOR_IMPORT_PATH_001.json",
        "--level",
        "summary",
        "--json",
    )
    assert proposal_query["decision"] == "defer"
    assert "not eligible for live authority lookup" in proposal_query["reason"]

    candidate_query = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/PATCH_PI_MEMORY_TENSOR_RT_005.json",
        "--level",
        "summary",
        "--json",
    )
    assert candidate_query["decision"] == "defer"
    assert "not eligible for live authority lookup" in candidate_query["reason"]

    proposal_state = classify_patch_record_lifecycle("registry/governance/patches/DEBT_VALIDATOR_IMPORT_PATH_001.json")
    assert proposal_state == {
        "target": "registry/governance/patches/DEBT_VALIDATOR_IMPORT_PATH_001.json",
        "patch_id": "DEBT_VALIDATOR_IMPORT_PATH_001",
        "status": "PROPOSED",
        "normalized_status": "proposed",
        "lifecycle_scope": "patch_record",
        "lifecycle_class": "PROPOSAL",
        "live_lookup_eligible": False,
    }

    candidate_state = classify_patch_record_lifecycle("registry/governance/patches/PATCH_PI_MEMORY_TENSOR_RT_005.json")
    assert candidate_state == {
        "target": "registry/governance/patches/PATCH_PI_MEMORY_TENSOR_RT_005.json",
        "patch_id": "PATCH_PI_MEMORY_TENSOR_RT_005",
        "status": "registered_late",
        "normalized_status": "registered_late",
        "lifecycle_scope": "patch_record",
        "lifecycle_class": "CANDIDATE",
        "live_lookup_eligible": False,
    }


def test_patch_081_does_not_change_partial_without_explicit_none_executed_or_historical_lookup_semantics():
    proposal_as_registry = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/DEBT_VALIDATOR_IMPORT_PATH_001.json",
        "--authority-role",
        "REGISTRY_STATE_AUTHORITY",
        "--level",
        "summary",
        "--json",
    )
    assert proposal_as_registry["decision"] == "defer"

    partial_query = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055.json",
        "--level",
        "summary",
        "--json",
    )
    assert partial_query["decision"] == "defer"

    executed_query = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/ECONOMICS_SIGMA_D_EQUIVALENCE_PASS_001.json",
        "--level",
        "summary",
        "--json",
    )
    assert executed_query["decision"] == "defer"

    historical_query = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/PATCH_PI_RT_CALCULUS_005.json",
        "--level",
        "summary",
        "--json",
    )
    assert historical_query["decision"] in ("allow", "defer")

    assert classify_patch_record_lifecycle("registry/governance/patches/PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055.json") is None
    assert (
        classify_patch_record_explicit_none_authority_effect(
            "registry/governance/patches/PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055.json"
        )
        is None
    )
    assert classify_patch_record_lifecycle("registry/governance/patches/ECONOMICS_SIGMA_D_EQUIVALENCE_PASS_001.json") is None
    assert classify_patch_record_lifecycle("registry/governance/patches/PATCH_PI_RT_CALCULUS_005.json") is None
