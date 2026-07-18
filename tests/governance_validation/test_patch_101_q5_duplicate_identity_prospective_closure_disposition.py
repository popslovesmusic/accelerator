from __future__ import annotations

import json
import subprocess
import sys

from ._helpers import load_json


def _run_query(*args: str) -> dict:
    cmd = [sys.executable, "-m", "scripts.query_governance", *args]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def test_patch_100_and_101_counts_and_structures():
    patch_100 = load_json("patches/PATCH_GOVERNANCE_Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION_LIVE_LOOKUP_BOUNDARY_100.json")
    patch_101 = load_json("patches/PATCH_GOVERNANCE_Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION_PROSPECTIVE_CLOSURE_DISPOSITION_101.json")
    disposition = load_json("outputs/governance_inventory/q5_duplicate_identity_prospective_closure_disposition_101.json")
    active_queue = load_json("outputs/governance_inventory/q5_post_disposition_active_queue_101.json")

    assert patch_100["patch_id"] == "PATCH_GOVERNANCE_Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION_LIVE_LOOKUP_BOUNDARY_100"
    assert patch_101["patch_id"] == "PATCH_GOVERNANCE_Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION_PROSPECTIVE_CLOSURE_DISPOSITION_101"

    assert len(patch_101["resolved_global_ambiguity_ids"]) == 43
    assert patch_101["counts"] == {
        "global_blocking_ambiguity_count_before": 43,
        "global_blocking_ambiguity_count_after": 0,
        "q5_nominal_queue_before": 43,
        "q5_nominal_queue_after": 0,
        "q5_live_unresolved_count_before": 43,
        "q5_live_unresolved_count_after": 0,
    }

    assert disposition["resolved_count"] == 43
    assert disposition["closure_proof"]["decision"] == "PROSPECTIVELY_CLOSE"

    assert active_queue["queue_counts"] == {
        "before": 43,
        "after": 0
    }
    assert active_queue["queue"] == []


def test_patch_100_and_101_live_lookup_behavior():
    # Verify DB table components are deferred
    query_table = _run_query(
        "authority",
        "--target",
        "registry/db/acellorator_index.sqlite::artifacts",
        "--level",
        "summary",
        "--json",
    )
    assert query_table["decision"] == "defer"
    assert "Database schema components" in query_table["reason"]

    # Verify python bytecode pyc is deferred
    query_pyc = _run_query(
        "authority",
        "--target",
        "scripts/db/__pycache__/db_health_check.cpython-312.pyc",
        "--level",
        "summary",
        "--json",
    )
    assert query_pyc["decision"] == "defer"
    assert "Database schema components" in query_pyc["reason"]

    # Verify build_supersession_edges utility script is deferred
    query_edges = _run_query(
        "authority",
        "--target",
        "scripts/db/build_supersession_edges.py",
        "--level",
        "summary",
        "--json",
    )
    assert query_edges["decision"] == "defer"
    assert "Database schema components" in query_edges["reason"]
