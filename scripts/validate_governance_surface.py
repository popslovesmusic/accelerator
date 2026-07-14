import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.validation_surface_wrapper import run_validation_surface


STAGES = [
    "registry_validation",
    "governance_ledger_validation",
    "patch_record_validation",
    "patch_chain_validation",
    "patch_gate_validation",
    "db_authority_validation",
    "role_aware_authority_validation",
    "write_boundary_validation",
    "validation_reducer_authority_validation",
]


def main():
    return run_validation_surface(
        "Governance validation surface",
        STAGES,
        "outputs/audits/governance_surface_validation.json",
        "--governance-only",
    )


if __name__ == "__main__":
    raise SystemExit(main())
