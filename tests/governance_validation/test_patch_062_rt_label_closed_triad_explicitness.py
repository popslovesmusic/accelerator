from ._helpers import load_json, sha256_file


def test_patch_062_records_rt_label_clarification_without_rewriting_rt_core():
    patch = load_json("registry/governance/patches/PATCH_PI_RT_CALCULUS_062.json")
    authority = load_json("docs/governance/rt_real_truth_semantic_authority_062.json")
    report = load_json("outputs/governance_inventory/rt_definition_compliance_report_062.json")

    assert patch["patch_id"] == "PATCH_PI_RT_CALCULUS_062"
    assert patch["status"] == "APPLIED"
    assert patch["rt_core_modified"] is False
    assert patch["core_rule"]["id"] == "RT_LABEL_CLASSIFICATION_062_001"
    assert authority["canonical_definition"]["RT"] == "Real Truth"
    assert authority["canonical_definition"]["non_operator_rule"] == (
        "RT is a classification label and does not itself perform operations."
    )
    assert authority["ultra_short_guard"] == "RT labels closed Real Truth; RT does not perform closure."

    summary = report["classification_summary"]
    assert summary["COMPATIBLE_BY_INHERITANCE"] == 10
    assert summary["AMBIGUOUS_REVIEW_REQUIRED"] == 4
    assert summary["CONFLICTING_REVIEW_REQUIRED"] == 2

    records = {entry["path"]: entry for entry in report["records"]}
    assert records["registry/math/rt_ind_conditioning_001.json"]["classification"] == "CONFLICTING_REVIEW_REQUIRED"
    assert records["governance/live/semantic_contracts/memory_tensor_rt_semantic_contract.json"]["classification"] == (
        "AMBIGUOUS_REVIEW_REQUIRED"
    )
    assert records["departments/physics/department_ssot.md"]["classification"] == "COMPATIBLE_BY_INHERITANCE"


def test_patch_062_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["registry/governance/patches/PATCH_PI_RT_CALCULUS_062.json"] == (
        sha256_file("registry/governance/patches/PATCH_PI_RT_CALCULUS_062.json").upper()
    )
    assert hash_registry["hashes"]["docs/governance/rt_real_truth_semantic_authority_062.json"] == (
        sha256_file("docs/governance/rt_real_truth_semantic_authority_062.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/rt_definition_compliance_report_062.json"] == (
        sha256_file("outputs/governance_inventory/rt_definition_compliance_report_062.json").upper()
    )
