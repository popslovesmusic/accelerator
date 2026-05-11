import json
import argparse
import os
import sqlite3
try:
    from scripts.agent_memory.memory_retrieval import retrieve_memory_context
    from scripts.registry_runtime_trace import run_registry_runtime_trace
    from scripts.claim_evidence_graph import build_claim_evidence_graph
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from agent_memory.memory_retrieval import retrieve_memory_context
    from registry_runtime_trace import run_registry_runtime_trace
    from claim_evidence_graph import build_claim_evidence_graph

def build_memory_packet(query, db_path, agent="Gemini", limit=15):
    # 1. Base Retrieval
    ctx = retrieve_memory_context(db_path, query, limit=limit)
    
    # 2. Traceability
    trace = run_registry_runtime_trace(db_path, query, limit=limit)
    
    # 3. Graph Summary
    graph = build_claim_evidence_graph(db_path)
    
    packet = {
        "memory_packet": {
            "packet_id": f"MEM-{os.popen('powershell -Command \"[guid]::NewGuid().ToString()\"').read().strip()[:8]}",
            "query": query,
            "agent": agent,
            "generated_at": os.popen('date /t').read().strip() + " " + os.popen('time /t').read().strip(),
            "orientation_context": {
                "current_command_evidence": [a["path"] for a in ctx["artifacts"] if a["orientation_status"] == "current_command_evidence"],
                "canonical_authority": [a["path"] for a in ctx["artifacts"] if a["orientation_status"] == "canonical_active"],
                "historical_residue": [a["path"] for a in ctx["artifacts"] if a["is_residue"]],
                "supersession_cautions": [],
                "db_health": {}, # Placeholder
                "traceability_links": trace["trace_report"]["resolved_links"]
            },
            "retrieved_artifacts": ctx["artifacts"],
            "retrieved_trace_reports": [trace["trace_report"]],
            "memory_conflicts": trace["trace_report"]["conflicts"],
            "residue_warnings": [],
            "missing_context": trace["trace_report"]["missing_links"],
            "recommended_next_steps": [],
            "warnings": ctx["warnings"]
        }
    }
    
    # Collect cautions
    for a in ctx["artifacts"]:
        if "cautions" in a and a["cautions"]:
            packet["memory_packet"]["orientation_context"]["supersession_cautions"].extend(a["cautions"])
        if a.get("is_residue"):
            packet["memory_packet"]["residue_warnings"].append(f"Artifact '{a['path']}' is historical residue.")

    return packet

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble a governed memory packet.")
    parser.add_argument("--query", required=True, help="Query for memory assembly.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--agent", default="Gemini", help="Target agent.")
    parser.add_argument("--limit", type=int, default=15, help="Limit retrieval depth.")
    
    args = parser.parse_args()
    packet = build_memory_packet(args.query, args.db, args.agent, args.limit)
    print(json.dumps(packet, indent=2))
