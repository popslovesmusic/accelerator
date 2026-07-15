from __future__ import annotations

import argparse
import json
import sys
from importlib import metadata
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS_PATH = PROJECT_ROOT / "requirements.txt"
LOCKFILE_PATH = PROJECT_ROOT / "requirements.lock.txt"
DEPENDENCY_POLICY_PATH = PROJECT_ROOT / "docs/math/dependency_reproducibility_policy.md"
REPRODUCIBILITY_REGISTRY_PATH = PROJECT_ROOT / "registry/math/audit002_dependency_reproducibility_lock_registry.json"
VENV_ACTIVATION_PATH = PROJECT_ROOT / "scripts/activate_venv.ps1"

SUPPORTED_PYTHON_BASELINE = "3.14.4"
SUPPORTED_PYTHON_MAJOR_MINOR = (3, 14)

SURFACE_GOVERNANCE_PATCH_PYTEST = "governance_patch_pytest"
SURFACE_FULL_PYTEST_COLLECTION = "full_pytest_collection"

REQUIRED_VALIDATION_DEPENDENCIES = {
    "pytest": "9.0.3",
}

DEPENDENCY_ROLE_MAP = {
    "pytest": {
        "classification": "REQUIRED_VALIDATION_DEPENDENCY",
        "reason": "Targeted governance patch validation records consistently use python -m pytest tests/governance_validation -q.",
    },
    "jsonschema": {
        "classification": "REQUIRED_VALIDATION_DEPENDENCY",
        "reason": "The locked validation baseline records jsonschema in the validation stack for governed validation tooling.",
    },
    "typer": {
        "classification": "LEGACY_DEPENDENCY",
        "reason": "Only tests/test_lexicon_cli.py imports typer, and that test also targets a missing oneproc.lexicon_cli surface.",
    },
}

SUPPORTED_SURFACES = {
    SURFACE_GOVERNANCE_PATCH_PYTEST: {
        "command": "python -m pytest tests/governance_validation -q",
        "required_dependencies": REQUIRED_VALIDATION_DEPENDENCIES,
        "optional_dependencies": {
            "typer": "Legacy test-only dependency outside the supported governance patch-validation path.",
        },
        "status_when_ready": "READY",
    },
    SURFACE_FULL_PYTEST_COLLECTION: {
        "command": "python -m pytest",
        "required_dependencies": {},
        "optional_dependencies": {},
        "status_when_ready": "UNSUPPORTED_VALIDATION_SURFACE",
        "unsupported_reasons": [
            "Full pytest collection is not the current governed supported validation path.",
            "Historical governance records already classify full pytest collection as blocked by legacy dependency and import-contract gaps.",
            "tests/test_lexicon_cli.py depends on typer and a missing oneproc.lexicon_cli surface.",
            "tests/test_rd_boundary_scaling_policy.py and tests/test_tda_adjacency_threshold.py rely on tool import contracts not selected by the supported patch-validation path.",
        ],
    },
}


def _read_requirements(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def _read_lockfile(path: Path) -> dict[str, str]:
    locked = {}
    for line in _read_requirements(path):
        if "==" not in line:
            continue
        name, version = line.split("==", 1)
        locked[name.strip().lower()] = version.strip()
    return locked


def _build_surface_inventory() -> dict[str, dict[str, str]]:
    return {
        "requirements_txt": {
            "path": "requirements.txt",
            "classification": "DECLARATIVE_DEPENDENCY_SURFACE",
            "role": "Human-readable top-level dependency declaration.",
        },
        "requirements_lock_txt": {
            "path": "requirements.lock.txt",
            "classification": "DECLARATIVE_LOCK_SURFACE",
            "role": "Exact validated dependency lock for the recorded baseline environment.",
        },
        "dependency_reproducibility_policy": {
            "path": "docs/math/dependency_reproducibility_policy.md",
            "classification": "INSTRUCTIONAL_POLICY_SURFACE",
            "role": "Documents how requirements.txt and requirements.lock.txt are interpreted.",
        },
        "audit002_reproducibility_registry": {
            "path": "registry/math/audit002_dependency_reproducibility_lock_registry.json",
            "classification": "REGISTERED_BASELINE_EVIDENCE",
            "role": "Records the 2026-05-13 baseline Python and validation stack versions.",
        },
        "activate_venv_script": {
            "path": "scripts/activate_venv.ps1",
            "classification": "BOOTSTRAP_HELPER",
            "role": "Activates the expected repo-local .venv after it has been created.",
        },
        "run_global_validation_batch": {
            "path": "run_global_validation.bat",
            "classification": "INSTRUCTIONAL_LAUNCHER",
            "role": "Historical Windows launcher; not selected as the canonical test-environment authority surface for this patch.",
        },
    }


def get_contract() -> dict[str, object]:
    locked_dependencies = _read_lockfile(LOCKFILE_PATH)
    return {
        "supported_python_baseline": SUPPORTED_PYTHON_BASELINE,
        "supported_python_major_minor": list(SUPPORTED_PYTHON_MAJOR_MINOR),
        "dependency_authority_surfaces": [
            "requirements.txt",
            "requirements.lock.txt",
            "docs/math/dependency_reproducibility_policy.md",
            "registry/math/audit002_dependency_reproducibility_lock_registry.json",
        ],
        "environment_bootstrap": {
            "venv_creation_command": "python -m venv .venv",
            "activation_script": "scripts/activate_venv.ps1",
            "dependency_install_command": "python -m pip install -r requirements.lock.txt",
        },
        "surface_inventory": _build_surface_inventory(),
        "dependency_roles": DEPENDENCY_ROLE_MAP,
        "locked_dependencies": locked_dependencies,
        "supported_surfaces": SUPPORTED_SURFACES,
        "selected_minimal_supported_surface": SURFACE_GOVERNANCE_PATCH_PYTEST,
    }


def _installed_version(distribution_name: str, version_provider=None) -> str | None:
    provider = version_provider or metadata.version
    try:
        return provider(distribution_name)
    except metadata.PackageNotFoundError:
        return None


def evaluate_environment(
    surface_id: str = SURFACE_GOVERNANCE_PATCH_PYTEST,
    *,
    version_provider=None,
    python_version_info=None,
) -> dict[str, object]:
    contract = get_contract()
    surfaces = contract["supported_surfaces"]
    if surface_id not in surfaces:
        raise ValueError(f"Unknown validation surface: {surface_id}")

    surface = surfaces[surface_id]
    python_info = python_version_info or sys.version_info
    python_version = f"{python_info.major}.{python_info.minor}.{python_info.micro}"

    result = {
        "surface_id": surface_id,
        "command": surface["command"],
        "supported_python_baseline": contract["supported_python_baseline"],
        "active_python_version": python_version,
        "active_python_matches_supported_major_minor": (
            python_info.major,
            python_info.minor,
        ) == SUPPORTED_PYTHON_MAJOR_MINOR,
        "dependency_authority_surfaces": contract["dependency_authority_surfaces"],
        "required_dependencies": [],
        "optional_dependencies": [],
        "missing_required_dependencies": [],
        "version_mismatches": [],
        "environment_status": surface["status_when_ready"],
        "reason": None,
    }

    if surface_id == SURFACE_FULL_PYTEST_COLLECTION:
        result["reason"] = "Full pytest collection remains outside the governed supported validation-environment contract."
        result["unsupported_reasons"] = list(surface["unsupported_reasons"])
        return result

    if not result["active_python_matches_supported_major_minor"]:
        result["environment_status"] = "ENVIRONMENT_NOT_READY"
        result["reason"] = "Active interpreter is outside the governed Python 3.14 baseline family."

    for distribution_name, expected_version in surface["required_dependencies"].items():
        installed_version = _installed_version(distribution_name, version_provider=version_provider)
        result["required_dependencies"].append(
            {
                "name": distribution_name,
                "expected_version": expected_version,
                "installed_version": installed_version,
            }
        )
        if installed_version is None:
            result["missing_required_dependencies"].append(distribution_name)
            result["environment_status"] = "ENVIRONMENT_NOT_READY"
        elif installed_version != expected_version:
            result["version_mismatches"].append(
                {
                    "name": distribution_name,
                    "expected_version": expected_version,
                    "installed_version": installed_version,
                }
            )
            result["environment_status"] = "ENVIRONMENT_NOT_READY"

    for distribution_name, rationale in surface["optional_dependencies"].items():
        result["optional_dependencies"].append(
            {
                "name": distribution_name,
                "installed_version": _installed_version(distribution_name, version_provider=version_provider),
                "rationale": rationale,
            }
        )

    if result["environment_status"] == "READY":
        result["reason"] = "Required governed dependencies for the supported governance patch-validation path are present."
    elif result["reason"] is None:
        result["reason"] = "Required governed dependencies for the supported governance patch-validation path are missing or mismatched."

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Governed Python validation-environment contract checker.")
    parser.add_argument(
        "--surface",
        default=SURFACE_GOVERNANCE_PATCH_PYTEST,
        choices=sorted(SUPPORTED_SURFACES.keys()),
        help="Validation surface to evaluate.",
    )
    args = parser.parse_args()

    result = evaluate_environment(args.surface)
    print(json.dumps(result, indent=2))

    if result["environment_status"] == "READY":
        return 0
    if result["environment_status"] == "UNSUPPORTED_VALIDATION_SURFACE":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
