from ._helpers import (
    EXPECTED_INVENTORY_COUNTS,
    EXPECTED_LIVE_AUTHORITY_COUNT,
    EXPECTED_LIVE_AUTHORITY_DIGEST,
    EXPECTED_SUMMARY_COUNTS,
    expected_artifact_hashes,
    load_json,
    live_authority_digest,
    sha256_file,
)


def test_additive_inventory_patch_preserves_live_authority_records():
    patch = load_json("registry/governance/patches/PATCH_GOVERNANCE_GLOBAL_INVENTORY_002.json")
    summary = load_json("outputs/governance_inventory/governance_inventory_summary.json")
    inventory = load_json("outputs/governance_inventory/governance_surface_inventory.json")
    artifact_hashes = expected_artifact_hashes()

    assert patch["patch_mode"] == "ADDITIVE_ONLY"
    assert patch["status"] == "PARTIAL"
    assert patch["authority_effect"]["classification"] == "NONE"
    assert patch["core_rule_reference"]["rule_id"] == "GOVERNANCE_INVENTORY_TRANSITIONAL_EVIDENCE_001"
    assert patch["core_rule_reference"]["hash"] == sha256_file(
        "governance/core_rules/GOVERNANCE_INVENTORY_TRANSITIONAL_EVIDENCE_001.json"
    )

    provenance_records = patch["provenance_records"]
    assert [record["artifact_path"] for record in provenance_records] == [
        "docs/manual_repository_audit_2026_07_13.md",
        "outputs/governance_inventory/governance_surface_inventory.json",
        "outputs/governance_inventory/governance_authority_relationships.json",
        "outputs/governance_inventory/governance_ambiguity_register.json",
        "outputs/governance_inventory/governance_inventory_summary.json",
    ]
    assert [record["provenance_id"] for record in provenance_records] == [
        "GOVINV-PROV-2E8B1A016EE51FB3",
        "GOVINV-PROV-63CE0623B52B47C6",
        "GOVINV-PROV-48E7B3841579FEB7",
        "GOVINV-PROV-57FA240021B4BACC",
        "GOVINV-PROV-1F6A84C25EF5E873",
    ]
    assert [record["artifact_sha256"] for record in provenance_records] == [
        artifact_hashes["docs/manual_repository_audit_2026_07_13.md"],
        artifact_hashes["outputs/governance_inventory/governance_surface_inventory.json"],
        artifact_hashes["outputs/governance_inventory/governance_authority_relationships.json"],
        artifact_hashes["outputs/governance_inventory/governance_ambiguity_register.json"],
        artifact_hashes["outputs/governance_inventory/governance_inventory_summary.json"],
    ]
    assert patch["evidence_set_reference"]["evidence_set_id"] == "GOVERNANCE_GLOBAL_INVENTORY_2026_07_13"
    assert patch["evidence_set_reference"]["authority_effect"] == "NONE"
    assert patch["registration_gate"]["status"] == "PASS"
    assert patch["inventory_completion_gate"]["status"] == "BLOCKED"
    assert patch["inventory_completion_gate"]["blocking_ambiguities"] == 514
    assert patch["patch_gate_transition"]["before"]["failed_preconditions"] == [
        "missing_provenance",
        "missing_core_rule",
        "non_additive_patch_mode",
    ]
    assert patch["patch_gate_transition"]["required_after"]["missing_provenance"] == "RESOLVED"
    assert patch["patch_gate_transition"]["required_after"]["missing_core_rule"] == "RESOLVED"
    assert patch["patch_gate_transition"]["required_after"]["non_additive_patch_mode"] == "RESOLVED"
    assert patch["patch_gate_transition"]["required_after"]["inventory_ambiguity_status"] == "STILL_BLOCKING"
    assert patch["patch_gate_transition"]["expected_gate_result"]["patch_002_registration_gate"] == "PASS"
    assert patch["patch_gate_transition"]["expected_gate_result"]["inventory_completion_gate"] == "BLOCKED"
    assert patch["core_rule_reference"]["hash"] == sha256_file(
        "governance/core_rules/GOVERNANCE_INVENTORY_TRANSITIONAL_EVIDENCE_001.json"
    )

    assert summary["status"] == "PARTIAL"
    assert summary["counts"] == EXPECTED_SUMMARY_COUNTS
    assert summary["runtime_gate"]["patch_gate_status"] == "blocked"
    assert summary["runtime_gate"]["reason"] == "missing_provenance, missing_core_rule, non_additive_patch_mode"
    assert summary["outputs_created"] == [
        "outputs/governance_inventory/governance_surface_inventory.json",
        "outputs/governance_inventory/governance_authority_relationships.json",
        "outputs/governance_inventory/governance_ambiguity_register.json",
        "outputs/governance_inventory/governance_inventory_summary.json",
    ]

    live_count, live_digest = live_authority_digest()
    assert live_count == EXPECTED_LIVE_AUTHORITY_COUNT
    assert live_digest == EXPECTED_LIVE_AUTHORITY_DIGEST
    assert inventory["records"]
    assert len([record for record in inventory["records"] if record["authority_state"] == "PROPOSAL"]) == EXPECTED_INVENTORY_COUNTS["proposals"]
    assert len([record for record in inventory["records"] if record["authority_state"] == "HISTORICAL"]) == EXPECTED_INVENTORY_COUNTS["historical_surfaces"]
    assert len([record for record in inventory["records"] if record["authority_state"] == "GENERATED_VIEW"]) == EXPECTED_INVENTORY_COUNTS["generated_views"]
