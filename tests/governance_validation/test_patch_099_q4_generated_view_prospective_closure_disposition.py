from __future__ import annotations

import json
import subprocess
import sys

from ._helpers import load_json


def _run_query(*args: str) -> dict:
    cmd = [sys.executable, "-m", "scripts.query_governance", *args]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def test_patch_098_and_099_counts_and_structures():
    patch_098 = load_json("patches/PATCH_GOVERNANCE_Q4_GENERATED_VIEW_LIVE_LOOKUP_BOUNDARY_098.json")
    patch_099 = load_json("patches/PATCH_GOVERNANCE_Q4_GENERATED_VIEW_PROSPECTIVE_CLOSURE_DISPOSITION_099.json")
    disposition = load_json("outputs/governance_inventory/q4_generated_view_prospective_closure_disposition_099.json")
    active_queue = load_json("outputs/governance_inventory/q4_post_disposition_active_queue_099.json")

    assert patch_098["patch_id"] == "PATCH_GOVERNANCE_Q4_GENERATED_VIEW_LIVE_LOOKUP_BOUNDARY_098"
    assert patch_099["patch_id"] == "PATCH_GOVERNANCE_Q4_GENERATED_VIEW_PROSPECTIVE_CLOSURE_DISPOSITION_099"

    assert len(patch_099["resolved_global_ambiguity_ids"]) == 367
    assert patch_099["counts"] == {
        "global_blocking_ambiguity_count_before": 412,
        "global_blocking_ambiguity_count_after": 45,
        "q4_nominal_queue_before": 367,
        "q4_nominal_queue_after": 0,
        "q4_live_unresolved_count_before": 367,
        "q4_live_unresolved_count_after": 0,
    }

    assert disposition["resolved_count"] == 367
    assert disposition["closure_proof"]["decision"] == "PROSPECTIVELY_CLOSE"

    assert active_queue["queue_counts"] == {
        "before": 367,
        "after": 0
    }
    assert active_queue["queue"] == []


def test_patch_098_and_099_live_lookup_behavior():
    # Verify generated audit files are deferred on live lookup
    query_audit = _run_query(
        "authority",
        "--target",
        "outputs/audits/ai_db_retrieval_path_audit_2026_07_03.json",
        "--level",
        "summary",
        "--json",
    )
    assert query_audit["decision"] == "defer"
    assert "Generated output views" in query_audit["reason"]

    # Verify db schema.sql is deferred
    query_schema = _run_query(
        "authority",
        "--target",
        "registry/db/schema.sql",
        "--level",
        "summary",
        "--json",
    )
    assert query_schema["decision"] == "defer"
    assert "DB schema definitions" in query_schema["reason"]

    # Verify current_state_002.sql is allowed
    query_state = _run_query(
        "authority",
        "--target",
        "registry/db/migrations/20260703_governance_runtime_current_state_002.sql",
        "--level",
        "summary",
        "--json",
    )
    assert query_state["decision"] == "allow"
