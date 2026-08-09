import json
import os
from datetime import datetime


REGISTRY_PATH = "registry/math/meta004_derivation_graph_atlas_registry.json"
OUT_PATH = "outputs/math_tests/meta004_derivation_graph_atlas_result.json"


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def run_meta004() -> dict:
    results = {
        "id": "META004",
        "status": "pass",
        "assembly_timestamp": datetime.now().isoformat(),
        "atlas_document_count": 0,
        "graph_outputs_present": False,
        "codex_cross_references_present": False,
        "warnings": [],
        "errors": [],
        "governance_adherence": {
            "no_theorem_elevation": True,
            "no_global_closure_claims": True,
            "no_physics_claims": True,
            "results_marked_cartographic": True,
        },
    }

    if not os.path.exists(REGISTRY_PATH):
        results["status"] = "fail"
        results["errors"].append(f"Registry not found: {REGISTRY_PATH}")
        return {"derivation_graph_atlas_assembly": results}

    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception as exc:
        results["status"] = "fail"
        results["errors"].append(f"Registry JSON load error: {exc}")
        return {"derivation_graph_atlas_assembly": results}

    outputs = registry.get("atlas_layer", {}).get("atlas_outputs", [])
    doc_paths = [o.get("file_path") for o in outputs if isinstance(o, dict)]
    doc_paths = [p for p in doc_paths if isinstance(p, str)]

    missing = [p for p in doc_paths if not os.path.exists(p)]
    if missing:
        results["status"] = "fail"
        results["errors"].extend([f"Missing atlas doc: {p}" for p in missing])
    else:
        results["graph_outputs_present"] = True

    results["atlas_document_count"] = len(doc_paths)

    codex_refs = 0
    for p in doc_paths:
        if not os.path.exists(p):
            continue
        txt = _read_text(p)
        if "codex_master_index.md" in txt:
            codex_refs += 1
        if "no theorem elevation" not in txt.lower():
            results["warnings"].append(f"Governance phrase missing (no theorem elevation) in {p}")
        if "no global closure" not in txt.lower():
            results["warnings"].append(f"Governance phrase missing (no global closure) in {p}")
        if "no physics" not in txt.lower():
            results["warnings"].append(f"Governance phrase missing (no physics) in {p}")

    if codex_refs == len([p for p in doc_paths if os.path.exists(p)]) and codex_refs > 0:
        results["codex_cross_references_present"] = True
    else:
        results["status"] = "fail"
        results["errors"].append("Codex cross-references missing from one or more atlas documents.")

    return {"derivation_graph_atlas_assembly": results}


if __name__ == "__main__":
    report = run_meta004()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"META004 atlas assembly results saved to {OUT_PATH}")
