from ._helpers import (
    EXPECTED_LOGICAL_SNAPSHOT_SHA256,
    EXPECTED_PROVENANCE_RULE_IDS,
    EXPECTED_SOURCE_SCOPE,
    EXPECTED_SOURCE_SNAPSHOT,
    deterministic_provenance_id,
    expected_artifact_hashes,
    load_json,
)


def test_inventory_provenance_records_are_complete():
    data = load_json("governance/provenance/governance_inventory_2026_07_13_provenance.json")

    assert data["schema_id"] == "governance_inventory_provenance_v1"
    assert data["patch_id"] == "PATCH_GOVERNANCE_INVENTORY_PROVENANCE_AND_ADDITIVE_AUTHORITY_004"
    assert data["status"] == "PARTIAL"
    assert data["authority_effect"] == "NONE"
    assert data["record_count"] == 5

    expected_hashes = expected_artifact_hashes()
    records = data["records"]
    assert len(records) == 5

    for record in records:
        artifact_path = record["artifact_path"]
        artifact_sha256 = record["artifact_sha256"]
        snapshot = record["source_snapshot"]

        assert artifact_path in expected_hashes
        assert artifact_sha256.lower() == expected_hashes[artifact_path].lower()
        assert record["authority_effect"] == "NONE"
        assert record["governing_rule_ids"] == EXPECTED_PROVENANCE_RULE_IDS
        assert record["source_scope"] == EXPECTED_SOURCE_SCOPE
        assert snapshot == EXPECTED_SOURCE_SNAPSHOT
        assert snapshot["logical_snapshot_sha256"] == EXPECTED_LOGICAL_SNAPSHOT_SHA256
        assert record["provenance_id"] == deterministic_provenance_id(
            artifact_path,
            artifact_sha256,
            snapshot["logical_snapshot_sha256"],
        )
        assert record["created_at"] == "2026-07-13T13:02:48.947987+00:00"
        assert record["producer"]
        assert record["production_method"] in {
            "manual review",
            "deterministic scan and classification reduction",
            "classification reduction",
            "deterministic reduction",
        }
