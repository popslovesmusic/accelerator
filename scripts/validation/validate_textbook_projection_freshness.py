import argparse
import hashlib
import json
from pathlib import Path


DEFAULT_CONTRACT = "governance/live/textbook_projection_freshness_contract.json"


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


class TextbookProjectionFreshnessValidator:
    """Fail closed when the textbook or one of its declared sources drifts."""

    def __init__(self, root_dir, contract_path=DEFAULT_CONTRACT):
        self.root = Path(root_dir).resolve()
        self.contract_path = self.root / contract_path

    def _resolve_governed_path(self, relative_path):
        candidate = (self.root / relative_path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(f"Path escapes repository root: {relative_path}") from exc
        return candidate

    def run(self):
        result = {
            "status": "success",
            "errors": [],
            "warnings": [],
            "items_checked": 0,
            "work_expectation": "REQUIRED",
            "work_state": "WORK_STARTED",
            "targets_discovered": 1,
            "targets_attempted": 1,
            "targets_completed": 0,
            "passed_count": 0,
            "failed_count": 0,
            "evidence_paths": [str(self.contract_path.relative_to(self.root)).replace("\\", "/")],
        }

        if not self.contract_path.is_file():
            result["status"] = "failed"
            result["errors"].append(f"Missing textbook freshness contract: {self.contract_path}")
            result.update(work_state="WORK_COMPLETED", targets_completed=1, failed_count=1)
            return result

        try:
            contract = json.loads(self.contract_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            result["status"] = "failed"
            result["errors"].append(f"Cannot load textbook freshness contract: {exc}")
            result.update(work_state="WORK_COMPLETED", targets_completed=1, failed_count=1)
            return result

        required = {
            "contract_id",
            "artifact_id",
            "artifact_role",
            "canonical_snapshot_id",
            "projection_path",
            "projection_sha256",
            "projection_status",
            "source_dependencies",
        }
        missing = sorted(required - set(contract))
        if missing:
            result["errors"].append(f"Contract missing required fields: {', '.join(missing)}")

        if contract.get("artifact_role") != "GENERATED_PROJECTION":
            result["errors"].append("Textbook artifact_role must be GENERATED_PROJECTION.")
        if contract.get("projection_status") != "current":
            result["errors"].append("Textbook projection_status must be current.")

        projection_relative = contract.get("projection_path")
        if isinstance(projection_relative, str):
            try:
                projection_path = self._resolve_governed_path(projection_relative)
                if not projection_path.is_file():
                    result["errors"].append(f"Missing textbook projection: {projection_relative}")
                else:
                    result["items_checked"] += 1
                    result["evidence_paths"].append(projection_relative)
                    actual = _sha256(projection_path)
                    expected = str(contract.get("projection_sha256") or "").upper()
                    if actual != expected:
                        result["errors"].append(
                            f"Textbook projection hash mismatch: expected {expected}, observed {actual}."
                        )
                    text = projection_path.read_text(encoding="utf-8-sig")
                    for marker in contract.get("required_projection_markers", []):
                        if marker not in text:
                            result["errors"].append(f"Textbook is missing required governance marker: {marker}")
            except (OSError, ValueError) as exc:
                result["errors"].append(str(exc))
        else:
            result["errors"].append("projection_path must be a repository-relative string.")

        dependencies = contract.get("source_dependencies")
        if not isinstance(dependencies, list) or not dependencies:
            result["errors"].append("source_dependencies must be a non-empty list.")
            dependencies = []

        seen_paths = set()
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                result["errors"].append("Each source dependency must be an object.")
                continue
            relative = dependency.get("path")
            expected = str(dependency.get("sha256") or "").upper()
            if not isinstance(relative, str) or not expected:
                result["errors"].append("Each source dependency requires path and sha256.")
                continue
            if relative in seen_paths:
                result["errors"].append(f"Duplicate source dependency: {relative}")
                continue
            seen_paths.add(relative)
            try:
                path = self._resolve_governed_path(relative)
                if not path.is_file():
                    result["errors"].append(f"Missing declared textbook source: {relative}")
                    continue
                result["items_checked"] += 1
                result["evidence_paths"].append(relative)
                actual = _sha256(path)
                if actual != expected:
                    result["errors"].append(
                        f"Textbook source drift: {relative}; expected {expected}, observed {actual}."
                    )
            except (OSError, ValueError) as exc:
                result["errors"].append(str(exc))

        if result["errors"]:
            result["status"] = "failed"
        result.update(
            work_state="WORK_COMPLETED",
            targets_completed=1,
            passed_count=1 if result["status"] == "success" else 0,
            failed_count=1 if result["status"] == "failed" else 0,
        )
        result["contract_id"] = contract.get("contract_id")
        result["canonical_snapshot_id"] = contract.get("canonical_snapshot_id")
        result["dependency_count"] = len(dependencies)
        return result


def main():
    parser = argparse.ArgumentParser(description="Validate textbook projection freshness.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--contract", default=DEFAULT_CONTRACT)
    args = parser.parse_args()

    result = TextbookProjectionFreshnessValidator(args.root, args.contract).run()
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
