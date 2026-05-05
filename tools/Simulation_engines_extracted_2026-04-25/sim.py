from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect bundled engine_manifest.json for provenance/discovery.")
    parser.add_argument("--config", type=Path, required=False, help="Unused (kept for manifest compatibility).")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = Path(__file__).with_name("engine_manifest.json")
    data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    (out_dir / "engine_manifest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
