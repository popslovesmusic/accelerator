import os
import json
import re
from pathlib import Path

def parse_markdown_item(file_path):
    content = file_path.read_text(encoding='utf-8')
    
    # Extract ID and Title from the first line (# L001 — Admissible Increment or # Theorem I — ...)
    header_match = re.search(r'^#\s+(?:(?:Lemma|Proof|Theorem)\s+)?(?:(L|P|T)(\d+)|Theorem\s+(I+V?|VI*|X|V))\s+—\s+(.*)$', content, re.MULTILINE)
    
    if not header_match:
        return None

    if header_match.group(1):
        item_id = f"{header_match.group(1)}{header_match.group(2)}"
        title = header_match.group(4).strip()
    else:
        # Roman numeral to T-number mapping for Theorems
        roman_map = {"I": "T001", "II": "T002", "III": "T003", "IV": "T004", "V": "T005"}
        item_id = roman_map.get(header_match.group(3), header_match.group(3))
        title = header_match.group(4).strip()
    
    # Extract sections using regex
    def get_section(section_name):
        # Handle numbered headers like "## 1. Abstract" or "## Abstract"
        pattern = rf"## (?:\d+\.\s+)?{section_name}\s+(.*?)(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    statement = get_section("Statement")
    if not statement: statement = get_section("Goal") # Proofs use "Goal"
    if not statement: statement = get_section("1. Abstract") # Theorems use "1. Abstract"
    if not statement: statement = get_section("Abstract")
    
    dependencies_raw = get_section("Dependencies")
    if not dependencies_raw: dependencies_raw = get_section("Uses") # Proofs use "Uses"
    if not dependencies_raw: dependencies_raw = get_section("2. Symbolic Trace (Formal Closure)") # Theorems use this
    if not dependencies_raw: dependencies_raw = get_section("Symbolic Trace (Formal Closure)")
    
    status = get_section("Status")
    if not status: 
        # Extract from a key-value style if in a list, handle optional bolding
        status_match = re.search(r'-\s+(?:\*\*)?Status:?(?:\*\*)?\s+(.*)', content)
        status = status_match.group(1).strip().strip('*') if status_match else "draft"
    else:
        # If it was matched as a section, try to find a list item within it
        status_match = re.search(r'-\s+(?:\*\*)?Status:?(?:\*\*)?\s+(.*)', status)
        if status_match:
            status = status_match.group(1).strip().strip('*')

    supersedes = get_section("Supersedes / Superseded-by")
    if not supersedes:
        # Check for inline Supersedes in Status or other sections
        super_match = re.search(r'-\s+(?:\*\*)?Supersedes:?(?:\*\*)?\s+(.*)', content)
        supersedes = super_match.group(1).strip().strip('*') if super_match else ""
    
    evidence_raw = get_section("Evidence")
    if not evidence_raw: evidence_raw = get_section("Verification") # Theorems use "Verification"
    
    evidence_paths = []
    # If no specific section found, search whole content as fallback
    search_text = evidence_raw if evidence_raw else content
    
    # Simple extraction of paths from markdown links or plain text
    # Match both [text](path) and raw results/path
    found = re.findall(r'\[.*?\]\((.*?)\)|(results/[\w\-/.]+)', search_text)
    for pair in found:
        path = pair[0] or pair[1]
        if path:
            # Normalize results path (remove leading ../)
            if "results/" in path:
                # Find start of results/ and take until end of string or next space/)
                start = path.find("results/")
                path = path[start:]
                # Trim trailing ) if captured from markdown
                if path.endswith(')'): path = path[:-1]
                evidence_paths.append(path.strip())
    
    # Remove duplicates
    evidence_paths = list(set(evidence_paths))

    # Expanded fields from Patch Group F
    proof_type = get_section("Proof Type")
    if not proof_type:
        proof_type_match = re.search(r'-\s+Proof Type:\s+(.*)', content)
        proof_type = proof_type_match.group(1).strip() if proof_type_match else "heuristic"
    
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

    # Process Theorems
    theorems_dir = root / "theorems"
    theorems = []
    if theorems_dir.exists():
        for f in theorems_dir.glob("T*.md"):
            item = parse_markdown_item(f)
            if item:
                existing = find_existing(item['item_id'], 'theorems')
                if existing:
                    if not item['evidence_paths'] and 'evidence_paths' in existing:
                        item['evidence_paths'] = existing['evidence_paths']
                    if item['status'] == "draft" and existing['status'] != "draft":
                        item['status'] = existing['status']
                theorems.append(item)

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
    theorems.sort(key=lambda x: x['item_id'])
    lemmas.sort(key=lambda x: x['item_id'])
    proofs.sort(key=lambda x: x['item_id'])

    registry['theorems'] = theorems
    registry['lemmas'] = lemmas
    registry['proofs'] = proofs

    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)
    
    print(f"Sync complete. Registered {len(theorems)} theorems, {len(lemmas)} lemmas, and {len(proofs)} proofs.")

if __name__ == "__main__":
    main()
