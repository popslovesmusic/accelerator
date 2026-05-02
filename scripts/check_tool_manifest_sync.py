import argparse
import json
from pathlib import Path
from json import JSONDecodeError


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _cert_path_for(tool_entry: dict) -> Path | None:
    validation_path = tool_entry.get("validation_path")
    if not validation_path:
        return None
    p = (REPO_ROOT / validation_path / "certification_manifest.json").resolve()
    return p if p.exists() else None


def check_sync(tool_manifest_path: Path, only_tools: set[str] | None = None) -> list[str]:
    manifest = _load_json(tool_manifest_path)
    failures: list[str] = []

    for tool in manifest.get("tools", []):
        name = tool.get("name")
        if not name:
            continue
        if only_tools is not None and name not in only_tools:
            continue

        cert_path = _cert_path_for(tool)
        if cert_path is None:
            continue

        try:
            cert = _load_json(cert_path)
        except JSONDecodeError as e:
            failures.append(f"{name}: invalid certification_manifest.json ({cert_path.as_posix()}): {e}")
            continue
        sv = cert.get("scientific_validity", {}) if isinstance(cert, dict) else {}

        expected = {
            "certification_level": cert.get("certification_level"),
            "has_falsification": bool(sv.get("falsification_verified", False)),
            "numerical_stability_verified": bool(sv.get("numerical_stability_verified", False)),
            "uncertainty_quantified": bool(sv.get("uncertainty_quantified", False)),
            "provenance_verified": bool(sv.get("provenance_verified", False)),
        }

        actual = {k: tool.get(k) for k in expected.keys()}
        mismatched = {k: {"manifest": actual[k], "cert": expected[k]} for k in expected if actual[k] != expected[k]}
        if mismatched:
            failures.append(
                f"{name}: {json.dumps(mismatched, sort_keys=True)} (cert={cert_path.as_posix()})"
            )

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Check registry/tool_manifest.json matches tool-local certification manifests.")
    parser.add_argument("--manifest", default="registry/tool_manifest.json", help="Path to tool_manifest.json")
    parser.add_argument("--tool", action="append", default=None, help="Tool name to check (repeatable).")
    args = parser.parse_args()

    tool_manifest_path = (REPO_ROOT / args.manifest).resolve()
    only_tools = set(args.tool) if args.tool else None

    failures = check_sync(tool_manifest_path, only_tools=only_tools)
    if failures:
        print("FAIL: tool_manifest mismatch:")
        for f in failures:
            print(" -", f)
        return 1

    print("OK: tool_manifest matches certification manifests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
