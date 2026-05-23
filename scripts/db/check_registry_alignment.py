import sqlite3
import json
from pathlib import Path

def check_alignment():
    db_path = "registry/db/acellorator_index.sqlite"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    report = {"status": "pass", "mismatches": []}

    # 1. Check Claim Registry Alignment
    with open("registry/claim_registry.json", 'r') as f:
        claims = json.load(f).get("claims", [])
    
    for c in claims:
        cid = c["claim_id"]
        path = c.get("paper_path")
        if not path: continue # Some claims might not have papers yet
        
        path = path.replace("/", "\\") # Standardize to backslashes for DB check
        cursor.execute("SELECT id FROM artifacts WHERE path = ?", (path,))
        if not cursor.fetchone():
            # Try forward slash
            cursor.execute("SELECT id FROM artifacts WHERE path = ?", (path.replace("\\", "/"),))
            if not cursor.fetchone():
                report["status"] = "fail"
                report["mismatches"].append(f"Claim {cid}: Paper path {path} missing from DB.")

    # 2. Check Math Registry Alignment
    with open("registry/math_registry.json", 'r') as f:
        math = json.load(f)
        items = math.get("theorems", []) + math.get("lemmas", []) + math.get("proofs", [])
    
    for item in items:
        iid = item["item_id"]
        path = item["path"].replace("\\", "/")
        cursor.execute("SELECT id FROM artifacts WHERE path = ?", (path,))
        if not cursor.fetchone():
            # DB uses backslashes for some reason? Let's check both
            cursor.execute("SELECT id FROM artifacts WHERE path = ?", (path.replace("/", "\\"),))
            if not cursor.fetchone():
                report["status"] = "fail"
                report["mismatches"].append(f"Math Item {iid}: Path {path} missing from DB.")

    conn.close()
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    check_alignment()
