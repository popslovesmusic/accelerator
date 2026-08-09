import json
with open('registry/tool_manifest.json', 'r', encoding='utf-8-sig') as f:
    m = json.load(f)
for t in m.get("tools", []):
    name = t.get("name")
    cert = t.get("certification_level")
    lang = t.get("implementation_language")
    pk = t.get("latest_equivalence_packet")
    print(f"{name}: {cert} ({lang}) PK: {pk}")
