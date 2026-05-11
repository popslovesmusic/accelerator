import sqlite3
import os
import argparse
import fnmatch

PATTERNS = [
    "*backup*", "*.bak", "*legacy*", "*deprecated*", "*old*", "*copy*",
    "*_v1*", "*_v2*", "*_v3*"
]

def build_supersession_edges(db_path, root_dir, dry_run=True):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all artifacts
    cursor.execute("SELECT id, path FROM artifacts")
    artifacts = cursor.fetchall()
    
    edges_found = []

    for art in artifacts:
        path = art["path"]
        name = os.path.basename(path)
        
        # Check if this artifact matches a shadow pattern
        matches = False
        for pattern in PATTERNS:
            if fnmatch.fnmatch(name.lower(), pattern):
                matches = True
                break
        
        if matches:
            # Try to find potential active counterpart
            # (Simple heuristic: strip pattern and look for match)
            base_name = name
            for p in ["_v1", "_v2", "_v3", ".bak", "copy of "]:
                base_name = base_name.replace(p, "")
            
            if base_name != name:
                # Find artifacts with base_name in their path
                cursor.execute("SELECT id, path FROM artifacts WHERE path LIKE ? AND id != ?", (f"%{base_name}%", art["id"]))
                candidates = cursor.fetchall()
                
                for cand in candidates:
                    relation = "shadow_of"
                    if ".bak" in name: relation = "backup_of"
                    elif "legacy" in name: relation = "legacy_of"
                    elif "v1" in name or "v2" in name: relation = "version_variant_of"
                    
                    edges_found.append({
                        "from_id": art["id"],
                        "from_path": path,
                        "to_id": cand["id"],
                        "to_path": cand["path"],
                        "relation": relation,
                        "confidence": "probable"
                    })

    if dry_run:
        print(f"[DRY-RUN] Found {len(edges_found)} potential supersession edges.")
        for e in edges_found[:10]:
            print(f"  {e['from_path']} -> {e['to_path']} ({e['relation']})")
    else:
        for e in edges_found:
            cursor.execute("""
                INSERT OR IGNORE INTO supersession_edges (
                    from_artifact_id, to_artifact_id, relation, confidence
                )
                VALUES (?, ?, ?, ?)
            """, (e["from_id"], e["to_id"], e["relation"], e["confidence"]))
        conn.commit()
        print(f"Applied {len(edges_found)} supersession edges.")

    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect and build supersession edges.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--root", default=".", help="Root directory.")
    parser.add_argument("--apply", action="store_true", help="Apply edges to database.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only (default).")
    
    args = parser.parse_args()
    dry_run = not args.apply
    build_supersession_edges(args.db, args.root, dry_run)
