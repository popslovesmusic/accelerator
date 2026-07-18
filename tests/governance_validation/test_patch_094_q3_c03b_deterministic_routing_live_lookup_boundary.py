from __future__ import annotations

import json
import subprocess
import sys

from ._helpers import load_json


def _run_query(*args: str) -> dict:
    cmd = [sys.executable, "-m", "scripts.query_governance", *args]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def test_patch_094_and_095_counts_and_structures():
    patch_094 = load_json("patches/PATCH_GOVERNANCE_Q3_C03B_DETERMINISTIC_ROUTING_LIVE_LOOKUP_BOUNDARY_094.json")
    patch_095 = load_json("patches/PATCH_GOVERNANCE_Q3_C03B_DETERMINISTIC_ROUTING_PROSPECTIVE_CLOSURE_DISPOSITION_095.json")
    disposition = load_json("outputs/governance_inventory/q3_c03b_prospective_closure_disposition_095.json")
    active_queue = load_json("outputs/governance_inventory/q3_post_c03b_active_queue_095.json")

    assert patch_094["patch_id"] == "PATCH_GOVERNANCE_Q3_C03B_DETERMINISTIC_ROUTING_LIVE_LOOKUP_BOUNDARY_094"
    assert patch_095["patch_id"] == "PATCH_GOVERNANCE_Q3_C03B_DETERMINISTIC_ROUTING_PROSPECTIVE_CLOSURE_DISPOSITION_095"

    assert patch_095["resolved_global_ambiguity_ids"] == ["AMB-GOV-SURF-0742", "AMB-GOV-SURF-0743"]
    assert patch_095["counts"] == {
        "global_blocking_ambiguity_count_before": 435,
        "global_blocking_ambiguity_count_after": 433,
        "q3_nominal_queue_before": 27,
        "q3_nominal_queue_after": 25,
        "q3_live_unresolved_count_before": 25,
        "q3_live_unresolved_count_after": 23,
    }

    assert disposition["exact_closure_set"]["global_ambiguity_ids"] == ["AMB-GOV-SURF-0742", "AMB-GOV-SURF-0743"]
    assert disposition["closure_disposition"]["disposition"] == "PROSPECTIVELY_CLOSED"

    assert active_queue["q3_nominal_queue_after"] == 25
    assert active_queue["q3_live_unresolved_after"] == 23
    assert "AMB-GOV-SURF-0742" not in active_queue["remaining_live_q3_item_ids"]
    assert "AMB-GOV-SURF-0743" not in active_queue["remaining_live_q3_item_ids"]


def test_patch_094_and_095_live_lookup_behavior():
    # Verify both patch records are deferred on live lookup
    for patch_file in (
        "registry/governance/patches/PATCH_ACCELERATOR_DETERMINISTIC_DECISION_CACHE_053.json",
        "registry/governance/patches/PATCH_ACCELERATOR_DETERMINISTIC_ROUTING_AND_CANDIDATE_BOUNDING_054.json"
    ):
        query = _run_query(
            "authority",
            "--target",
            patch_file,
            "--level",
            "summary",
            "--json",
        )
        assert query["decision"] == "defer"
        assert "Deterministic routing component patch records" in query["reason"]

    # Verify that predecessor and implementation surfaces still resolve under their own roles
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
    assert validate_query["authority_owner"] == "runtime"
