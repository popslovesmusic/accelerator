import os
import json
import hashlib
from pathlib import Path

def calculate_hash(path):
    try:
        content = path.read_bytes()
        return hashlib.sha256(content).hexdigest()
    except Exception as e:
        print(f"Error hashing {path}: {e}")
        return None

def main():
    root = Path(__file__).resolve().parent.parent
    hashes_file = root / "registry/economics/economics_hashes.json"
    
    data = {}
    
    # 1. Theory Folder files (additive-only theory files mapped by basename)
    theory_dir = root / "docs/theory/foundational/5_03_26 unity/economics"
    if theory_dir.exists():
        for p in sorted(theory_dir.glob("*.md")):
            name = p.stem
            h = calculate_hash(p)
            if h:
                data[name] = h
                
    # 2. Docs Economics Folder files (mapped by relative path from project root)
    econ_dir = root / "docs/economics"
    if econ_dir.exists():
        for p in sorted(econ_dir.rglob("*")):
            if p.is_file() and p.name != ".gitkeep":
                rel = str(p.relative_to(root)).replace("\\", "/")
                h = calculate_hash(p)
                if h:
                    data[rel] = h
                    
    with open(hashes_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    print(f"Economics hashes synchronized and saved to {hashes_file}")

if __name__ == "__main__":
    main()
