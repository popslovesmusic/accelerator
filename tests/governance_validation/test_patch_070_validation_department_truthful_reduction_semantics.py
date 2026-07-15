from scripts.global_validate import (
    _build_governed_stage_policy,
    _build_stage_results,
    _reduce_validation_outcome,
)

from ._helpers import load_json, sha256_file


def _trace_entry(stage_name, status, *, warnings=None, errors=None, reason=None):
    return {
        "stage": stage_name,
        "status": status,
        "failure_class": "none",
        "duration_seconds": 0.01,
        "timed_out": False,
        "error_count": len(errors or []),
        "warning_count": len(warnings or []),
        "result_snapshot": {
            "status": status,
            "warnings": warnings or [],
            "errors": errors or [],
            "reason": reason,
        },
    }


def test_patch_070_records_authoritative_reduction_surface():
    artifact = load_json("outputs/governance_inventory/validation_department_truthful_reduction_semantics_070.json")

    authority = artifact["authority_surface_determination"]
    assert authority["validation_reduction_authority"]["surface"] == "scripts/global_validate.py"
    assert authority["validation_reduction_authority"]["rule_id"] == "GOVERNANCE_VALIDATION_FAIL_CLOSED_001"


def test_patch_070_all_required_clean_stages_allow_clean_pass():
    policy = _build_governed_stage_policy("full", ["alpha", "beta"])
    stage_results = _build_stage_results(
        [
            _trace_entry("alpha", "success"),
            _trace_entry("beta", "pass"),
        ],
        stage_policy=policy,
    )

    reduction = _reduce_validation_outcome(stage_results, policy)

    assert [entry["status"] for entry in stage_results] == ["PASS", "PASS"]
    assert reduction["overall_status"] == "pass"
    assert reduction["clean_pass_eligible"] is True


def test_patch_070_skipped_required_stage_blocks_clean_pass():
    policy = _build_governed_stage_policy("full", ["alpha", "beta"])
    stage_results = _build_stage_results(
        [
            _trace_entry("alpha", "success"),
            _trace_entry("beta", "skipped", reason="Excluded by validation mode."),
        ],
        stage_policy=policy,
    )

    reduction = _reduce_validation_outcome(stage_results, policy)

    assert stage_results[1]["status"] == "SKIPPED_REQUIRED"
    assert reduction["overall_status"] == "incomplete"
    assert reduction["clean_pass_eligible"] is False
    assert reduction["incomplete_stages"] == ["beta"]


def test_patch_070_missing_required_stage_blocks_clean_pass():
    policy = _build_governed_stage_policy("full", ["alpha", "beta"])
    stage_results = _build_stage_results([_trace_entry("alpha", "success")], stage_policy=policy)

    reduction = _reduce_validation_outcome(stage_results, policy)

    assert reduction["overall_status"] == "incomplete"
    assert reduction["clean_pass_eligible"] is False
    assert reduction["missing_required_stages"] == ["beta"]


def test_patch_070_warning_remains_visible_and_blocks_clean_pass():
    policy = _build_governed_stage_policy("full", ["alpha", "beta"])
    stage_results = _build_stage_results(
        [
            _trace_entry("alpha", "success"),
            _trace_entry("beta", "warning", warnings=["degrading warning"]),
        ],
        stage_policy=policy,
    )

    reduction = _reduce_validation_outcome(stage_results, policy)

    assert stage_results[1]["status"] == "WARNING"
    assert stage_results[1]["failure_summary"] == "degrading warning"
    assert reduction["overall_status"] == "warning"
    assert reduction["clean_pass_eligible"] is False
    assert reduction["degraded_stages"] == ["beta"]


def test_patch_070_conditionally_applicable_not_applicable_can_remain_non_blocking():
    policy = {
        "alpha": {"required": True, "conditionally_applicable": False},
        "beta": {"required": True, "conditionally_applicable": True},
    }
    stage_results = _build_stage_results(
        [
            _trace_entry("alpha", "success"),
            _trace_entry("beta", "not_applicable", reason="Condition not met."),
        ],
        stage_policy=policy,
    )

    reduction = _reduce_validation_outcome(stage_results, policy)

    assert stage_results[1]["status"] == "NOT_APPLICABLE"
    assert reduction["overall_status"] == "pass"
    assert reduction["clean_pass_eligible"] is True


def test_patch_070_unknown_terminal_state_fails_closed():
    policy = _build_governed_stage_policy("full", ["alpha"])
    stage_results = _build_stage_results([_trace_entry("alpha", "mystery_state")], stage_policy=policy)

    reduction = _reduce_validation_outcome(stage_results, policy)

    assert stage_results[0]["status"] == "UNKNOWN_STATUS"
    assert reduction["overall_status"] == "fail"
    assert reduction["clean_pass_eligible"] is False
    assert reduction["unknown_status_stages"] == ["alpha"]


def test_patch_070_report_write_success_does_not_overwrite_validation_result():
    policy = _build_governed_stage_policy("full", ["alpha"])
    stage_results = _build_stage_results(
        [_trace_entry("alpha", "warning", warnings=["degrading warning"])],
        stage_policy=policy,
        include_report_write=True,
        report_path="outputs/audits/global_health_report.json",
    )

    reduction = _reduce_validation_outcome(stage_results, policy)

    assert stage_results[-1]["stage_name"] == "report_write"
    assert stage_results[-1]["status"] == "PASS"
    assert reduction["overall_status"] == "warning"
    assert reduction["clean_pass_eligible"] is False


def test_patch_070_preserves_suspended_full_project_validation_state():
    artifact = load_json("outputs/governance_inventory/validation_department_truthful_reduction_semantics_070.json")

    assert artifact["governed_state_preservation"]["full_project_validation"] == (
        "SUSPENDED_PENDING_VALIDATOR_DEPARTMENT_COMPLETION"
    )
    assert artifact["governed_state_preservation"]["q1_local_queue"] == 0
    assert artifact["governed_state_preservation"]["global_blocking_ambiguities"] == 487


def test_patch_070_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["outputs/governance_inventory/validation_department_truthful_reduction_semantics_070.json"] == (
        sha256_file("outputs/governance_inventory/validation_department_truthful_reduction_semantics_070.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_VALIDATION_DEPARTMENT_TRUTHFUL_REDUCTION_SEMANTICS_070.json"] == (
        sha256_file("patches/PATCH_VALIDATION_DEPARTMENT_TRUTHFUL_REDUCTION_SEMANTICS_070.json").upper()
    )
    assert hash_registry["hashes"]["registry/governance/patches/PATCH_VALIDATION_DEPARTMENT_TRUTHFUL_REDUCTION_SEMANTICS_070.json"] == (
        sha256_file("registry/governance/patches/PATCH_VALIDATION_DEPARTMENT_TRUTHFUL_REDUCTION_SEMANTICS_070.json").upper()
    )
    assert hash_registry["hashes"]["tests/governance_validation/test_patch_070_validation_department_truthful_reduction_semantics.py"] == (
        sha256_file("tests/governance_validation/test_patch_070_validation_department_truthful_reduction_semantics.py").upper()
    )
