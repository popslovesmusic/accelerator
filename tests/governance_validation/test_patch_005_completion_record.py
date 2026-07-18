from ._helpers import (
    EXPECTED_AMBIGUITY_CLASS_COUNTS,
    EXPECTED_AMBIGUITY_CLASSIFICATION_LOGICAL_SHA256,
    EXPECTED_AMBIGUITY_RECORD_COUNT,
    EXPECTED_AMBIGUITY_RISK_CLASSIFICATION_PATH,
    EXPECTED_FULL_PYTEST_COLLECTION_BLOCKER,
    EXPECTED_QUEUE_GROUP_COUNTS,
    EXPECTED_QUEUE_SOURCE_SNAPSHOT_LOGICAL_SHA256,
    EXPECTED_REMEDIATION_ORDER_RULE_HASH,
    EXPECTED_REMEDIATION_ORDER_RULE_ID,
    EXPECTED_REMEDIATION_QUEUE_LOGICAL_SHA256,
    EXPECTED_REMEDIATION_QUEUE_PATH,
    EXPECTED_REMEDIATION_QUEUE_REVIEW_PATH,
    EXPECTED_REMEDIATION_QUEUE_SUMMARY_LOGICAL_SHA256,
    EXPECTED_REMEDIATION_QUEUE_SUMMARY_PATH,
    EXPECTED_REMEDIATION_ORDER_RULE_PATH,
    EXPECTED_RESOLUTION_MODE_COUNTS,
    EXPECTED_RISK_DIMENSION_COUNTS,
    EXPECTED_SEVERITY_COUNTS,
    load_json,
    sha256_file,
)


def test_patch_005_completion_record_captures_queue_artifacts_and_validation_results():
    patch = load_json("patches/PATCH_GOVERNANCE_AMBIGUITY_RISK_CLASSIFICATION_AND_REMEDIATION_QUEUE_005.json")

    assert patch["patch_id"] == "PATCH_GOVERNANCE_AMBIGUITY_RISK_CLASSIFICATION_AND_REMEDIATION_QUEUE_005"
    assert patch["title"] == "Governance Ambiguity Risk Classification and Remediation Queue"
    assert patch["status"] == "PARTIAL"
    assert patch["mode"] == "additive"
    assert patch["depends_on"] == [
        "PATCH_GOVERNANCE_GLOBAL_INVENTORY_002",
        "PATCH_GOVERNANCE_INVENTORY_PROVENANCE_AND_ADDITIVE_AUTHORITY_004",
    ]
    assert patch["live_semantic_dependencies"]["classification"] == "SEMANTICS_SURVIVE_ELSEWHERE"
    assert patch["live_semantic_dependencies"]["historical_reference"]["patch_id"] == (
        "PATCH_GOVERNANCE_STATUS_SEMANTICS_AND_BLOCKING_REDUCTION_003"
    )

    assert patch["core_rule"] == {
        "rule_id": EXPECTED_REMEDIATION_ORDER_RULE_ID,
        "path": EXPECTED_REMEDIATION_ORDER_RULE_PATH,
        "hash": EXPECTED_REMEDIATION_ORDER_RULE_HASH,
        "status": "LIVE",
        "scope": "Governance ambiguity classification and remediation queue ordering only.",
        "effect": "Determines the remediation order for ambiguous governance surfaces without resolving any ambiguity or conferring authority.",
        "authority_effect": "NONE",
    }
    assert patch["core_rule"]["hash"] == sha256_file(EXPECTED_REMEDIATION_ORDER_RULE_PATH)

    assert patch["source_snapshot"]["logical_snapshot_sha256"] == EXPECTED_QUEUE_SOURCE_SNAPSHOT_LOGICAL_SHA256
    assert patch["artifact_bundle"]["classification"]["record_count"] == EXPECTED_AMBIGUITY_RECORD_COUNT
    assert patch["artifact_bundle"]["classification"]["logical_hash"] == EXPECTED_AMBIGUITY_CLASSIFICATION_LOGICAL_SHA256
    assert patch["artifact_bundle"]["classification"]["hash"] == sha256_file(EXPECTED_AMBIGUITY_RISK_CLASSIFICATION_PATH)
    assert patch["artifact_bundle"]["queue"]["record_count"] == EXPECTED_AMBIGUITY_RECORD_COUNT
    assert patch["artifact_bundle"]["queue"]["logical_hash"] == EXPECTED_REMEDIATION_QUEUE_LOGICAL_SHA256
    assert patch["artifact_bundle"]["queue"]["hash"] == sha256_file(EXPECTED_REMEDIATION_QUEUE_PATH)
    assert patch["artifact_bundle"]["summary"]["record_count"] == EXPECTED_AMBIGUITY_RECORD_COUNT
    assert patch["artifact_bundle"]["summary"]["summary_logical_sha256"] == EXPECTED_REMEDIATION_QUEUE_SUMMARY_LOGICAL_SHA256
    assert patch["artifact_bundle"]["summary"]["hash"] == sha256_file(EXPECTED_REMEDIATION_QUEUE_SUMMARY_PATH)
    assert patch["artifact_bundle"]["review"]["hash"] == sha256_file(EXPECTED_REMEDIATION_QUEUE_REVIEW_PATH)
    assert len(patch["artifact_bundle"]["summary"]["top_25_queue_records"]) == 25

    assert patch["queue_classification_summary"]["queue_groups"] == EXPECTED_QUEUE_GROUP_COUNTS
    assert patch["queue_classification_summary"]["severity"] == EXPECTED_SEVERITY_COUNTS
    assert patch["queue_classification_summary"]["risk_dimensions"] == EXPECTED_RISK_DIMENSION_COUNTS
    assert patch["queue_classification_summary"]["resolution_modes"] == EXPECTED_RESOLUTION_MODE_COUNTS
    assert patch["queue_classification_summary"]["ambiguity_class"] == EXPECTED_AMBIGUITY_CLASS_COUNTS

    assert patch["patch_002_additive_mode_evidence"] == {
        "patch_id": "PATCH_GOVERNANCE_GLOBAL_INVENTORY_002",
        "path": "registry/governance/patches/PATCH_GOVERNANCE_GLOBAL_INVENTORY_002.json",
        "hash": "57df558e2844f357920664456135aac48d230610a83f4083ccf482a03e17cd10",
        "patch_mode": "ADDITIVE_ONLY",
        "status": "PARTIAL",
        "authority_effect": "NONE",
        "registration_gate": "PASS",
        "inventory_completion_gate": "BLOCKED",
        "blocking_ambiguities": 514,
    }
    assert patch["authority_comparison"] == {
        "pre_patch_live_authority_count": 77,
        "post_patch_live_authority_count": 77,
        "pre_patch_live_authority_digest": "e69d8cd0477cef5fc4b9defc55ca61e7fa5c34945af4ee16e135f72cbe2f6e76",
        "post_patch_live_authority_digest": "e69d8cd0477cef5fc4b9defc55ca61e7fa5c34945af4ee16e135f72cbe2f6e76",
        "live_authority_replacement_detected": False,
        "proposal_status_changes": 0,
        "historical_status_changes": 0,
        "generated_view_status_changes": 0,
        "ambiguity_records_removed": 0,
        "ambiguity_records_resolved": 0,
    }
    assert patch["inventory_counts"] == {
        "total_surfaces": 1083,
        "explicit_live_authorities": 77,
        "proposals": 52,
        "historical_surfaces": 177,
        "superseded_surfaces": 0,
        "generated_views": 587,
        "implied_authorities": 17,
        "conflicting_authorities": 0,
        "authority_unknown": 0,
        "file_authoritative_candidates": 142,
        "database_authoritative_candidates": 4,
        "duplicate_truth_candidates": 0,
        "staleness_rule_surfaces": 9,
        "data_preservation_rule_surfaces": 13,
        "blocking_ambiguities": 514,
    }

    assert patch["validation_results"]["focused_governance_validation"] == {
        "status": "pass",
        "test_count": 9,
        "passed": 9,
        "failed": 0,
    }
    assert patch["validation_results"]["governance_only_global_validate"] == {
        "status": "pass",
        "command": "python -m scripts.global_validate --governance-only --no-db-log",
        "overall_status": "pass",
        "stage_result_count": 14,
        "stale_report_warning": False,
        "report_path": "outputs/audits/global_health_report.json",
        "report_hash": patch["validation_results"]["governance_only_global_validate"]["report_hash"],
    }
    assert patch["validation_results"]["default_global_validate"] == {
        "status": "timeout",
        "command": "python -m scripts.global_validate --no-db-log",
        "timeout_seconds": 600,
    }
    assert patch["validation_results"]["compileall"] == {"status": "pass"}
    assert patch["validation_results"]["git_diff_check"] == {"status": "pass"}
    assert patch["validation_results"]["complete_regression_suite"] == {
        "status": "blocked",
        "collected_tests": 59,
        "collection_errors": 3,
        "missing_modules": EXPECTED_FULL_PYTEST_COLLECTION_BLOCKER,
    }

    assert patch["known_limitations"] == [
        "The inventory completion gate remains blocked by 514 unresolved ambiguities.",
        "The default full-project global validator did not finish within the allotted validation window in this environment.",
        "The full regression suite is blocked during collection by unrelated missing dependencies in this environment.",
        "No inventoried surface gained authority from this patch.",
    ]
    assert patch["unrelated_changes_preserved"] is True
