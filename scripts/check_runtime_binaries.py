import os
import json
import hashlib
import ctypes
from pathlib import Path

def compute_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def check_binaries():
    manifest_path = Path("registry/runtime_binary_manifest.json")
    if not manifest_path.exists():
        print(f"Error: Manifest {manifest_path} not found.")
        return

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    results = []
    for entry in manifest.get("entries", []):
        tool_id = entry["tool_id"]
        required_binaries = entry.get("required_binaries", [])
        
        tool_status = {"tool_id": tool_id, "binaries": []}
        
        for bin_name in required_binaries:
            # Simple search heuristic: check tools/<tool_id>/
            bin_path = Path("tools") / tool_id / bin_name
            bin_info = {"name": bin_name, "path": str(bin_path), "exists": False, "hash": None, "loads": False}
            
            if bin_path.exists():
                bin_info["exists"] = True
                bin_info["hash"] = compute_hash(bin_path)
                
                if bin_name.endswith(".dll"):
                    try:
                        ctypes.CDLL(str(bin_path))
                        bin_info["loads"] = True
                    except Exception as e:
                        bin_info["load_error"] = str(e)
            
            tool_status["binaries"].append(bin_info)
        results.append(tool_status)
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    check_binaries()
