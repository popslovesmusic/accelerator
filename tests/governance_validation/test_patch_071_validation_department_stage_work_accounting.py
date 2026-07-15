import json

from scripts.global_validate import EngineValidator, _build_governed_stage_policy, _build_stage_results, _reduce_validation_outcome
from scripts.math import math_program_validate as math_program_validate_module

from ._helpers import load_json, sha256_file


def _trace_entry(stage_name, status, *, work_expectation, work_state, discovered, attempted, completed, reason=None):
    return {
        "stage": stage_name,
        "status": status,
        "failure_class": "none",
        "duration_seconds": 0.01,
        "timed_out": False,
        "error_count": 0,
        "warning_count": 0,
        "result_snapshot": {
            "status": status,
            "warnings": [],
            "errors": [],
            "work_expectation": work_expectation,
            "work_state": work_state,
            "targets_discovered": discovered,
            "targets_attempted": attempted,
            "targets_completed": completed,
            "zero_work_reason": reason,
        },
    }


def test_patch_071_records_stage_contract_determination():
    artifact = load_json("outputs/governance_inventory/validation_department_stage_work_accounting_071.json")

    contracts = artifact["stage_contract_determination"]
    assert contracts["engine_validation"]["work_expectation"] == "CONDITIONALLY_REQUIRED"
    assert contracts["math_program_validation"]["work_expectation"] == "REQUIRED"


def test_patch_071_engine_validation_valid_no_applicable_work(tmp_path):
    manifest_path = tmp_path / "registry" / "governance_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps({"nodes": {"t1": {"type": "tool", "status": "C3", "data": {}}}}), encoding="utf-8")

    result = EngineValidator(tmp_path).run()

    assert result["status"] == "success"
    assert result["work_expectation"] == "CONDITIONALLY_REQUIRED"
    assert result["work_state"] == "VALID_NO_APPLICABLE_WORK"
    assert result["targets_discovered"] == 0
    assert result["targets_completed"] == 0


def test_patch_071_engine_validation_selection_empty_is_not_clean_success(tmp_path):
    manifest_path = tmp_path / "registry" / "governance_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "nodes": {
                    "tool_a": {
                        "type": "tool",
                        "status": "C4",
                        "data": {"name": "tool_a", "entry_point": "tools/tool_a.py"},
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    result = EngineValidator(tmp_path).run()

    assert result["status"] == "warning"
    assert result["tools_tested"] == []
    assert result["work_state"] == "SELECTION_EMPTY"
    assert result["targets_discovered"] == 1
    assert result["targets_selected"] == 0
    assert result["targets_completed"] == 0


def test_patch_071_math_program_validation_reports_completed_work(monkeypatch):
    def fake_run_math_validator(_script):
        return {"fake_validation": {"status": "pass", "warnings": [], "errors": []}}

    monkeypatch.setattr(math_program_validate_module, "run_math_validator", fake_run_math_validator)

    report = math_program_validate_module.validate_math_program(full_report=False)["math_program_validation"]

    assert report["work_expectation"] == "REQUIRED"
    assert report["work_state"] == "WORK_COMPLETED"
    assert report["targets_discovered"] == len(report["validators_run"])
    assert report["targets_attempted"] == len(report["validators_run"])
    assert report["targets_completed"] == len(report["validators_run"])
    assert report["items_checked"] == len(report["validators_run"])
    assert report["items_checked"] > 0


def test_patch_071_required_zero_work_blocks_clean_pass():
    policy = _build_governed_stage_policy("full", ["math_program_validation"])
    stage_results = _build_stage_results(
        [
            _trace_entry(
                "math_program_validation",
                "success",
                work_expectation="REQUIRED",
                work_state="EVALUATION_EMPTY",
                discovered=5,
                attempted=5,
                completed=0,
                reason="No substantive validator results completed.",
            )
        ],
        stage_policy=policy,
    )

    reduction = _reduce_validation_outcome(stage_results, policy)

    assert stage_results[0]["status"] == "EVALUATION_EMPTY"
    assert stage_results[0]["work_state"] == "EVALUATION_EMPTY"
    assert reduction["overall_status"] == "incomplete"
    assert reduction["clean_pass_eligible"] is False


def test_patch_071_conditionally_required_valid_no_work_can_remain_non_blocking():
    policy = _build_governed_stage_policy("full", ["engine_validation"])
    stage_results = _build_stage_results(
        [
            _trace_entry(
                "engine_validation",
                "success",
                work_expectation="CONDITIONALLY_REQUIRED",
                work_state="VALID_NO_APPLICABLE_WORK",
                discovered=0,
                attempted=0,
                completed=0,
                reason="No C4 engine tool surfaces were discovered.",
            )
        ],
        stage_policy=policy,
    )

    reduction = _reduce_validation_outcome(stage_results, policy)

    assert stage_results[0]["status"] == "VALID_NO_APPLICABLE_WORK"
    assert reduction["overall_status"] == "pass"
    assert reduction["clean_pass_eligible"] is True


def test_patch_071_work_accounting_unknown_fails_closed():
    policy = _build_governed_stage_policy("full", ["math_program_validation"])
    stage_results = _build_stage_results(
        [
            _trace_entry(
                "math_program_validation",
                "success",
                work_expectation="REQUIRED",
                work_state="WORK_ACCOUNTING_UNKNOWN",
                discovered=10,
                attempted=10,
                completed=10,
                reason="Work accounting could not be determined.",
            )
        ],
        stage_policy=policy,
    )

    reduction = _reduce_validation_outcome(stage_results, policy)

    assert stage_results[0]["status"] == "WORK_ACCOUNTING_UNKNOWN"
    assert reduction["overall_status"] == "fail"
    assert reduction["clean_pass_eligible"] is False


def test_patch_071_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["outputs/governance_inventory/validation_department_stage_work_accounting_071.json"] == (
        sha256_file("outputs/governance_inventory/validation_department_stage_work_accounting_071.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_VALIDATION_DEPARTMENT_STAGE_WORK_ACCOUNTING_071.json"] == (
        sha256_file("patches/PATCH_VALIDATION_DEPARTMENT_STAGE_WORK_ACCOUNTING_071.json").upper()
    )
    assert hash_registry["hashes"]["registry/governance/patches/PATCH_VALIDATION_DEPARTMENT_STAGE_WORK_ACCOUNTING_071.json"] == (
        sha256_file("registry/governance/patches/PATCH_VALIDATION_DEPARTMENT_STAGE_WORK_ACCOUNTING_071.json").upper()
    )
    assert hash_registry["hashes"]["tests/governance_validation/test_patch_071_validation_department_stage_work_accounting.py"] == (
        sha256_file("tests/governance_validation/test_patch_071_validation_department_stage_work_accounting.py").upper()
    )
