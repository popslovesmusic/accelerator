import sqlite3
import os
import argparse
import hashlib
try:
    from scripts.orientation_status_check import classify_path
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from orientation_status_check import classify_path

def get_checksum(path):
    if os.path.isdir(path):
        return None
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def index_artifacts(db_path, root_dir, dry_run=False):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for root, dirs, files in os.walk(root_dir):
        # Exclude some noisy dirs
        if '.git' in dirs: dirs.remove('.git')
        if '.venv' in dirs: dirs.remove('.venv')
        if '__pycache__' in dirs: dirs.remove('__pycache__')
        
        for name in files + dirs:
            full_path = os.path.relpath(os.path.join(root, name), root_dir)
            status, scope, confidence = classify_path(full_path)
            checksum = get_checksum(os.path.join(root, name))
            
            # Simple artifact type
            ext = os.path.splitext(name)[1].lower()
            a_type = 'directory' if os.path.isdir(os.path.join(root, name)) else ext[1:] if ext else 'file'
            
            if dry_run:
                print(f"[DRY-RUN] {full_path} -> {status} | {scope} | {confidence}")
                continue

            cursor.execute("""
                INSERT OR REPLACE INTO artifacts (
                    path, artifact_type, orientation_status, authority_scope, evidence_confidence, checksum
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (full_path, a_type, status, scope, confidence, checksum))
    
    if not dry_run:
        conn.commit()
    conn.close()
    print(f"Artifact indexing complete for {root_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index filesystem artifacts in the database.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--root", default=".", help="Root directory to index.")
    parser.add_argument("--dry-run", action="store_true", help="Do not modify database.")
    
    args = parser.parse_args()
    index_artifacts(args.db, args.root, args.dry_run)
