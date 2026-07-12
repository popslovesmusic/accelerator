import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.validation_surface_wrapper import run_validation_surface


STAGES = [
    "math_validation",
    "math_test_provenance_validation",
    "math_program_validation",
]


def main():
    return run_validation_surface(
        "Math validation surface",
        STAGES,
        "outputs/audits/math_surface_validation.json",
        "--math-only",
    )


if __name__ == "__main__":
    raise SystemExit(main())
