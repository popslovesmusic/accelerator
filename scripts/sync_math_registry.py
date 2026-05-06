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
    if not status: status = "draft"
    
    supersedes = get_section("Supersedes / Superseded-by")
    
    evidence_raw = get_section("Evidence")
    evidence_paths = []
    if evidence_raw:
        # Simple extraction of paths from markdown links or plain text
        evidence_paths = re.findall(r'\[.*?\]\((.*?)\)|results/\S+', evidence_raw)
        # Clean up paths
        evidence_paths = [p.strip() for p in evidence_paths if p.strip()]

    # Expanded fields from Patch Group F
    proof_type = get_section("Proof Type")
    if not proof_type: proof_type = "heuristic" # default
    
    def get_list_section(section_name):
        section = get_section(section_name)
        if not section: return []
        # Split by lines and remove bullet points/whitespace
        lines = [line.strip().lstrip('-').lstrip('*').strip() for line in section.split('\n') if line.strip()]
        return lines

    return {
        "item_id": item_id,
        "title": title,
        "statement": statement,
        "dependencies_raw": dependencies_raw,
        "status": status,
        "proof_type": proof_type,
        "object_classes": get_list_section("Object Classes"),
        "operators_used": get_list_section("Operators"),
        "constraints_used": get_list_section("Constraints"),
        "preserved_invariants": get_list_section("Invariants"),
        "dependent_lemmas": get_list_section("Dependent Lemmas"),
        "contradicted_by": get_list_section("Contradicted By"),
        "simulation_bindings": get_list_section("Simulation Bindings"),
        "known_scope_limits": get_list_section("Scope Limits"),
        "failure_conditions": get_list_section("Failure Conditions"),
        "supersedes": supersedes,
        "path": str(file_path.absolute().relative_to(Path.cwd().absolute())),
        "evidence_paths": evidence_paths
    }

def main():
    root = Path("docs/theory/foundational/5_03_26 unity/math")
    registry_path = Path("registry/math_registry.json")
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # Helper to find existing item for merging
    def find_existing(item_id, category):
        for item in registry.get(category, []):
            if item['item_id'] == item_id:
                return item
        return None

    # Process Lemmas
    lemmas_dir = root / "lemmas"
    lemmas = []
    for f in lemmas_dir.glob("L*.md"):
        if f.name == "LEMMA_TEMPLATE.md": continue
        item = parse_markdown_item(f)
        if item:
            existing = find_existing(item['item_id'], 'lemmas')
            if existing:
                # Merge: prefer file content, but keep evidence_paths if file is empty
                if not item['evidence_paths'] and 'evidence_paths' in existing:
                    item['evidence_paths'] = existing['evidence_paths']
                
                # Trust registry status if it's been upgraded and we have evidence
                if item['status'] == "draft" and existing['status'] != "draft":
                    if item['evidence_paths'] or existing.get('evidence_paths'):
                        item['status'] = existing['status']
            lemmas.append(item)
    
    # Process Proofs
    proofs_dir = root / "proofs"
    proofs = []
    for f in proofs_dir.glob("P*.md"):
        if f.name == "PROOF_TEMPLATE.md": continue
        item = parse_markdown_item(f)
        if item:
            existing = find_existing(item['item_id'], 'proofs')
            if existing:
                if not item['evidence_paths'] and 'evidence_paths' in existing:
                    item['evidence_paths'] = existing['evidence_paths']
                
                if item['status'] == "draft" and existing['status'] != "draft":
                    if item['evidence_paths'] or existing.get('evidence_paths'):
                        item['status'] = existing['status']
            proofs.append(item)

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
