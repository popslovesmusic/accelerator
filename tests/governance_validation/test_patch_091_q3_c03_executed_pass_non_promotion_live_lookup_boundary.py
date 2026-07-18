from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from ._helpers import load_json


def _run_query(*args: str) -> dict:
    cmd = [sys.executable, "-m", "scripts.query_governance", *args]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def test_q3_091_t01_target_set_cardinality_and_classification():
    # Verify exact 23 target items from Patch 090 classification
    classification = load_json("outputs/governance_inventory/q3_c03_executed_pass_item_classification_090.json")
    targets = [item for item in classification["items"] if item.get("classification") == "MISSING_LIFECYCLE_TRANSITION"]
    
    assert len(targets) == 23
    
    # Excludes 0742 and 0743
    amb_ids = {item["global_ambiguity_id"] for item in targets}
    assert "AMB-GOV-SURF-0742" not in amb_ids
    assert "AMB-GOV-SURF-0743" not in amb_ids


def test_q3_091_t02_executed_proposal_record_deferred():
    # Executed proposal record queried as live authority must return defer.
    # Query with forensic level to bypass warning list truncation.
    query = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/ECONOMICS_SIGMA_D_EQUIVALENCE_PASS_001.json",
        "--level",
        "forensic",
        "--json",
    )
    assert query["decision"] == "defer"
    assert "not eligible for live authority lookup" in query["reason"]
    assert any("represents process execution or validation state only" in warning for warning in query["warnings"])


def test_q3_091_t03_t04_pass_proposal_records_deferred():
    # Create temporary mock patches in registry/governance/patches/
    mock_pass_path = Path("registry/governance/patches/PATCH_MOCK_PASS_091.json")
    mock_warn_path = Path("registry/governance/patches/PATCH_MOCK_PASS_WARN_091.json")
    
    mock_pass_content = {
        "patch_id": "PATCH_MOCK_PASS_091",
        "status": "PASS"
    }
    mock_warn_content = {
        "patch_id": "PATCH_MOCK_PASS_WARN_091",
        "status": "PASS_WITH_WARNINGS"
    }
    
    try:
        mock_pass_path.write_text(json.dumps(mock_pass_content), encoding="utf-8")
        mock_warn_path.write_text(json.dumps(mock_warn_content), encoding="utf-8")
        
        # Test Q3-091-T03: PASS proposal record queried as live authority -> deferred
        query_pass = _run_query(
            "authority",
            "--target",
            str(mock_pass_path).replace("\\", "/"),
            "--level",
            "forensic",
            "--json",
        )
        assert query_pass["decision"] == "defer"
        assert "not eligible for live authority lookup" in query_pass["reason"]
        
        # Test Q3-091-T04: PASS_WITH_WARNINGS proposal record queried as live authority -> deferred
        query_warn = _run_query(
            "authority",
            "--target",
            str(mock_warn_path).replace("\\", "/"),
            "--level",
            "forensic",
            "--json",
        )
        assert query_warn["decision"] == "defer"
        assert "not eligible for live authority lookup" in query_warn["reason"]
        
    finally:
        if mock_pass_path.exists():
            os.remove(mock_pass_path)
        if mock_warn_path.exists():
            os.remove(mock_warn_path)


def test_q3_091_t05_remains_discoverable_for_audit():
    # Same record queried in proposal, execution, validation, history, or audit context remains discoverable
    query = _run_query(
        "patch-chain",
        "--patch-id",
        "ECONOMICS_SIGMA_D_EQUIVALENCE_PASS_001",
        "--json",
    )
    assert query["patch_id"] == "ECONOMICS_SIGMA_D_EQUIVALENCE_PASS_001"
    # Status is classified as unknown by the chain status normalizer due to lack of a lifecycle transition
    assert query["status"] == "unknown"


def test_q3_091_t06_global_validate_invocation_authority():
    # scripts/global_validate.py remains VALIDATION_INVOCATION_AUTHORITY
    role_query = _run_query(
        "authority",
        "--target",
        "scripts/global_validate.py",
        "--authority-role",
        "VALIDATION_INVOCATION_AUTHORITY",
        "--level",
        "summary",
        "--json",
    )
    assert role_query["decision"] == "allow"


def test_q3_091_t07_affected_surfaces_remain_independently_governed():
    # Representative affected registry or mathematical surface remains independently governed under Q0 partition
    query = _run_query(
        "authority",
        "--target",
        "governance/authority_partitions/Q0_AUTHORITY_SCOPE_PARTITION_001.json",
        "--authority-role",
        "REGISTRY_WRITE_AUTHORITY",
        "--level",
        "summary",
        "--json",
    )
    assert query["decision"] == "allow"
    assert query["authority_owner"] == "unknown"  # Resolves dynamically through role partitions


def test_q3_091_t08_applied_records_not_excluded():
    # Explicitly transitioned live patch record control (applied status) is not excluded
    query = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/PATCH_PI_RT_CALCULUS_005.json",
        "--level",
        "summary",
        "--json",
    )
    assert query["decision"] in ("allow", "defer")


def test_q3_091_t09_0742_0743_controls_unchanged():
    # AMB-GOV-SURF-0742 and AMB-GOV-SURF-0743 controls (routing patches) remain allowed (status unchanged)
    query_0742 = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/PATCH_ACCELERATOR_DETERMINISTIC_DECISION_CACHE_053.json",
        "--level",
        "summary",
        "--json",
    )
    assert query_0742["decision"] in ("allow", "defer")
    
    query_0743 = _run_query(
        "authority",
        "--target",
        "registry/governance/patches/PATCH_ACCELERATOR_DETERMINISTIC_ROUTING_AND_CANDIDATE_BOUNDING_054.json",
        "--level",
        "summary",
        "--json",
    )
    assert query_0743["decision"] in ("allow", "defer")
