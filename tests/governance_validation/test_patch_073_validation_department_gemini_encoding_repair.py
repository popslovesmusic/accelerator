from pathlib import Path

from ._helpers import load_json, sha256_file


def _gemini_lines():
    return Path("GEMINI.md").read_text(encoding="utf-8").splitlines()


def test_patch_073_known_mojibake_sequences_are_absent():
    text = Path("GEMINI.md").read_text(encoding="utf-8")

    assert "(â„°â‰ 0) â‡”_R Î´(â„°>0)" not in text
    assert "C0Ã¢â‚¬â€œC5" not in text


def test_patch_073_repository_confirmed_unicode_expression_is_present():
    text = Path("GEMINI.md").read_text(encoding="utf-8")

    assert "(ℰ≠0) ⇔_R δ(ℰ>0)" in text
    assert "C0–C5" in text


def test_patch_073_surrounding_content_is_unchanged():
    lines = _gemini_lines()

    assert lines[26] == (
        "**Non-Occlusive Humility Clause:** No unrestricted ontological, physical, mathematical, or universal truth claims may be made from framework structure, metaphor, simulation, analogy, or internal consistency alone. You MUST report what was observed, defined, simulated, compared, or structurally mapped, with explicit scope."
    )
    assert lines[46] == "- **Recoverable Output:** No empirical claim is valid without a recoverable output path in `results/`."
    assert lines[48] == "- **Reporting Structure:** Every report/paper MUST follow the structure:"


def test_patch_073_authority_role_classification_is_unchanged():
    artifact = load_json("outputs/governance_inventory/validation_department_gemini_encoding_repair_073.json")

    assert artifact["authority_role_determination"]["authority_role"] == "INSTRUCTION_AUTHORITY"
    assert artifact["authority_role_determination"]["authority_state"] == "EXPLICIT_LIVE_AUTHORITY"


def test_patch_073_governance_artifacts_parse_and_hashes_are_registered():
    artifact = load_json("outputs/governance_inventory/validation_department_gemini_encoding_repair_073.json")
    patch = load_json("patches/PATCH_VALIDATION_DEPARTMENT_GEMINI_ENCODING_REPAIR_073.json")
    registry_patch = load_json("registry/governance/patches/PATCH_VALIDATION_DEPARTMENT_GEMINI_ENCODING_REPAIR_073.json")
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert artifact["patch_id"] == "PATCH_VALIDATION_DEPARTMENT_GEMINI_ENCODING_REPAIR_073"
    assert patch["patch_id"] == "PATCH_VALIDATION_DEPARTMENT_GEMINI_ENCODING_REPAIR_073"
    assert registry_patch["patch_id"] == "PATCH_VALIDATION_DEPARTMENT_GEMINI_ENCODING_REPAIR_073"

    assert hash_registry["hashes"]["GEMINI.md"] == sha256_file("GEMINI.md").upper()
    assert hash_registry["hashes"]["outputs/governance_inventory/validation_department_gemini_encoding_repair_073.json"] == (
        sha256_file("outputs/governance_inventory/validation_department_gemini_encoding_repair_073.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_VALIDATION_DEPARTMENT_GEMINI_ENCODING_REPAIR_073.json"] == (
        sha256_file("patches/PATCH_VALIDATION_DEPARTMENT_GEMINI_ENCODING_REPAIR_073.json").upper()
    )
    assert hash_registry["hashes"]["registry/governance/patches/PATCH_VALIDATION_DEPARTMENT_GEMINI_ENCODING_REPAIR_073.json"] == (
        sha256_file("registry/governance/patches/PATCH_VALIDATION_DEPARTMENT_GEMINI_ENCODING_REPAIR_073.json").upper()
    )
    assert hash_registry["hashes"]["tests/governance_validation/test_patch_073_validation_department_gemini_encoding_repair.py"] == (
        sha256_file("tests/governance_validation/test_patch_073_validation_department_gemini_encoding_repair.py").upper()
    )
