import json
import argparse
import os
try:
    from scripts.agent_memory.memory_packet_builder import build_memory_packet
except ImportError:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from agent_memory.memory_packet_builder import build_memory_packet

def generate_codex_memory_context(query, db_path, limit=15):
    packet = build_memory_packet(query, db_path, agent="Codex", limit=limit)
    
    # Add Codex-specific maintenance/repair footer
    packet["memory_packet"]["recommended_next_steps"].append("Identify shadow/residue artifacts for potential archiving.")
    packet["memory_packet"]["recommended_next_steps"].append("Ensure any proposed fix preserves SSOT registry integrity.")
    
    print(json.dumps(packet, indent=2))
    return packet

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Codex-safe maintenance memory packet.")
    parser.add_argument("--query", required=True, help="Query for memory context.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=15, help="Result limit.")
    
    args = parser.parse_args()
    generate_codex_memory_context(args.query, args.db, args.limit)
