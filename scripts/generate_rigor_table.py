import json

manifest_path = "tool_manifest.json"
with open(manifest_path, 'r', encoding='utf-8-sig') as f:
    manifest = json.load(f)

# Sort tools by class then name
tools = sorted(manifest["tools"], key=lambda x: (x["model_class"], x["name"]))

print("| Tool | Class | Status | Certification |")
print("| --- | --- | --- | --- |")
for t in tools:
    status = "Verified" if t.get("certification_level", "C0") != "C0" else "Provisional"
    print(f"| `{t['name']}` | {t['model_class']} | {status} | {t.get('certification_level', 'C0')} |")
