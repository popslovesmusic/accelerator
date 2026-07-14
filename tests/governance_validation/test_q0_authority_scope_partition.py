from tools.governance_inventory import build_q0_authority_scope_partition_bundle


def test_q0_authority_scope_partition_bundle_separates_roles_and_claims():
    bundle = build_q0_authority_scope_partition_bundle()
    partition = bundle["partition"]

    assert partition["schema_id"] == "governance_q0_authority_scope_partition_v1"
    assert partition["schema_version"] == "1.0.0"
    assert partition["patch_id"] == "PATCH_GOVERNANCE_Q0_AUTHORITY_SCOPE_PARTITION_007"
    assert partition["status"] == "PARTITIONED"
    assert partition["authority_effect"] == "LIVE_SCOPE_CONSTRAINT"
    assert partition["cluster_id"] == "Q0-CLUSTER-D3129CA0B3C98DED"
    assert partition["governed_domain_id"] == "governance-validation-control-plane"
    assert partition["validation_partition"]["canonical_invocation"] == "python -m scripts.global_validate"
    assert partition["validation_partition"]["terminal_reducer_rule_id"] == "GOVERNANCE_VALIDATION_FAIL_CLOSED_001"
    assert partition["validation_partition"]["supporting_validator_ids"] == [
        "GOV-SURF-0881",
        "GOV-SURF-0994",
        "GOV-SURF-0005",
        "GOV-SURF-0123",
        "GOV-SURF-0001",
        "GOV-SURF-0002",
        "GOV-SURF-0132",
        "GOV-SURF-0134",
    ]
    assert partition["resolved_ambiguity_count"] == 10
    assert partition["resolved_question_count"] == 12
    assert partition["remaining_blocking_ambiguities"] == 504
    assert partition["summary"]["completion_mode"] == "SEPARATE_NON_OVERLAPPING_SCOPES"
    assert partition["summary"]["resolved_record_count"] == 10
    assert partition["summary"]["resolved_question_count"] == 12
    assert partition["summary"]["remaining_blocking_ambiguities"] == 504
    assert partition["registry_state_partition"]["potential_subpartitions"][3]["scope"] == "INTEGRITY_HASHES"
    assert len(partition["write_owner_assignments"]) == 4
    assert len(partition["instruction_partition"]["instruction_surface_assignments"]) == 5
    assert len(partition["generated_evidence_partition"]["surfaces"]) == 3
    assert len(partition["role_assignments"]) == 11
    assert len(partition["resolved_ambiguity_claims"]) == 12
    assert len(partition["remaining_ambiguity_claims"]) == 504

    roles = {record["surface_id"]: tuple(record["assigned_roles"]) for record in partition["role_assignments"]}
    assert roles["GOV-SURF-0972"] == ("VALIDATION_INVOCATION_AUTHORITY", "VALIDATION_REDUCTION_AUTHORITY")
    assert roles["GOV-SURF-0881"] == ("REGISTRY_STATE_AUTHORITY",)
    assert roles["GOV-SURF-0132"] == ("REGISTRY_STATE_AUTHORITY",)
    assert roles["GOV-SURF-0882"] == ("GENERATED_EVIDENCE",)
    assert roles["GOV-SURF-0994"] == ("GENERATED_EVIDENCE",)
    assert roles["GOV-SURF-0123"] == ("GENERATED_EVIDENCE",)
    assert roles["GOV-SURF-0005"] == ("INSTRUCTION_AUTHORITY",)
    assert roles["GOV-SURF-0001"] == ("INSTRUCTION_AUTHORITY",)
    assert roles["GOV-SURF-0002"] == ("INSTRUCTION_AUTHORITY",)
    assert roles["GOV-SURF-0134"] == ("INSTRUCTION_AUTHORITY",)
    assert roles["GOV-SURF-0103"] == ("INSTRUCTION_AUTHORITY",)

    first_write_owner = partition["write_owner_assignments"][0]
    assert first_write_owner["authorized_writer_id"] == "scripts/governance/register_q0_authority_scope_partition.py"
    assert first_write_owner["authorized_entry_point"] == "python -m scripts.governance.register_q0_authority_scope_partition"

    assert bundle["before_state"]["logical_hash"]
    assert bundle["after_state"]["logical_hash"]
    assert bundle["before_state"]["logical_hash"] != bundle["after_state"]["logical_hash"]
    assert bundle["diff"]["logical_hash"]
    assert bundle["queue_artifact"]["resolved_record_count"] == 10
    assert bundle["queue_artifact"]["resolved_question_count"] == 12
    assert bundle["queue_artifact"]["remaining_record_count"] == 504
    assert bundle["queue_artifact"]["logical_hash"] == build_q0_authority_scope_partition_bundle()["queue_artifact"]["logical_hash"]


def test_q0_authority_scope_partition_artifact_paths_are_stable():
    bundle = build_q0_authority_scope_partition_bundle()

    assert bundle["partition"]["logical_hash"] == build_q0_authority_scope_partition_bundle()["partition"]["logical_hash"]
    assert bundle["partition"]["core_rule_reference"]["path"] == "governance/core_rules/GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001.json"
    assert bundle["partition"]["core_rule_reference"]["rule_id"] == "GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001"
    assert bundle["core_rule"]["source_patch_id"] == "PATCH_GOVERNANCE_Q0_AUTHORITY_SCOPE_PARTITION_007"
