import json
import argparse
import os
import sqlite3

def query_residue(query, db_path):
    # This tool retrieves compressed residue packets by scanning defined output directories
    # or querying the DB if indexed.
    
    results = {
        "query": query,
        "matching_packets": []
    }
    
    # Search in outputs/reports
    report_dir = "outputs/reports"
    if os.path.exists(report_dir):
        for f in os.listdir(report_dir):
            if f.endswith('.json') and query.lower() in f.lower():
                path = os.path.join(report_dir, f)
                try:
                    with open(path, 'r') as f_in:
                        data = json.load(f_in)
                        packet = data.get("content", {}).get("residue_packet") or data.get("residue_packet")
                        if packet:
                            results["matching_packets"].append({
                                "packet_id": packet.get("packet_id"),
                                "path": path,
                                "summary": packet.get("compressed_summary"),
                                "confidence": packet.get("confidence")
                            })
                except:
                    continue
                    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query compressed residue.")
    parser.add_argument("--query", required=True, help="Keyword query.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to database.")
    
    args = parser.parse_args()
    res = query_residue(args.query, args.db)
    print(json.dumps(res, indent=2))
