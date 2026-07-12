import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.validation_surface_wrapper import run_validation_surface


STAGES = [
    "engine_validation",
    "hygiene_validation",
    "implementation_validation",
    "evidence_validation",
    "campaign_validation",
    "governance_integrity_validation",
]


def main():
    return run_validation_surface(
        "Operational validation surface",
        STAGES,
        "outputs/audits/operational_surface_validation.json",
    )


if __name__ == "__main__":
    raise SystemExit(main())
