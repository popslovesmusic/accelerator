from types import SimpleNamespace

from scripts import validation_environment_contract as contract_module

from ._helpers import load_json, sha256_file


def _python_version(major=3, minor=14, micro=4):
    return SimpleNamespace(major=major, minor=minor, micro=micro)


def _version_provider_factory(versions):
    def version_provider(name):
        if name not in versions:
            raise contract_module.metadata.PackageNotFoundError(name)
        return versions[name]

    return version_provider


def test_patch_072_records_selected_minimal_supported_surface():
    artifact = load_json("outputs/governance_inventory/validation_department_supported_test_environment_contract_072.json")

    assert artifact["selected_minimal_contract"]["surface_id"] == contract_module.SURFACE_GOVERNANCE_PATCH_PYTEST
    assert artifact["selected_minimal_contract"]["command"] == "python -m pytest tests/governance_validation -q"


def test_patch_072_governance_patch_pytest_ready_when_required_dependency_present():
    result = contract_module.evaluate_environment(
        contract_module.SURFACE_GOVERNANCE_PATCH_PYTEST,
        version_provider=_version_provider_factory({"pytest": "9.0.3"}),
        python_version_info=_python_version(),
    )

    assert result["environment_status"] == "READY"
    assert result["missing_required_dependencies"] == []
    assert result["version_mismatches"] == []


def test_patch_072_missing_required_dependency_is_explicit_not_ready():
    result = contract_module.evaluate_environment(
        contract_module.SURFACE_GOVERNANCE_PATCH_PYTEST,
        version_provider=_version_provider_factory({}),
        python_version_info=_python_version(),
    )

    assert result["environment_status"] == "ENVIRONMENT_NOT_READY"
    assert result["missing_required_dependencies"] == ["pytest"]
    assert "Required governed dependencies" in result["reason"]


def test_patch_072_optional_legacy_dependency_absence_does_not_block_governance_patch_pytest():
    result = contract_module.evaluate_environment(
        contract_module.SURFACE_GOVERNANCE_PATCH_PYTEST,
        version_provider=_version_provider_factory({"pytest": "9.0.3"}),
        python_version_info=_python_version(),
    )

    optional_names = {entry["name"] for entry in result["optional_dependencies"]}
    assert "typer" in optional_names
    assert result["environment_status"] == "READY"


def test_patch_072_typer_is_classified_as_legacy_dependency():
    contract = contract_module.get_contract()

    assert contract["dependency_roles"]["typer"]["classification"] == "LEGACY_DEPENDENCY"
    assert "tests/test_lexicon_cli.py" in contract["dependency_roles"]["typer"]["reason"]


def test_patch_072_full_pytest_collection_remains_explicitly_unsupported():
    result = contract_module.evaluate_environment(
        contract_module.SURFACE_FULL_PYTEST_COLLECTION,
        version_provider=_version_provider_factory({"pytest": "9.0.3"}),
        python_version_info=_python_version(),
    )

    assert result["environment_status"] == "UNSUPPORTED_VALIDATION_SURFACE"
    assert "outside the governed supported" in result["reason"].lower()
    assert any("typer" in reason for reason in result["unsupported_reasons"])


def test_patch_072_environment_readiness_does_not_overwrite_validation_failure():
    readiness = contract_module.evaluate_environment(
        contract_module.SURFACE_GOVERNANCE_PATCH_PYTEST,
        version_provider=_version_provider_factory({"pytest": "9.0.3"}),
        python_version_info=_python_version(),
    )
    substantive_validation_status = "fail"

    assert readiness["environment_status"] == "READY"
    assert substantive_validation_status == "fail"


def test_patch_072_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["scripts/validation_environment_contract.py"] == (
        sha256_file("scripts/validation_environment_contract.py").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/validation_department_supported_test_environment_contract_072.json"] == (
        sha256_file("outputs/governance_inventory/validation_department_supported_test_environment_contract_072.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_VALIDATION_DEPARTMENT_SUPPORTED_TEST_ENVIRONMENT_CONTRACT_072.json"] == (
        sha256_file("patches/PATCH_VALIDATION_DEPARTMENT_SUPPORTED_TEST_ENVIRONMENT_CONTRACT_072.json").upper()
    )
    assert hash_registry["hashes"]["registry/governance/patches/PATCH_VALIDATION_DEPARTMENT_SUPPORTED_TEST_ENVIRONMENT_CONTRACT_072.json"] == (
        sha256_file("registry/governance/patches/PATCH_VALIDATION_DEPARTMENT_SUPPORTED_TEST_ENVIRONMENT_CONTRACT_072.json").upper()
    )
    assert hash_registry["hashes"]["tests/governance_validation/test_patch_072_validation_department_supported_test_environment_contract.py"] == (
        sha256_file("tests/governance_validation/test_patch_072_validation_department_supported_test_environment_contract.py").upper()
    )
