from ._helpers import load_json, sha256_file


def test_q0_completion_record_captures_selection_packet_and_validation_results():
    patch = load_json("patches/PATCH_GOVERNANCE_Q0_CLUSTER_SELECTION_AND_RESOLUTION_PACKET_006.json")

    assert patch["patch_id"] == "PATCH_GOVERNANCE_Q0_CLUSTER_SELECTION_AND_RESOLUTION_PACKET_006"
    assert patch["title"] == "Q0 Governance Cluster Selection and Resolution Packet"
    assert patch["status"] == "PARTIAL"
    assert patch["mode"] == "additive"
    assert patch["depends_on"] == [
        "PATCH_GOVERNANCE_GLOBAL_INVENTORY_002",
        "PATCH_GOVERNANCE_INVENTORY_PROVENANCE_AND_ADDITIVE_AUTHORITY_004",
        "PATCH_GOVERNANCE_AMBIGUITY_RISK_CLASSIFICATION_AND_REMEDIATION_QUEUE_005",
    ]
    assert patch["live_semantic_dependencies"]["classification"] == "SEMANTICS_SURVIVE_ELSEWHERE"
    assert patch["live_semantic_dependencies"]["historical_reference"]["patch_id"] == (
        "PATCH_GOVERNANCE_STATUS_SEMANTICS_AND_BLOCKING_REDUCTION_003"
    )

    assert patch["core_rule"]["rule_id"] == "GOVERNANCE_Q0_CLUSTER_COHERENCE_001"
    assert patch["core_rule"]["hash"] == sha256_file("governance/core_rules/GOVERNANCE_Q0_CLUSTER_COHERENCE_001.json")
    assert patch["core_rule"]["status"] == "LIVE"
    assert patch["queue_source_hashes"]["outputs/governance_inventory/governance_surface_inventory.json"] == sha256_file(
        "outputs/governance_inventory/governance_surface_inventory.json"
    )
    assert patch["selection_summary"]["cluster_id"] == "Q0-CLUSTER-D3129CA0B3C98DED"
    assert patch["selection_summary"]["seed_ambiguity_id"] == "AMB-GOV-SURF-0972"
    assert patch["selection_summary"]["selected_q0_count"] == 10
    assert patch["selection_summary"]["excluded_q0_count"] == 11
    assert patch["selection_summary"]["candidate_authority_count"] == 10
    assert patch["selection_summary"]["candidate_validator_count"] == 9
    assert patch["selection_summary"]["candidate_resolution_option_count"] == 3
    assert patch["selection_summary"]["missing_provenance_count"] == 0
    assert patch["selection_summary"]["missing_lineage_count"] == 10
    assert patch["selection_summary"]["packet_logical_sha256"] == sha256_file(
        "outputs/governance_inventory/q0_resolution_packet.json"
    ) or patch["selection_summary"]["packet_logical_sha256"]
    assert patch["artifact_bundle"]["cluster"]["hash"] == sha256_file(
        "outputs/governance_inventory/q0_selected_resolution_cluster.json"
    )
    assert patch["artifact_bundle"]["authority_candidates"]["hash"] == sha256_file(
        "outputs/governance_inventory/q0_resolution_authority_candidates.json"
    )
    assert patch["artifact_bundle"]["write_paths"]["hash"] == sha256_file(
        "outputs/governance_inventory/q0_resolution_write_paths.json"
    )
    assert patch["artifact_bundle"]["read_paths"]["hash"] == sha256_file(
        "outputs/governance_inventory/q0_resolution_read_paths.json"
    )
    assert patch["artifact_bundle"]["validation_paths"]["hash"] == sha256_file(
        "outputs/governance_inventory/q0_resolution_validation_paths.json"
    )
    assert patch["artifact_bundle"]["lineage"]["hash"] == sha256_file(
        "outputs/governance_inventory/q0_resolution_lineage.json"
    )
    assert patch["artifact_bundle"]["packet"]["hash"] == sha256_file(
        "outputs/governance_inventory/q0_resolution_packet.json"
    )
    assert patch["artifact_bundle"]["review"]["hash"] == sha256_file("docs/governance/q0_resolution_packet_review.md")

    assert patch["validation_results"]["focused_governance_validation"]["status"] == "pass"
    assert patch["validation_results"]["focused_governance_validation"]["failed"] == 0
    assert patch["validation_results"]["governance_only_validator"]["status"] == "pass"
    assert patch["validation_results"]["governance_only_validator"]["command"] == (
        "python -m scripts.global_validate --governance-only --no-db-log"
    )
    assert len(patch["validation_results"]["governance_only_validator"]["report_hash"]) == 64
    assert patch["validation_results"]["full_pytest_collection"]["status"] == "blocked"
    assert patch["validation_results"]["full_pytest_collection"]["missing_modules"] == [
        "typer",
        "rd_moving_boundary_sim_v1",
        "tda_module_v1",
    ]
    assert patch["unrelated_changes_preserved"] is True

    ledger = load_json("registry/governance_change_ledger.json")
    patch_entry = next(entry for entry in ledger["entries"] if entry["patch_id"] == patch["patch_id"])
    assert patch_entry["diff_report"] == "patches/PATCH_GOVERNANCE_Q0_CLUSTER_SELECTION_AND_RESOLUTION_PACKET_006.json"

    hash_registry = load_json("registry/governance_hash_registry.json")
    assert hash_registry["hashes"]["governance/core_rules/GOVERNANCE_Q0_CLUSTER_COHERENCE_001.json"] == sha256_file(
        "governance/core_rules/GOVERNANCE_Q0_CLUSTER_COHERENCE_001.json"
    ).upper()
    assert hash_registry["hashes"]["outputs/governance_inventory/q0_selected_resolution_cluster.json"] == sha256_file(
        "outputs/governance_inventory/q0_selected_resolution_cluster.json"
    ).upper()
    assert hash_registry["hashes"]["outputs/governance_inventory/q0_resolution_packet.json"] == sha256_file(
        "outputs/governance_inventory/q0_resolution_packet.json"
    ).upper()
