import sqlite3
import json
import os
import argparse
import hashlib
from datetime import datetime
try:
    from scripts.orientation_status_check import classify_path
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from orientation_status_check import classify_path

def get_hash(path):
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def snapshot_registries(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    registries = [
        "registry/tool_manifest.json",
        "registry/lexicon_canonical.json",
        "registry/lexicon_alias_map.json",
        "registry/lexicon_gap_queue.json",
        "registry/lexicon_validation_registry.json",
        "registry/math_registry.json",
        "registry/compliance_charter_v2_3.json"
    ]

    for path in registries:
        if not os.path.exists(path):
            print(f"Skipping missing registry: {path}")
            continue

        status, scope, _ = classify_path(path)
        source_hash = get_hash(path)
        modified_at = datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
        
        # Determine type and key count
        r_type = "unknown"
        key_count = 0
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "lexicon" in path: r_type = "lexicon"
                elif "claim" in path: r_type = "claim"
                elif "manifest" in path: r_type = "tool_manifest"
                
                # Heuristic for key count
                if isinstance(data, dict):
                    # Check top level collection keys
                    for k in ["terms", "tools", "claims", "lemmas", "proofs"]:
                        if k in data and isinstance(data[k], (list, dict)):
                            key_count = len(data[k])
                            break
                    if key_count == 0:
                        key_count = len(data)
                elif isinstance(data, list):
                    key_count = len(data)
        except:
            pass

        cursor.execute("""
            INSERT INTO registry_snapshots (
                registry_path, registry_type, source_hash, key_count, 
                modified_at, orientation_status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (path, r_type, source_hash, key_count, modified_at, status))

    conn.commit()
    conn.close()
    print("Registry snapshots indexed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Snapshot SSOT registry metadata into DB.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    args = parser.parse_args()
    snapshot_registries(args.db)
