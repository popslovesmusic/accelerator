import json
import os

manifest_path = os.environ.get("ACELLORATOR_TOOL_MANIFEST", "registry/tool_manifest.json")
with open(manifest_path, "r", encoding="utf-8-sig") as f:
    manifest = json.load(f)

manifest_tools = {t["name"] for t in manifest["tools"]}

tools_root = os.environ.get("ACELLORATOR_TOOLS_ROOT", "tools")
actual_dirs = [
    d
    for d in os.listdir(tools_root)
    if os.path.isdir(os.path.join(tools_root, d)) and d.endswith("_cpp")
]

missing = []
for d in actual_dirs:
    if d not in manifest_tools:
        missing.append(d)

if missing:
    print(f"C++ directories not in {manifest_path}:")
    for d in missing:
        print(f"  - {d}")
else:
    print(f"All C++ directories are in {manifest_path}")
