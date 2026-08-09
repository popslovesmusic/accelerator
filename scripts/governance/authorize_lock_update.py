import json
import hashlib
from pathlib import Path
from datetime import datetime

def calculate_hash(path):
    try:
        content = path.read_bytes()
        return hashlib.sha256(content).hexdigest()
    except:
        return None

def relock_math():
    root = Path(".")
    
    # 1. Math source hashes (source-registry based)
    math_source_registry_path = root / "registry/math_source_registry.json"
    math_hashes_path = root / "registry/math_hashes.json"
    
    if math_source_registry_path.exists():
        print("Relocking math source registry...")
        with open(math_source_registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        new_hashes = {}
        items = registry.get('documents', [])
        for item in items:
            item_id = item.get('doc_id') or item.get('path')
            path_value = item.get('path')
            if not item_id or not path_value:
                print(f"Warning: Malformed math source registry entry: {item}")
                continue

            path = root / path_value
            if path.exists():
                new_hashes[item_id] = calculate_hash(path)
            else:
                print(f"Warning: File for {item_id} not found at {path}")
        
        with open(math_hashes_path, 'w', encoding='utf-8') as f:
            json.dump(new_hashes, f, indent=2)
        print(f"Updated {math_hashes_path}")

    # 2. math_core_hashes.json (directory-based)
    math_core_dir = root / "registry/math"
    math_codex_dir = root / "docs/math"
    math_core_hashes_path = root / "registry/math_core_hashes.json"
    
    core_paths = []
    if math_core_dir.is_dir():
        core_paths.extend(sorted(math_core_dir.glob("*.json")))
    if math_codex_dir.is_dir():
        core_paths.extend(sorted(math_codex_dir.glob("*.md")))
        
    if core_paths:
        print("Relocking math core/codex...")
        current = {"meta": {"generated_at": datetime.now().isoformat()}, "files": {}}
        for p in core_paths:
            rel = str(p.relative_to(root)).replace("\\", "/")
            current["files"][rel] = calculate_hash(p)
            
        with open(math_core_hashes_path, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)
        print(f"Updated {math_core_hashes_path}")

if __name__ == "__main__":
    relock_math()
