import json
import argparse
import os
try:
    from scripts.residue.residue_packet_builder import build_residue_packet
    from scripts.save_report import save_report
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from residue.residue_packet_builder import build_residue_packet
    from save_report import save_report

def compress_residue(query, db_path, out_path, limit=20):
    packet = build_residue_packet(query, db_path, limit=limit)
    
    # Save the packet
    task_id = f"COMPRESS-{query.upper().replace(' ', '_')}"
    save_report(packet, out_path, task_id, orientation="historical_residue", force=True)
    
    # Optional: Index in DB (if schema extended)
    return packet

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compress residue into governed summaries.")
    parser.add_argument("--query", required=True, help="Topic to compress.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to database.")
    parser.add_argument("--out", required=True, help="Output path for summary.")
    parser.add_argument("--limit", type=int, default=20, help="Source limit.")
    
    args = parser.parse_args()
    compress_residue(args.query, args.db, args.out, args.limit)
