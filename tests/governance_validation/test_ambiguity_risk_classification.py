from ._helpers import (
    EXPECTED_AMBIGUITY_CLASS_COUNTS,
    EXPECTED_AMBIGUITY_CLASSIFICATION_LOGICAL_SHA256,
    EXPECTED_AMBIGUITY_RECORD_COUNT,
    EXPECTED_AMBIGUITY_RISK_CLASSIFICATION_PATH,
    EXPECTED_QUEUE_GROUP_COUNTS,
    EXPECTED_REMEDIATION_ORDER_RULE_HASH,
    EXPECTED_REMEDIATION_ORDER_RULE_PATH,
    EXPECTED_REMEDIATION_ORDER_RULE_ID,
    EXPECTED_REMEDIATION_QUEUE_LOGICAL_SHA256,
    EXPECTED_RESOLUTION_MODE_COUNTS,
    EXPECTED_RISK_DIMENSION_COUNTS,
    EXPECTED_SEVERITY_COUNTS,
    load_json,
    sha256_file,
)
from tools.governance_inventory.ambiguity_risk import build_ambiguity_risk_classification


def test_ambiguity_risk_classification_file_has_required_shape_and_counts():
    data = load_json(EXPECTED_AMBIGUITY_RISK_CLASSIFICATION_PATH)

    assert data["schema_id"] == "governance_ambiguity_risk_classification_v1"
    assert data["schema_version"] == "1.0.0"
    assert data["record_count"] == EXPECTED_AMBIGUITY_RECORD_COUNT
    assert len(data["records"]) == EXPECTED_AMBIGUITY_RECORD_COUNT
    assert data["logical_hash"] == EXPECTED_AMBIGUITY_CLASSIFICATION_LOGICAL_SHA256
    assert data["core_rule_reference"] == {
        "rule_id": EXPECTED_REMEDIATION_ORDER_RULE_ID,
        "path": EXPECTED_REMEDIATION_ORDER_RULE_PATH,
        "hash": EXPECTED_REMEDIATION_ORDER_RULE_HASH,
    }
    assert data["core_rule_reference"]["hash"] == sha256_file(EXPECTED_REMEDIATION_ORDER_RULE_PATH)
    assert data["counts"]["queue_groups"] == EXPECTED_QUEUE_GROUP_COUNTS
    assert data["counts"]["severity"] == EXPECTED_SEVERITY_COUNTS
    assert data["counts"]["risk_dimensions"] == EXPECTED_RISK_DIMENSION_COUNTS
    assert data["counts"]["resolution_modes"] == EXPECTED_RESOLUTION_MODE_COUNTS
    assert data["counts"]["ambiguity_class"] == EXPECTED_AMBIGUITY_CLASS_COUNTS

    required_fields = {
        "ambiguity_id",
        "source_record_id",
        "ambiguity_class",
        "path_or_table",
        "surface_type",
        "title_or_name",
        "authority_state",
        "storage_state",
        "affected_surfaces",
        "risk_dimensions",
        "risk_score",
        "severity",
        "execution_reachable",
        "execution_reachability_status",
        "write_reachable",
        "write_reachability_status",
        "validation_reachable",
        "validation_reachability_status",
        "authority_candidates",
        "required_evidence",
        "recommended_resolution_mode",
        "queue_group",
        "queue_position",
        "status",
    }
    ambiguity_ids = set()
    queue_positions = []
    for record in data["records"]:
        assert required_fields.issubset(record)
        assert record["status"] == "QUEUED"
        assert 1 <= record["queue_position"] <= EXPECTED_AMBIGUITY_RECORD_COUNT
        queue_positions.append(record["queue_position"])
        assert record["source_record_id"] == record["surface_id"]
        assert record["ambiguity_id"] == f"AMB-{record['source_record_id']}"
        assert record["ambiguity_id"] not in ambiguity_ids
        ambiguity_ids.add(record["ambiguity_id"])

    assert len(ambiguity_ids) == EXPECTED_AMBIGUITY_RECORD_COUNT
    assert sorted(queue_positions) == list(range(1, EXPECTED_AMBIGUITY_RECORD_COUNT + 1))


def test_ambiguity_risk_classification_is_deterministic():
    first = build_ambiguity_risk_classification()
    second = build_ambiguity_risk_classification()

    assert first["record_count"] == EXPECTED_AMBIGUITY_RECORD_COUNT
    assert second["record_count"] == EXPECTED_AMBIGUITY_RECORD_COUNT
    assert first["logical_hash"] == EXPECTED_AMBIGUITY_CLASSIFICATION_LOGICAL_SHA256
    assert second["logical_hash"] == EXPECTED_AMBIGUITY_CLASSIFICATION_LOGICAL_SHA256
    assert first["logical_hash"] == second["logical_hash"]
    assert first["core_rule_reference"]["hash"] == sha256_file(EXPECTED_REMEDIATION_ORDER_RULE_PATH)
    assert second["core_rule_reference"]["hash"] == sha256_file(EXPECTED_REMEDIATION_ORDER_RULE_PATH)
    assert first["counts"] == second["counts"]
    assert first["counts"]["queue_groups"] == EXPECTED_QUEUE_GROUP_COUNTS
    assert first["counts"]["severity"] == EXPECTED_SEVERITY_COUNTS
    assert first["counts"]["risk_dimensions"] == EXPECTED_RISK_DIMENSION_COUNTS
    assert first["counts"]["resolution_modes"] == EXPECTED_RESOLUTION_MODE_COUNTS
