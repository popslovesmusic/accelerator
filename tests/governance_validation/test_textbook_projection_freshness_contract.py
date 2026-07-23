import hashlib
import json
from pathlib import Path

from scripts.global_validate import (
    TextbookProjectionFreshnessValidator,
    _build_governed_stage_policy,
    _selected_stage_names,
)


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _write_fixture(root):
    textbook = root / "docs/textbook.md"
    source = root / "registry/source.json"
    contract = root / "governance/contract.json"
    textbook.parent.mkdir(parents=True)
    source.parent.mkdir(parents=True)
    contract.parent.mkdir(parents=True)
    textbook.write_text("TEXTBOOK_PROJECTION_FRESHNESS_CONTRACT_001\n", encoding="utf-8")
    source.write_text('{"status":"current"}\n', encoding="utf-8")
    contract.write_text(
        json.dumps(
            {
                "contract_id": "TEXTBOOK_PROJECTION_FRESHNESS_CONTRACT_001",
                "artifact_id": "MPF-TEXTBOOK-COMPLETE",
                "artifact_role": "GENERATED_PROJECTION",
                "canonical_snapshot_id": "TEST-SNAPSHOT",
                "projection_path": "docs/textbook.md",
                "projection_sha256": _sha256(textbook),
                "projection_status": "current",
                "required_projection_markers": ["TEXTBOOK_PROJECTION_FRESHNESS_CONTRACT_001"],
                "source_dependencies": [
                    {"path": "registry/source.json", "sha256": _sha256(source)}
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return textbook, source


def test_fresh_contract_passes(tmp_path):
    _write_fixture(tmp_path)

    result = TextbookProjectionFreshnessValidator(tmp_path, "governance/contract.json").run()

    assert result["status"] == "success"
    assert result["items_checked"] == 2


def test_declared_source_drift_fails_closed(tmp_path):
    _, source = _write_fixture(tmp_path)
    source.write_text('{"status":"changed"}\n', encoding="utf-8")

    result = TextbookProjectionFreshnessValidator(tmp_path, "governance/contract.json").run()

    assert result["status"] == "failed"
    assert any("Textbook source drift" in error for error in result["errors"])


def test_textbook_drift_fails_closed(tmp_path):
    textbook, _ = _write_fixture(tmp_path)
    textbook.write_text("changed\n", encoding="utf-8")

    result = TextbookProjectionFreshnessValidator(tmp_path, "governance/contract.json").run()

    assert result["status"] == "failed"
    assert any("projection hash mismatch" in error for error in result["errors"])


def test_freshness_stage_is_required_in_governed_full_run():
    stage_name = "textbook_projection_freshness_validation"
    stage_names = sorted(_selected_stage_names("full"))
    policy = _build_governed_stage_policy("full", stage_names)

    assert stage_name in stage_names
    assert policy[stage_name]["required"] is True
    assert policy[stage_name]["work_expectation"] == "REQUIRED"
