# Root Directory Layout

This repository now uses these homes for new generated artifacts:

| Path | Purpose |
| --- | --- |
| `outputs/<engine-or-program>/...` | Recoverable run outputs, reports, JSONL command logs, CSV metrics |
| `scripts/` | Root-level build/run helpers |
| `bin/` | Local manually-built binaries, ignored by git |
| `<engine>_cpp/` | C++ source, headers, local build scripts, and compatibility binaries expected by manifests |
| `Simulation_engines_extracted_2026-04-25/outputs/...` | Outputs local to the extracted engine package |

## Output Rule

New root-level runs should write to `outputs/<engine-or-program>/<run-name>/`.

Engine-local `outputs/` folders may still exist from older runs. New C++ ports and
UHD/SYCL report writers should prefer the root `outputs/` directory unless the
engine package is intentionally self-contained, as with
`Simulation_engines_extracted_2026-04-25`.

## Build Products

Build products are ignored by `.gitignore`. Do not commit `.exe`, `.obj`, `.lib`,
`.exp`, `.pdb`, or generated CMake build trees unless explicitly needed as release
artifacts.
