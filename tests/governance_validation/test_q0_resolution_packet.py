from ._helpers import load_json, sha256_file
from tools.governance_inventory.resolution_packet_builder import build_q0_resolution_packet_bundle


EXPECTED_AUTHORITY_FIELDS = {
    "ambiguity_id",
    "queue_position",
    "surface_id",
    "path",
    "surface_type",
    "current_classification",
    "hash_or_version",
    "declared_scope",
    "claimed_scope",
    "provenance_status",
    "lineage_status",
    "read_reachable",
    "write_reachable",
    "validation_reachable",
    "active_consumer_count",
    "active_writer_count",
    "evidence",
}


def test_q0_resolution_packet_file_has_expected_shape():
    packet = load_json("outputs/governance_inventory/q0_resolution_packet.json")

    assert packet["schema_id"] == "governance_q0_resolution_packet_v1"
    assert packet["schema_version"] == "1.0.0"
    assert packet["patch_id"] == "PATCH_GOVERNANCE_Q0_CLUSTER_SELECTION_AND_RESOLUTION_PACKET_006"
    assert packet["generated_at"] == "2026-07-13T23:15:00-04:00"
    assert packet["cluster_schema_reference"]["cluster_id"] == packet["cluster_summary"]["cluster_id"]
    assert packet["cluster_summary"]["seed_ambiguity_id"] == "AMB-GOV-SURF-0972"
    assert packet["cluster_summary"]["selected_q0_count"] == 10
    assert packet["queue_source_hashes"]["outputs/governance_inventory/governance_surface_inventory.json"] == sha256_file(
        "outputs/governance_inventory/governance_surface_inventory.json"
    )
    assert packet["candidate_inventory_reference"]["record_count"] == 10
    assert packet["authority_candidates"] and len(packet["authority_candidates"]) == 10
    assert [record["surface_id"] for record in packet["authority_candidates"]] == [
        "GOV-SURF-0972",
        "GOV-SURF-0881",
        "GOV-SURF-0994",
        "GOV-SURF-0005",
        "GOV-SURF-0123",
        "GOV-SURF-0001",
        "GOV-SURF-0002",
        "GOV-SURF-0132",
        "GOV-SURF-0134",
        "GOV-SURF-0103",
    ]
    for record in packet["authority_candidates"]:
        assert EXPECTED_AUTHORITY_FIELDS.issubset(record)
        assert record["authority_effect"] if "authority_effect" in record else True
    assert packet["write_path_map"]["record_count"] == 10
    assert packet["read_path_map"]["record_count"] == 10
    assert packet["validation_path_map"]["record_count"] == 9
    assert len(packet["lineage_map"]["relationships"]) == 19
    assert len(packet["lineage_map"]["missing_lineage"]) == 10
    assert len(packet["state_consistency_risks"]) == 4
    assert len(packet["candidate_resolution_options"]) == 3
    assert {option["mode"] for option in packet["candidate_resolution_options"]} == {
        "PROVE_EXCLUSIVE_WRITE_OWNER",
        "SELECT_CANONICAL_AUTHORITY",
        "SEPARATE_AUTHORITY_DOMAINS",
    }
    assert all("preferred" not in option for option in packet["candidate_resolution_options"])
    assert len(packet["required_resolution_tests"]) >= 10
    assert packet["rollback_boundary"]["selected_cluster_id"] == packet["cluster_summary"]["cluster_id"]
    assert packet["provenance_map"]["record_count"] == 10
    assert all(record["authority_effect"] == "NONE" for record in packet["provenance_map"]["records"])
    assert packet["path_map_logical_hashes"]["write"] == packet["write_path_map"]["logical_hash"]
    assert packet["path_map_logical_hashes"]["read"] == packet["read_path_map"]["logical_hash"]
    assert packet["path_map_logical_hashes"]["validation"] == packet["validation_path_map"]["logical_hash"]
    assert packet["path_map_logical_hashes"]["lineage"] == packet["lineage_map"]["logical_hash"]
    assert packet["path_map_logical_hashes"]["provenance"] == packet["provenance_map"]["logical_hash"]


def test_q0_resolution_packet_is_deterministic():
    first = build_q0_resolution_packet_bundle()
    second = build_q0_resolution_packet_bundle()

    assert first["packet"]["logical_hash"] == second["packet"]["logical_hash"]
    assert first["cluster"]["logical_hash"] == second["cluster"]["logical_hash"]
    assert first["candidate_inventory"]["logical_hash"] == second["candidate_inventory"]["logical_hash"]
    assert first["write_path_map"]["logical_hash"] == second["write_path_map"]["logical_hash"]
    assert first["read_path_map"]["logical_hash"] == second["read_path_map"]["logical_hash"]
    assert first["validation_path_map"]["logical_hash"] == second["validation_path_map"]["logical_hash"]
    assert first["lineage_map"]["logical_hash"] == second["lineage_map"]["logical_hash"]
    assert first["provenance_map"]["logical_hash"] == second["provenance_map"]["logical_hash"]

