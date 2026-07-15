from scripts.query_governance import build_patch_chain_result, normalize_patch_chain_status

from ._helpers import load_json, sha256_file


def test_partial_patch_status_is_retained_for_runtime_dependency_reduction():
    assert normalize_patch_chain_status("PARTIAL") == "partial"

    patch_002 = build_patch_chain_result("PATCH_GOVERNANCE_GLOBAL_INVENTORY_002")
    assert patch_002["status"] == "partial"
    assert patch_002["decision"] == "defer"
    assert patch_002["blockers"] == []


def test_q0_chain_uses_existing_evidence_dependencies_for_patch_002():
    patch_007 = build_patch_chain_result("PATCH_GOVERNANCE_Q0_AUTHORITY_SCOPE_PARTITION_007")
    patch_008 = build_patch_chain_result("PATCH_GOVERNANCE_MISSING_DEPENDENCY_003_CHAIN_REPAIR_008")

    assert "dependency_chain_not_satisfied" not in patch_007["blockers"]
    assert "dependency_chain_not_satisfied" not in patch_008["blockers"]
    assert patch_007["status"] == "partial"
    assert patch_008["status"] == "partial"
    assert patch_007["dependency_evaluation"][0] == {
        "patch_id": "PATCH_GOVERNANCE_GLOBAL_INVENTORY_002",
        "requirement_type": "REQUIRES_EXISTING_EVIDENCE",
        "satisfied": True,
        "dependency_status": "partial",
        "dependency_decision": "defer",
    }


def test_patch_009_registers_inventory_and_runtime_artifacts():
    inventory = load_json("outputs/governance_inventory/patch_002_dependency_edge_inventory.json")
    patch = load_json("patches/PATCH_GOVERNANCE_PATCH_002_TYPED_DEPENDENCY_RUNTIME_009.json")

    assert inventory["classification"]["runtime_behavior_before_repair"] == [
        "DEPENDENCY_TYPE_COLLAPSE",
        "STATUS_SEMANTIC_COLLAPSE",
    ]
    assert inventory["dependency_model"]["proven_q0_type_for_patch_002"] == "REQUIRES_EXISTING_EVIDENCE"
    assert patch["patch_id"] == "PATCH_GOVERNANCE_PATCH_002_TYPED_DEPENDENCY_RUNTIME_009"
    assert patch["diagnosis"]["primary"] == "DEPENDENCY_TYPE_COLLAPSE"
    assert patch["dependency_requirements"]["PATCH_GOVERNANCE_GLOBAL_INVENTORY_002"]["type"] == (
        "REQUIRES_EXISTING_EVIDENCE"
    )

    hash_registry = load_json("registry/governance_hash_registry.json")
    assert hash_registry["hashes"]["outputs/governance_inventory/patch_002_dependency_edge_inventory.json"] == (
        sha256_file("outputs/governance_inventory/patch_002_dependency_edge_inventory.json").upper()
    )
