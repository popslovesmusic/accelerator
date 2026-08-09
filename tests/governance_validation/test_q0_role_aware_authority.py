from tools.runtime_authority import (
    build_live_authority_access_inventory,
    resolve_role_aware_authority,
    validate_validator_partition,
    validate_write_boundary,
)


def test_role_aware_authority_requires_matching_role():
    blocked = resolve_role_aware_authority(
        "REGISTRY_STATE_AUTHORITY",
        target="scripts/global_validate.py",
    )
    assert blocked["decision"] == "block"
    assert "VALIDATION_INVOCATION_AUTHORITY" in blocked["warnings"][0]

    allowed = resolve_role_aware_authority(
        "VALIDATION_INVOCATION_AUTHORITY",
        target="scripts/global_validate.py",
    )
    assert allowed["decision"] == "allow"


def test_write_boundary_and_reducer_partition_are_fail_closed():
    validation = validate_validator_partition()
    assert validation["decision"] == "allow"

    allowed = validate_write_boundary(
        "CHANGE_HISTORY",
        "APPEND",
        "scripts/governance/register_q0_authority_scope_partition.py",
        {"entry": "ok"},
        "pytest",
    )
    assert allowed["decision"] == "allow"

    blocked = validate_write_boundary(
        "CHANGE_HISTORY",
        "DELETE",
        "scripts/governance/register_q0_authority_scope_partition.py",
        {"entry": "bad"},
        "pytest",
    )
    assert blocked["decision"] == "block"
    assert "operation_outside_writer_contract" in blocked["blockers"]


def test_live_authority_access_inventory_covers_primary_targets():
    inventory = build_live_authority_access_inventory()
    paths = {record["path"] for record in inventory["records"]}
    assert "scripts/query_governance.py" in paths
    assert "scripts/global_validate.py" in paths
