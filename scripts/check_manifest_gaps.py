import json
import os

manifest_path = "tool_manifest.json"
with open(manifest_path, 'r', encoding='utf-8-sig') as f:
    manifest = json.load(f)

manifest_tools = {t["name"] for t in manifest["tools"]}

actual_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and d.endswith("_cpp")]

missing = []
for d in actual_dirs:
    if d not in manifest_tools:
        missing.append(d)

if missing:
    print("C++ directories not in tool_manifest.json:")
    for d in missing:
        print(f"  - {d}")
else:
    print("All C++ directories are in tool_manifest.json")
