from ._helpers import EXPECTED_INVENTORY_COUNTS, load_json


def test_patch_002_gate_transition_records_truthful_post_patch_state():
    patch = load_json("registry/governance/patches/PATCH_GOVERNANCE_GLOBAL_INVENTORY_002.json")
    evidence_set = load_json("governance/evidence_sets/GOVERNANCE_GLOBAL_INVENTORY_2026_07_13.json")
    summary = load_json("outputs/governance_inventory/governance_inventory_summary.json")

    assert patch["patch_gate_transition"]["before"]["gate_status"] == "BLOCKED"
    assert patch["patch_gate_transition"]["required_after"]["missing_provenance"] == "RESOLVED"
    assert patch["patch_gate_transition"]["required_after"]["missing_core_rule"] == "RESOLVED"
    assert patch["patch_gate_transition"]["required_after"]["non_additive_patch_mode"] == "RESOLVED"
    assert patch["patch_gate_transition"]["required_after"]["inventory_ambiguity_status"] == "STILL_BLOCKING"
    assert patch["patch_gate_transition"]["required_after"]["inventory_status"] == "PARTIAL"
    assert patch["patch_gate_transition"]["expected_gate_result"]["patch_002_registration_gate"] == "PASS"
    assert patch["patch_gate_transition"]["expected_gate_result"]["inventory_completion_gate"] == "BLOCKED"

    assert evidence_set["record_type"] == "TRANSITIONAL_GOVERNANCE_EVIDENCE_SET"
    assert evidence_set["status"] == "PARTIAL"
    assert evidence_set["authority_effect"] == "NONE"
    assert evidence_set["contains_live_authority"] is False
    assert evidence_set["references_live_authority"] is True
    assert evidence_set["ambiguities_blocking"] is True
    assert evidence_set["eligible_for_governance_replacement"] is False
    assert evidence_set["inventory_counts"] == EXPECTED_INVENTORY_COUNTS
    assert evidence_set["core_rule"]["rule_id"] == "GOVERNANCE_INVENTORY_TRANSITIONAL_EVIDENCE_001"

    assert summary["counts"]["blocking_ambiguities"] == 514
    assert summary["counts"]["explicit_live_authorities"] == 77
    assert summary["counts"]["proposals"] == 52
    assert summary["counts"]["historical_surfaces"] == 177
    assert summary["counts"]["generated_views"] == 587
    assert summary["runtime_gate"]["patch_gate_status"] == "blocked"
