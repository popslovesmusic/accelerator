import os
import json
import re
from pathlib import Path

def parse_markdown_item(file_path):
    content = file_path.read_text(encoding='utf-8')
    
    # Extract ID and Title from the first line (# L001 — Admissible Increment)
    header_match = re.search(r'^#\s+(L|P)(\d+)\s+—\s+(.*)$', content, re.MULTILINE)
    if not header_match:
        return None
    
    item_id = f"{header_match.group(1)}{header_match.group(2)}"
    title = header_match.group(3).strip()
    
    # Extract sections using regex
    def get_section(section_name):
        pattern = rf"## {section_name}\s+(.*?)(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    statement = get_section("Statement")
    if not statement: statement = get_section("Goal") # Proofs use "Goal"
    
    dependencies_raw = get_section("Dependencies")
    if not dependencies_raw: dependencies_raw = get_section("Uses") # Proofs use "Uses"
    
    status = get_section("Status")
    
    supersedes = get_section("Supersedes / Superseded-by")
    
    return {
        "item_id": item_id,
        "title": title,
        "statement": statement,
        "dependencies_raw": dependencies_raw,
        "status": status,
        "supersedes": supersedes,
        "path": str(file_path.absolute().relative_to(Path.cwd().absolute()))
    }

def main():
    root = Path("docs/theory/foundational/5_03_26 unity/math")
    registry_path = Path("registry/math_registry.json")
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # Process Lemmas
    lemmas_dir = root / "lemmas"
    lemmas = []
    for f in lemmas_dir.glob("L*.md"):
        if f.name == "LEMMA_TEMPLATE.md": continue
        item = parse_markdown_item(f)
        if item: lemmas.append(item)
    
    # Process Proofs
    proofs_dir = root / "proofs"
    proofs = []
    for f in proofs_dir.glob("P*.md"):
        if f.name == "PROOF_TEMPLATE.md": continue
        item = parse_markdown_item(f)
        if item: proofs.append(item)

    # Simple sort by ID
    lemmas.sort(key=lambda x: x['item_id'])
    proofs.sort(key=lambda x: x['item_id'])

    registry['lemmas'] = lemmas
    registry['proofs'] = proofs

    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)
    
    print(f"Sync complete. Registered {len(lemmas)} lemmas and {len(proofs)} proofs.")

if __name__ == "__main__":
    main()
