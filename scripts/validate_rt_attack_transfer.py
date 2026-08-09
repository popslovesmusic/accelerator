"""Read-only validator for an RT Calculus -> Acellorator transfer package."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate(package: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    manifest_paths = list(package.glob("*.transfer.json"))
    if not manifest_paths:
        manifest_paths = [package / "transfer_manifest.json"]
    manifest_path = manifest_paths[0]
    if not manifest_path.is_file():
        return [f"missing transfer manifest: {manifest_path}"], warnings
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read transfer manifest: {exc}"], warnings

    expected = {
        "schema_id": "rt_attack_transfer_manifest_v1",
        "source_program": "RT_CALCULUS",
        "destination_program": "ACELLORATOR",
        "direction": "RT_CALCULUS_TO_ACELLORATOR_ONLY",
        "reverse_channel": "DISABLED",
    }
    for key, value in expected.items():
        if key == "schema_id" and key not in manifest:
            warnings.append("legacy transfer manifest has no schema_id; future exports must add it")
            continue
        if manifest.get(key) != value:
            fail(errors, f"{key} must be {value!r}")
    if manifest.get("intake_status") not in {"NOT_SUBMITTED", "SUBMITTED", "REJECTED", "ACCEPTED"}:
        fail(errors, "intake_status is invalid or missing")

    if manifest.get("authority_status") != "NON_CANONICAL_PROVISIONAL_EVIDENCE":
        fail(errors, "authority_status must remain NON_CANONICAL_PROVISIONAL_EVIDENCE")
    if manifest.get("file_count") != len(manifest.get("files", [])):
        fail(errors, "file_count does not match files length")

    package_root = package
    package_name = manifest.get("package_name")
    if isinstance(package_name, str) and (package / package_name).is_dir():
        package_root = package / package_name

    listed_paths: set[str] = set()
    for entry in manifest.get("files", []):
        relative = entry.get("relative_path")
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or "\\" in relative:
            fail(errors, f"invalid relative file path: {relative!r}")
            continue
        candidate = (package_root / relative).resolve()
        try:
            candidate.relative_to(package_root.resolve())
        except ValueError:
            fail(errors, f"path escapes package: {relative}")
            continue
        if relative in listed_paths:
            fail(errors, f"duplicate file entry: {relative}")
        listed_paths.add(relative)
        if not candidate.is_file():
            fail(errors, f"listed file is missing: {relative}")
            continue
        if candidate.stat().st_size != entry.get("byte_size"):
            fail(errors, f"size mismatch: {relative}")
        if sha256(candidate) != entry.get("sha256"):
            fail(errors, f"hash mismatch: {relative}")

    if not manifest.get("files"):
        fail(errors, "files must contain at least one entry")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="export package directory")
    args = parser.parse_args()
    errors, warnings = validate(args.package)
    result = {"package": str(args.package), "valid": not errors, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
