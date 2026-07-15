from __future__ import annotations

import json
import subprocess
import sys

from ._helpers import load_json
from tools.runtime_authority import build_live_authority_access_inventory, resolve_role_aware_authority


def _run_query(*args: str) -> dict:
    cmd = [sys.executable, "-m", "scripts.query_governance", *args]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def test_patch_079_resolves_only_amb_gov_surf_0875_and_preserves_neighbor_q3_state():
    patch = load_json("patches/PATCH_GOVERNANCE_Q3_RUN_MANIFEST_LIVE_CAMPAIGN_BOUNDARY_RESOLUTION_079.json")
    resolution = load_json("outputs/governance_inventory/q3_run_manifest_live_campaign_boundary_resolution_079.json")
    active_queue = load_json("outputs/governance_inventory/q3_run_manifest_live_campaign_boundary_active_queue_079.json")
    global_update = load_json("outputs/governance_inventory/q3_run_manifest_live_campaign_boundary_global_update_079.json")

    assert patch["resolved_global_ambiguity_ids"] == ["AMB-GOV-SURF-0875"]
    assert patch["role_per_surface"] == {
        "registry/governance/schemas/RUN_MANIFEST_V1.json": "SCHEMA_CONSTRAINT_SURFACE",
        "registry/governance/living_falsification_campaign_registry.json": "REGISTRY_STATE_AUTHORITY",
    }
    assert patch["counts"] == {
        "global_blocking_ambiguity_count_before": 484,
        "global_blocking_ambiguity_count_after": 483,
        "q3_live_unresolved_count_before": 74,
        "q3_live_unresolved_count_after": 73,
        "q3_nominal_queue_before": 76,
        "q3_nominal_queue_after": 75,
    }

    assert resolution["closure_proof"]["ambiguity_resolved"] is True
    assert resolution["closure_proof"]["schema_is_live_campaign_state_authority"] is False
    assert resolution["closure_proof"]["registry_is_only_live_campaign_state_candidate"] is True
    assert resolution["closure_proof"]["historical_or_instantiated_manifests_remain_distinguishable"] is True

    assert active_queue["queue_counts"] == {
        "q3_nominal_before": 76,
        "q3_nominal_after": 75,
        "q3_live_unresolved_before": 74,
        "q3_live_unresolved_after": 73,
        "q3_outside_scope_q5_unchanged": 2,
    }
    assert "AMB-GOV-SURF-0875" not in active_queue["remaining_live_q3_item_ids"]
    assert active_queue["unchanged_outside_scope_q5_item_ids"] == [
        "AMB-GOV-SURF-0776",
        "AMB-GOV-SURF-0868",
    ]

    assert global_update["global_accounting_update"] == {
        "global_blocking_ambiguity_count_before": 484,
        "resolved_in_this_patch": 1,
        "global_blocking_ambiguity_count_after": 483,
    }


def test_patch_079_runtime_authority_boundary_is_explicit_and_fail_closed():
    schema = resolve_role_aware_authority(
        "SCHEMA_CONSTRAINT_SURFACE",
        target="registry/governance/schemas/RUN_MANIFEST_V1.json",
    )
    assert schema["decision"] == "allow"
    assert schema["authority_source"] == "registry/governance/schemas/RUN_MANIFEST_V1.json"

    registry = resolve_role_aware_authority(
        "REGISTRY_STATE_AUTHORITY",
        target="registry/governance/living_falsification_campaign_registry.json",
    )
    assert registry["decision"] == "allow"
    assert registry["authority_source"] == "registry/governance/living_falsification_campaign_registry.json"

    schema_as_registry = resolve_role_aware_authority(
        "REGISTRY_STATE_AUTHORITY",
        target="registry/governance/schemas/RUN_MANIFEST_V1.json",
    )
    assert schema_as_registry["decision"] == "block"
    assert "SCHEMA_CONSTRAINT_SURFACE" in schema_as_registry["warnings"][0]

    registry_as_schema = resolve_role_aware_authority(
        "SCHEMA_CONSTRAINT_SURFACE",
        target="registry/governance/living_falsification_campaign_registry.json",
    )
    assert registry_as_schema["decision"] == "block"
    assert "REGISTRY_STATE_AUTHORITY" in registry_as_schema["warnings"][0]

    inventory = build_live_authority_access_inventory()
    classifications = {record["path"]: record["classification"] for record in inventory["records"]}
    assert classifications["registry/governance/schemas/RUN_MANIFEST_V1.json"] == "SCHEMA_CONSTRAINT_SURFACE"
    assert classifications["registry/governance/living_falsification_campaign_registry.json"] == "REGISTRY_STATE_AUTHORITY"


def test_patch_079_query_behavior_identifies_live_campaign_registry_without_granting_schema_live_state():
    live_query = _run_query(
        "authority",
        "--target",
        "registry/governance/living_falsification_campaign_registry.json",
        "--authority-role",
        "REGISTRY_STATE_AUTHORITY",
        "--level",
        "summary",
        "--json",
    )
    assert live_query["decision"] == "allow"
    assert live_query["authority_source"] == "registry/governance/living_falsification_campaign_registry.json"

    schema_query = _run_query(
        "authority",
        "--target",
        "registry/governance/schemas/RUN_MANIFEST_V1.json",
        "--authority-role",
        "SCHEMA_CONSTRAINT_SURFACE",
        "--level",
        "summary",
        "--json",
    )
    assert schema_query["decision"] == "allow"
    assert schema_query["authority_source"] == "registry/governance/schemas/RUN_MANIFEST_V1.json"

    collapse_attempt = _run_query(
        "authority",
        "--target",
        "registry/governance/schemas/RUN_MANIFEST_V1.json",
        "--authority-role",
        "REGISTRY_STATE_AUTHORITY",
        "--level",
        "summary",
        "--json",
    )
    assert collapse_attempt["decision"] == "block"
    assert "SCHEMA_CONSTRAINT_SURFACE" in collapse_attempt["warnings"][0]
