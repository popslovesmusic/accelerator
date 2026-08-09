import argparse
import json
import os

try:
    from scripts.query_governance import build_governed_context_capsule_v1
except ImportError:
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from query_governance import build_governed_context_capsule_v1


def build_memory_packet(query, db_path, agent="Gemini", limit=15):
    capsule = build_governed_context_capsule_v1(db_path, query=query, limit=limit)
    artifacts = capsule.get("relevant_artifacts", [])
    trace_report = capsule.get("runtime_trace", {}).get("trace_report", {})
    supersession_cautions = []
    for artifact in artifacts:
        supersession_cautions.extend(artifact.get("cautions", []))
        supersession = artifact.get("supersession", {})
        if isinstance(supersession, dict):
            for relation in supersession.get("relations", []):
                relation_text = relation.get("relation")
                if relation_text:
                    supersession_cautions.append(f"Artifact '{artifact.get('path')}' has supersession relation '{relation_text}'.")
    supersession_cautions.extend(trace_report.get("supersession_cautions", []))
    supersession_cautions = list(dict.fromkeys([item for item in supersession_cautions if item]))

    packet = {
        "memory_packet": {
            "packet_id": f"MEM-{str(capsule.get('capsule_hash', '')).replace('-', '')[:8].upper() or '00000000'}",
            "query": query,
            "agent": agent,
            "generated_at": capsule.get("provenance", {}).get("built_at"),
            "orientation_context": {
                "current_command_evidence": [
                    artifact.get("path")
                    for artifact in artifacts
                    if artifact.get("orientation_status") == "current_command_evidence"
                ],
                "canonical_authority": [
                    artifact.get("path")
                    for artifact in artifacts
                    if artifact.get("orientation_status") == "canonical_active"
                ],
                "historical_residue": [
                    artifact.get("path")
                    for artifact in artifacts
                    if artifact.get("is_residue")
                ],
                "supersession_cautions": supersession_cautions,
                "db_health": capsule.get("database_health", {}),
                "traceability_links": trace_report.get("resolved_links", []),
            },
            "retrieved_artifacts": artifacts,
            "retrieved_trace_reports": [trace_report],
            "memory_conflicts": trace_report.get("conflicts", []),
            "residue_warnings": [
                f"Artifact '{artifact.get('path')}' is historical residue."
                for artifact in artifacts
                if artifact.get("is_residue")
            ],
            "missing_context": trace_report.get("missing_links", []),
            "recommended_next_steps": [
                f"{action.get('action_id')}: {action.get('reason')}"
                for action in capsule.get("candidate_actions", [])
            ],
            "warnings": capsule.get("warnings", []),
        }
    }

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
