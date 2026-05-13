import json
import os
from datetime import datetime


REGISTRY_PATH = "registry/math/meta004_derivation_graph_atlas_registry.json"
RESULT_PATH = "outputs/math_tests/meta004_derivation_graph_atlas_result.json"
MT_REGISTRY_PATH = "registry/math/minimal_theorems_registry.json"


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def validate_meta004() -> dict:
    report = {
        "derivation_graph_atlas_validation": {
            "status": "pass",
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "warnings": [],
            "errors": [],
        }
    }
    v = report["derivation_graph_atlas_validation"]

    def check(ok: bool, name: str, err: str | None = None):
        v["checks"].append({"name": name, "status": "pass" if ok else "fail"})
        if not ok and err:
            v["errors"].append(err)
            v["status"] = "fail"

    check(os.path.exists(REGISTRY_PATH), "META004 registry exists", f"Missing registry: {REGISTRY_PATH}")
    check(os.path.exists(RESULT_PATH), "META004 results exist", f"Missing results: {RESULT_PATH}")

    if v["status"] == "fail":
        return report

    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)
        with open(RESULT_PATH, "r", encoding="utf-8") as f:
            results = json.load(f)
    except Exception as exc:
        v["status"] = "fail"
        v["errors"].append(f"JSON load error: {exc}")
        return report

    outputs = registry.get("atlas_layer", {}).get("atlas_outputs", [])
    doc_paths = [o.get("file_path") for o in outputs if isinstance(o, dict)]
    doc_paths = [p for p in doc_paths if isinstance(p, str)]

    check(len(doc_paths) >= 5, "Atlas document count minimum", f"Atlas doc count {len(doc_paths)} < 5")

    missing_docs = [p for p in doc_paths if not os.path.exists(p)]
    check(not missing_docs, "All atlas documents exist", f"Missing atlas docs: {missing_docs}")

    if missing_docs:
        return report

    # Governance checks within documents
    for p in doc_paths:
        txt = _read_text(p).lower()
        if "no theorem elevation" not in txt:
            v["status"] = "fail"
            v["errors"].append(f"Missing governance phrase 'no theorem elevation' in {p}")
        if "no global closure" not in txt:
            v["status"] = "fail"
            v["errors"].append(f"Missing governance phrase 'no global closure' in {p}")
        if "no physics" not in txt:
            v["status"] = "fail"
            v["errors"].append(f"Missing governance phrase 'no physics' in {p}")
        if "codex_master_index.md" not in txt:
            v["status"] = "fail"
            v["errors"].append(f"Missing codex cross-reference in {p}")

    check(v["status"] != "fail", "Governance phrases present")

    # Theorem statuses preserved (MT-001..003 should remain consolidated in registry)
    if os.path.exists(MT_REGISTRY_PATH):
        try:
            with open(MT_REGISTRY_PATH, "r", encoding="utf-8") as f:
                mt = json.load(f)
            mt_map = {t.get("theorem_id"): t for t in mt.get("theorems", []) if isinstance(t, dict)}
            for tid in ["MT-001", "MT-002", "MT-003"]:
                status = (mt_map.get(tid) or {}).get("status")
                check(status == "consolidated", f"Theorem status preserved: {tid}", f"{tid} status is '{status}', expected 'consolidated'")
        except Exception as exc:
            v["warnings"].append(f"Could not validate theorem statuses: {exc}")
    else:
        v["warnings"].append(f"Minimal theorems registry missing for status check: {MT_REGISTRY_PATH}")

    # Results sanity: expected keys present
    assembly = results.get("derivation_graph_atlas_assembly", {})
    check(assembly.get("graph_outputs_present") is True, "graph_outputs_present true", "Results indicate missing graph outputs.")
    check(assembly.get("codex_cross_references_present") is True, "codex_cross_references_present true", "Results indicate missing codex cross-references.")

    return report


if __name__ == "__main__":
    print(json.dumps(validate_meta004(), indent=2))
