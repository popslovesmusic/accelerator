import json
import re
import argparse
from pathlib import Path

# Lexicon Governor: Minimizes Agent Overhead by offloading compliance checks.
# Adheres to Compliance Charter v2.3

class LexiconGovernor:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.charter = self._load_json(repo_root / "registry/compliance_charter_v2_3.json")
        self.canonical = self._load_json(repo_root / "registry/lexicon_canonical.json")
        self.alias_map = self._load_json(repo_root / "registry/lexicon_alias_map.json").get("aliases", {})
        
        self.prohibited = set(self.charter.get("compliance_rules", {}).get("prohibited_primitives", []))
        self.replacements = {item["target"]: item["replacement"] 
                            for item in self.charter.get("compliance_rules", {}).get("mandatory_replacements", [])}

    def _load_json(self, path: Path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return {}

    def audit_text(self, text: str):
        violations = []
        suggestions = []
        
        # 1. Prohibited Primitives Check
        for p in self.prohibited:
            # Use word boundaries to avoid partial matches
            if re.search(rf"\b{re.escape(p)}\b", text, re.IGNORECASE):
                violations.append({"type": "prohibited_primitive", "term": p})

        # 2. Mandatory Replacements Check
        for target, replacement in self.replacements.items():
            if re.search(rf"\b{re.escape(target)}\b", text, re.IGNORECASE):
                violations.append({"type": "mandatory_replacement", "term": target, "suggested": replacement})

        # 3. Data Provenance Check (Basic heuristic for sim_id)
        has_sim_id = bool(re.search(r"sim_\d+|batch_\d+|202\d-\d{2}-\d{2}", text))
        
        # 4. Lexicon Normalization Check
        # Find words that might be terms but are unnormalized surface forms
        tokens = re.findall(r"\b[A-Za-z0-9_]+\b", text)
        unnormalized = []
        for t in tokens:
            t_lower = t.lower()
            if t_lower in self.alias_map and self.alias_map[t_lower] != t:
                unnormalized.append({"term": t, "normalized": self.alias_map[t_lower]})

        return {
            "compliant": len(violations) == 0 and has_sim_id,
            "violations": violations,
            "unnormalized_terms": unnormalized[:10], # Limit output to conserve context
            "data_provenance_found": has_sim_id,
            "charter_version": self.charter.get("charter_version", "unknown")
        }

def main():
    parser = argparse.ArgumentParser(description="Audit text for Lexicon and Charter compliance.")
    parser.add_argument("--text", help="Text to audit")
    parser.add_argument("--file", help="File to audit")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    governor = LexiconGovernor(root)

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    elif args.text:
        content = args.text
    else:
        print("Provide --text or --file")
        return

    result = governor.audit_text(content)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
