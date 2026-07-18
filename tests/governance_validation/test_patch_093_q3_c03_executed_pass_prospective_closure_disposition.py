from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ._helpers import load_json, sha256_file


def _run_query(*args: str) -> dict:
    cmd = [sys.executable, "-m", "scripts.query_governance", *args]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def test_q3_093_t01_t02_t03_closure_set_properties():
    # Load Patch 093 disposition
    disposition = load_json("outputs/governance_inventory/q3_c03_executed_pass_prospective_closure_disposition_093.json")
    closure_set_data = disposition["exact_closure_set"]
    
    # Q3-093-T01: Closure-set cardinality and uniqueness (exactly 23 unique IDs)
    assert closure_set_data["count"] == 23
    assert closure_set_data["unique_count"] == 23
    assert len(set(closure_set_data["global_ambiguity_ids"])) == 23

    # Q3-093-T02: Closure set versus Patch 092 prospective closure set (exact set equality)
    prospective_set = load_json("outputs/governance_inventory/q3_c03_executed_pass_prospective_closure_set_092.json")
    assert set(closure_set_data["global_ambiguity_ids"]) == set(prospective_set["global_ambiguity_ids"])

    # Q3-093-T03: Closure set versus remaining-live and reclassification sets (empty intersection)
    remaining_live = load_json("outputs/governance_inventory/q3_c03_executed_pass_remaining_live_set_092.json")
    reclassification = load_json("outputs/governance_inventory/q3_c03_executed_pass_reclassification_set_092.json")
    
    assert len(set(closure_set_data["global_ambiguity_ids"]).intersection(set(remaining_live["items"]))) == 0
    assert len(set(closure_set_data["global_ambiguity_ids"]).intersection(set(reclassification["items"]))) == 0


def test_q3_093_t04_t05_lookup_and_audit():
    disposition = load_json("outputs/governance_inventory/q3_c03_executed_pass_prospective_closure_disposition_093.json")
    closure_set_ids = disposition["exact_closure_set"]["global_ambiguity_ids"]

    # Q3-093-T04: All targets remain deferred under Patch 091
    prospective_set = load_json("outputs/governance_inventory/q3_c03_executed_pass_prospective_closure_set_092.json")
    for item in prospective_set["items"]:
        assert item["post_091_lookup_decision"] == "defer"

    # Q3-093-T05: Classifier control audit still passes
    audit_data = load_json("outputs/governance_inventory/q3_c03_patch_091_classifier_boundary_audit_092.json")
    assert audit_data["audit_disposition"] == "SUCCESS"
    for control_name, control in audit_data["control_cases"].items():
        if control_name in ["APPLIED record", "ACTIVE record", "APPROVED record", "non-patch PASS-containing record", "AMB-GOV-SURF-0742", "AMB-GOV-SURF-0743"]:
            assert control["post_091_lookup_decision"] == "allow"


def test_q3_093_t06_t07_t08_t09_arithmetic_and_preservation():
    disposition = load_json("outputs/governance_inventory/q3_c03_executed_pass_prospective_closure_disposition_093.json")
    active_queue = load_json("outputs/governance_inventory/q3_post_c03_executed_pass_active_queue_093.json")
    global_updates = load_json("outputs/governance_inventory/q3_c03_executed_pass_global_updates_093.json")

    # Q3-093-T06: Global arithmetic (458 minus 23 equals 435)
    assert disposition["global_accounting_update"]["global_blocking_ambiguities_before"] == 458
    assert disposition["global_accounting_update"]["global_blocking_ambiguities_after"] == 435
    assert global_updates["count_delta"]["global_blocking_ambiguity_count_before"] == 458
    assert global_updates["count_delta"]["global_blocking_ambiguity_count_after"] == 435

    # Q3-093-T07: Q3 nominal arithmetic (50 minus 23 equals 27)
    assert disposition["post_closure_q3_state"]["q3_nominal_queue_before"] == 50
    assert disposition["post_closure_q3_state"]["q3_nominal_queue_after"] == 27
    assert active_queue["queue_counts"]["q3_nominal_before"] == 50
    assert active_queue["queue_counts"]["q3_nominal_after"] == 27

    # Q3-093-T08: Q3 live-unresolved arithmetic (48 minus 23 equals 25)
    assert disposition["post_closure_q3_state"]["q3_live_unresolved_before"] == 48
    assert disposition["post_closure_q3_state"]["q3_live_unresolved_after"] == 25
    assert active_queue["queue_counts"]["q3_live_unresolved_before"] == 48
    assert active_queue["queue_counts"]["q3_live_unresolved_after"] == 25

    # Q3-093-T09: Q1, Q2, Q5-bound, 0742, and 0743 preservation (unchanged)
    assert disposition["preclosure_state"]["q1_local_queue"] == 0
    assert disposition["preclosure_state"]["q2_local_queue"] == 0
    assert disposition["post_closure_q3_state"]["q3_pending_outside_scope_q5_items_before"] == 2
    assert disposition["post_closure_q3_state"]["q3_pending_outside_scope_q5_items_after"] == 2
    
    assert disposition["0742_0743_preservation"]["excluded"] is True
    assert "AMB-GOV-SURF-0742" not in active_queue["resolved_global_ambiguity_ids"]
    assert "AMB-GOV-SURF-0743" not in active_queue["resolved_global_ambiguity_ids"]
    assert "AMB-GOV-SURF-0742" in active_queue["remaining_live_q3_item_ids"]
    assert "AMB-GOV-SURF-0743" in active_queue["remaining_live_q3_item_ids"]


def test_q3_093_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")
    
    files_to_check = [
        "outputs/governance_inventory/q3_c03_executed_pass_prospective_closure_disposition_093.json",
        "outputs/governance_inventory/q3_post_c03_executed_pass_active_queue_093.json",
        "outputs/governance_inventory/q3_c03_executed_pass_global_updates_093.json",
        "tests/governance_validation/test_patch_093_q3_c03_executed_pass_prospective_closure_disposition.py"
    ]
    for filepath in files_to_check:
        assert hash_registry["hashes"][filepath] == sha256_file(filepath).upper()
