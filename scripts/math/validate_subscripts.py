import os
import json
import re
from pathlib import Path

def run_subscript_audit():
    # Load registry
    registry_path = Path("registry/operator_subscript_registry.json")
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    valid_subscripts = {s["symbol"] for s in registry["operator_subscript_registry"]["subscripts"]}
    # Add 'xb' which is in the operator registry and used in some schema versions
    valid_subscripts.add("xb")
    # Add 'kappa' as a generic selector mentioned in schema v1.4
    valid_subscripts.add("kappa")
    valid_subscripts.add("\u03ba")
    
    # Pattern to find subscripts in relations
    # Matches \Leftrightarrow_{...} or <->_{...} or ⇔_{...}
    # Using more specific character class to avoid trailing punctuation
    patterns = [
        r"\\Leftrightarrow_\{?([a-zA-Z0-9\u0370-\u03ff_]+)\}?",
        r"<->_\{?([a-zA-Z0-9\u0370-\u03ff_]+)\}?",
        r"\u21d4_\{?([a-zA-Z0-9\u0370-\u03ff_]+)\}?"
    ]
    
    audit_results = {
        "status": "passed",
        "violations": [],
        "findings": []
    }
    
    docs_to_scan = list(Path("docs/math").glob("*.md")) + list(Path("docs").glob("MONO_PROCESS_MATHEMATICAL_SCHEMA_*.md"))
    
    for doc in docs_to_scan:
        with open(doc, "r", encoding="utf-8") as f:
            content = f.read()
            
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for m in matches:
                sub = m.group(1)
                # Clean LaTeX or markup if any
                sub_clean = sub.strip("{}")
                
                if sub_clean not in valid_subscripts:
                    audit_results["status"] = "failed"
                    audit_results["violations"].append({
                        "file": str(doc),
                        "expression": m.group(0),
                        "subscript": sub_clean,
                        "reason": "Subscript not found in operator_subscript_registry"
                    })
                else:
                    audit_results["findings"].append({
                        "file": str(doc),
                        "subscript": sub_clean,
                        "status": "valid"
                    })

    # Save audit report
    out_dir = Path("outputs/audits")
    os.makedirs(out_dir, exist_ok=True)
    with open(out_dir / "subscript_operator_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)
        
    print(f"Subscript Audit Complete. Status: {audit_results['status']}")
    if audit_results["status"] == "failed":
        print(f"Found {len(audit_results['violations'])} violations.")
    else:
        print("All subscripts validated.")

if __name__ == "__main__":
    run_subscript_audit()
