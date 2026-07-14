from ._helpers import (
    EXPECTED_AMBIGUITY_RECORD_COUNT,
    EXPECTED_AMBIGUITY_RISK_CLASSIFICATION_PATH,
    EXPECTED_AMBIGUITY_CLASSIFICATION_LOGICAL_SHA256,
    EXPECTED_AMBIGUITY_CLASS_COUNTS,
    EXPECTED_QUEUE_GROUP_COUNTS,
    EXPECTED_REMEDIATION_ORDER_RULE_PATH,
    EXPECTED_REMEDIATION_QUEUE_LOGICAL_SHA256,
    EXPECTED_REMEDIATION_QUEUE_PATH,
    EXPECTED_REMEDIATION_QUEUE_SUMMARY_LOGICAL_SHA256,
    EXPECTED_RESOLUTION_MODE_COUNTS,
    EXPECTED_RISK_DIMENSION_COUNTS,
    EXPECTED_SEVERITY_COUNTS,
    load_json,
    sha256_file,
)
from tools.governance_inventory.remediation_queue import build_remediation_queue_bundle, sort_queue_records


def test_remediation_queue_file_has_stable_total_order():
    data = load_json(EXPECTED_REMEDIATION_QUEUE_PATH)

    assert data["schema_id"] == "governance_remediation_queue_v1"
    assert data["schema_version"] == "1.0.0"
    assert data["record_count"] == EXPECTED_AMBIGUITY_RECORD_COUNT
    assert len(data["records"]) == EXPECTED_AMBIGUITY_RECORD_COUNT
    assert data["logical_hash"] == EXPECTED_REMEDIATION_QUEUE_LOGICAL_SHA256
    assert data["classification_logical_hash"] == EXPECTED_AMBIGUITY_CLASSIFICATION_LOGICAL_SHA256
    assert data["core_rule_reference"]["path"] == EXPECTED_REMEDIATION_ORDER_RULE_PATH
    assert data["core_rule_reference"]["hash"] == sha256_file(EXPECTED_REMEDIATION_ORDER_RULE_PATH)
    assert data["counts"]["queue_groups"] == EXPECTED_QUEUE_GROUP_COUNTS
    assert data["counts"]["severity"] == EXPECTED_SEVERITY_COUNTS
    assert data["counts"]["risk_dimensions"] == EXPECTED_RISK_DIMENSION_COUNTS
    assert data["counts"]["resolution_modes"] == EXPECTED_RESOLUTION_MODE_COUNTS
    assert data["counts"]["ambiguity_class"] == EXPECTED_AMBIGUITY_CLASS_COUNTS

    positions = [record["queue_position"] for record in data["records"]]
    assert positions == list(range(1, EXPECTED_AMBIGUITY_RECORD_COUNT + 1))
    assert len({record["ambiguity_id"] for record in data["records"]}) == EXPECTED_AMBIGUITY_RECORD_COUNT
    assert data["records"][0]["queue_group"] == "Q0_COMPETING_AUTHORITY_AND_WRITE_PATHS"
    assert data["records"][0]["ambiguity_class"] == "COMPETING_LIVE_AUTHORITY"
    assert all(
        record["queue_group"] != "Q2_AUTHORITY_LINEAGE" or record["ambiguity_class"] == "AUTHORITY_LINEAGE_MISSING"
        for record in data["records"]
    )
    assert all(
        record["queue_group"] != "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION"
        or record["ambiguity_class"] in {"LIVE_VERSUS_PROPOSAL_UNCLEAR", "CURRENT_VERSUS_HISTORICAL_UNCLEAR"}
        for record in data["records"]
    )
    assert all(
        record["queue_group"] != "Q4_GENERATED_VIEW_BOUNDARY"
        or record["ambiguity_class"] == "SOURCE_VERSUS_GENERATED_UNCLEAR"
        for record in data["records"]
    )


def test_remediation_queue_builder_is_deterministic_and_matches_sorted_classification():
    queue_one = build_remediation_queue_bundle()
    queue_two = build_remediation_queue_bundle()
    classification = load_json(EXPECTED_AMBIGUITY_RISK_CLASSIFICATION_PATH)
    sorted_classification = sort_queue_records(classification["records"])

    assert queue_one["logical_hash"] == EXPECTED_REMEDIATION_QUEUE_LOGICAL_SHA256
    assert queue_two["logical_hash"] == EXPECTED_REMEDIATION_QUEUE_LOGICAL_SHA256
    assert queue_one["logical_hash"] == queue_two["logical_hash"]
    assert queue_one["classification_logical_hash"] == EXPECTED_AMBIGUITY_CLASSIFICATION_LOGICAL_SHA256
    assert queue_two["classification_logical_hash"] == EXPECTED_AMBIGUITY_CLASSIFICATION_LOGICAL_SHA256
    assert queue_one["counts"]["queue_groups"] == EXPECTED_QUEUE_GROUP_COUNTS
    assert queue_one["counts"]["severity"] == EXPECTED_SEVERITY_COUNTS
    assert queue_one["counts"]["risk_dimensions"] == EXPECTED_RISK_DIMENSION_COUNTS
    assert queue_one["counts"]["resolution_modes"] == EXPECTED_RESOLUTION_MODE_COUNTS
    assert queue_one["counts"]["ambiguity_class"] == EXPECTED_AMBIGUITY_CLASS_COUNTS
    assert [record["ambiguity_id"] for record in queue_one["records"]] == [
        record["ambiguity_id"] for record in queue_two["records"]
    ]
    assert [record["ambiguity_id"] for record in queue_one["records"]] == [
        record["ambiguity_id"] for record in sorted_classification
    ]

