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
    manifest_path = Path("registry/governance_manifest.json")
    
    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}")
        return

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    nodes = manifest.get("nodes", {})
    edges = manifest.get("edges", [])

    # Process categories
    categories = {
        "theorems": ("theorems", "T*.md"),
        "lemmas": ("lemmas", "L*.md"),
        "proofs": ("proofs", "P*.md")
    }

    for type_name, (folder, pattern) in categories.items():
        folder_path = root / folder
        if not folder_path.exists(): continue
        
        for f in folder_path.glob(pattern):
            if f.name in ["LEMMA_TEMPLATE.md", "PROOF_TEMPLATE.md"]: continue
            
            item = parse_markdown_item(f)
            if not item: continue
            
            iid = item["item_id"]
            node_type = type_name[:-1] # theorem, lemma, proof
            
            # Update Node
            nodes[iid] = {
                "type": node_type,
                "status": item.get("status", "draft"),
                "data": item
            }
            
            # Update Edges (verified_by)
            for ep in item.get("evidence_paths", []):
                run_name = Path(ep).parent.name if "paper.md" in ep else Path(ep).name
                if run_name == "data": run_name = Path(ep).parent.name
                
                # Check for existing verified_by edge
                new_edge = {"source": iid, "target": run_name, "relation": "verified_by"}
                if new_edge not in edges:
                    edges.append(new_edge)

    manifest["nodes"] = nodes
    manifest["edges"] = edges

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    math_count = len([n for n in nodes.values() if n.get("type") in ["theorem", "lemma", "proof"]])
    print(f"Sync complete. Registered {math_count} mathematical items in the unified manifest.")

if __name__ == "__main__":
    main()
