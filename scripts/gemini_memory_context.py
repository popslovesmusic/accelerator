import json
import argparse
import os
try:
    from scripts.agent_memory.memory_packet_builder import build_memory_packet
except ImportError:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from agent_memory.memory_packet_builder import build_memory_packet

def generate_gemini_memory_context(query, db_path, limit=15):
    packet = build_memory_packet(query, db_path, agent="Gemini", limit=limit)
    
    # Add Gemini-specific governance footer
    packet["memory_packet"]["recommended_next_steps"].append("Summarize memory artifacts while preserving residue labels.")
    packet["memory_packet"]["recommended_next_steps"].append("Verify L3 status of any retrieved term before asserting definitions.")
    
    print(json.dumps(packet, indent=2))
    return packet

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Gemini-safe governed memory packet.")
    parser.add_argument("--query", required=True, help="Query for memory context.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=15, help="Result limit.")
    
    args = parser.parse_args()
    generate_gemini_memory_context(args.query, args.db, args.limit)
