from __future__ import annotations

import json
import subprocess
import sys

from ._helpers import load_json


def _run_query(*args: str) -> dict:
    cmd = [sys.executable, "-m", "scripts.query_governance", *args]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def test_patch_096_and_097_counts_and_structures():
    patch_096 = load_json("patches/PATCH_GOVERNANCE_Q3_C04_HISTORICAL_APPLIED_LIVE_LOOKUP_BOUNDARY_096.json")
    patch_097 = load_json("patches/PATCH_GOVERNANCE_Q3_C04_HISTORICAL_APPLIED_PROSPECTIVE_CLOSURE_DISPOSITION_097.json")
    disposition = load_json("outputs/governance_inventory/q3_c04_prospective_closure_disposition_097.json")
    active_queue = load_json("outputs/governance_inventory/q3_post_c04_active_queue_097.json")

    assert patch_096["patch_id"] == "PATCH_GOVERNANCE_Q3_C04_HISTORICAL_APPLIED_LIVE_LOOKUP_BOUNDARY_096"
    assert patch_097["patch_id"] == "PATCH_GOVERNANCE_Q3_C04_HISTORICAL_APPLIED_PROSPECTIVE_CLOSURE_DISPOSITION_097"

    assert len(patch_097["resolved_global_ambiguity_ids"]) == 23
    assert patch_097["counts"] == {
        "global_blocking_ambiguity_count_before": 433,
        "global_blocking_ambiguity_count_after": 410,
        "q3_nominal_queue_before": 25,
        "q3_nominal_queue_after": 2,
        "q3_live_unresolved_count_before": 23,
        "q3_live_unresolved_count_after": 0,
    }

    assert len(disposition["exact_closure_set"]["global_ambiguity_ids"]) == 23
    assert disposition["closure_disposition"]["disposition"] == "PROSPECTIVELY_CLOSED"

    assert active_queue["q3_nominal_queue_after"] == 2
    assert active_queue["q3_live_unresolved_after"] == 0
    assert not any(gid in active_queue["remaining_live_q3_item_ids"] for gid in patch_097["resolved_global_ambiguity_ids"])


def test_patch_096_and_097_live_lookup_behavior():
    # Verify historical patch records are deferred on live lookup
    for patch_file in (
        "registry/governance/patches/PATCH_PI_RT_CALCULUS_005.json",
        "registry/governance/patches/GOV_WORK_REDUCTION_FRAMEWORK_002.json"
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
        assert "Applied patch records are preserved historical records" in query["reason"]

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
