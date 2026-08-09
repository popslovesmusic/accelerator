import json
import os
from pathlib import Path
from datetime import datetime, UTC

def migrate():
    root = Path(".")
    manifest_path = root / "registry/governance_manifest.json"
    
    # 1. Load Sources
    registries = {
        "tool": root / "registry/tool_manifest.json",
        "math_source": root / "registry/math_source_registry.json",
        "claim": root / "registry/claim_registry.json",
        "evidence": root / "registry/evidence_index.json"
    }
    
    data = {}
    for key, path in registries.items():
        if path.exists():
            with open(path, 'r', encoding='utf-8-sig') as f:
                data[key] = json.load(f)
        else:
            data[key] = {}

    # 2. Initialize Unified Manifest
    unified = {
        "meta": {
            "version": "1.0.0",
            "generated_at": datetime.now(UTC).isoformat(),
            "project": "Acellorator Foundational Math Program"
        },
        "nodes": {},
        "edges": []
    }

    nodes = unified["nodes"]
    edges = unified["edges"]

    # 3. Migrate Tools
    tool_index_path = root / "registry/tool_index.json"
    entry_points = {}
    if tool_index_path.exists():
        with open(tool_index_path, 'r', encoding='utf-8') as f:
            tool_index = json.load(f)
            for t in tool_index:
                if "tool_name" in t and "entry_point" in t:
                    entry_points[t["tool_name"]] = t["entry_point"]

    for tool in data["tool"].get("tools", []):
        tid = tool["name"]
        if tid in entry_points:
            tool["entry_point"] = entry_points[tid]
        nodes[tid] = {
            "type": "tool",
            "status": tool.get("certification_level", "C0"),
            "data": tool
        }

    # 4. Migrate Math Sources from the canonical source registry.
    math_source = data["math_source"]
    documents = math_source.get("documents", []) if isinstance(math_source, dict) else []
    if documents:
        for doc in documents:
            doc_id = doc.get("doc_id") or Path(doc.get("path", "")).stem
            if not doc_id:
                continue
            nodes[doc_id] = {
                "type": "math_source_document",
                "status": "active",
                "data": doc
            }
            if doc.get("path"):
                edges.append({"source": doc_id, "target": doc["path"], "relation": "described_by"})

    # 5. Migrate Evidence (Runs)
    for run in data["evidence"]:
        rid = run.get("run_id") or run.get("evidence_id")
        if not rid: continue
        
        nodes[rid] = {
            "type": "run",
            "status": run.get("status", "complete"),
            "data": run
        }
        # Links to tools
        for tool in run.get("tools_used", []):
            if tool in nodes:
                edges.append({"source": rid, "target": tool, "relation": "executed_via"})

    # 6. Migrate Claims
    for claim in data["claim"].get("claims", []):
        cid = claim["claim_id"]
        nodes[cid] = {
            "type": "claim",
            "status": claim.get("status", "C1_defined"),
            "data": claim
        }
        # Links to math items
        # Heuristic: search paper content? No, look at item_id match in metadata if present
        # For now, link to paper_path
        if claim.get("paper_path"):
            edges.append({"source": cid, "target": claim["paper_path"], "relation": "documented_in"})
        
        # Links to runs (evidence_paths)
        for ep in claim.get("evidence_paths", []):
            run_name = Path(ep).name
            edges.append({"source": cid, "target": run_name, "relation": "supported_by"})

    # 7. Save
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(unified, f, indent=2)
    
    print(f"Migration complete. Governance manifest saved to {manifest_path}")
    print(f"Nodes: {len(nodes)}, Edges: {len(edges)}")

if __name__ == "__main__":
    migrate()
