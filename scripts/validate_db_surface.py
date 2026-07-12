import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.validation_surface_wrapper import run_validation_surface


STAGES = [
    "db_authority_validation",
]


def main():
    return run_validation_surface(
        "Database validation surface",
        STAGES,
        "outputs/audits/db_surface_validation.json",
        "--db-only",
    )


if __name__ == "__main__":
    raise SystemExit(main())
