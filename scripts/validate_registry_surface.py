import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.validation_surface_wrapper import run_validation_surface


STAGES = [
    "manifest_validation",
    "json_parse_validation",
    "registry_validation",
    "hash_registry_validation",
    "governance_ledger_validation",
    "patch_record_validation",
]


def main():
    return run_validation_surface(
        "Registry validation surface",
        STAGES,
        "outputs/audits/registry_surface_validation.json",
        "--registries-only",
    )


if __name__ == "__main__":
    raise SystemExit(main())
