import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent.parent
    
    # 1. Update registry/formal_object_registry.json
    formal_registry_file = root / "registry/formal_object_registry.json"
    if formal_registry_file.exists():
        try:
            with open(formal_registry_file, "r", encoding="utf-8") as f:
                formal_data = json.load(f)
            
            existing_ids = {obj["object_id"] for obj in formal_data.get("objects", [])}
            
            new_objects = [
                {
                    "object_id": "OBJ-vertical-bar",
                    "object_class": "operator",
                    "title": "vertical_bar_operator",
                    "status": "provisional",
                    "source_bindings": [
                        "registry/lexicon_gap_queue.json"
                    ],
                    "dependency_links": [],
                    "claim_scope": "universal",
                    "governance_bindings": [
                        "charter_v2.3"
                    ],
                    "runtime_visibility": True
                },
                {
                    "object_id": "OBJ-orientation-space",
                    "object_class": "primitive",
                    "title": "orientation_space_O",
                    "status": "provisional",
                    "source_bindings": [
                        "registry/lexicon_gap_queue.json"
                    ],
                    "dependency_links": [],
                    "claim_scope": "universal",
                    "governance_bindings": [
                        "charter_v2.3"
                    ],
                    "runtime_visibility": True
                }
            ]
            
            added = 0
            for obj in new_objects:
                if obj["object_id"] not in existing_ids:
                    formal_data["objects"].append(obj)
                    added += 1
            
            if added > 0:
                with open(formal_registry_file, "w", encoding="utf-8") as f:
                    json.dump(formal_data, f, indent=2)
                print(f"Added {added} objects to formal_object_registry.json")
            else:
                print("formal_object_registry.json already has vertical_bar and orientation_space")
        except Exception as e:
            print(f"Error updating formal_object_registry.json: {e}")
            
    # 2. Update registry/operator_registry.json
    operator_registry_file = root / "registry/operator_registry.json"
    if operator_registry_file.exists():
        try:
            with open(operator_registry_file, "r", encoding="utf-8") as f:
                op_data = json.load(f)
                
            existing_symbols = {op["symbol"] for op in op_data.get("operators", [])}
            
            new_ops = [
                {
                    "symbol": "|",
                    "latex": "|",
                    "name": "vertical_bar_operator",
                    "domain": "Admissible distinction-participation separator inside grouped expressions",
                    "codomain": "Interface for co-participation in distinction-generating expressions",
                    "closure_condition": "A | B marks the oriented comparison interface through which A and B participate in a distinction-generating expression.",
                    "collapse_mode": "Legality Failure",
                    "composition_rules": [
                        "Used within TC_asym to mark co-participation in grouped expressions",
                        "Must be defined before Org_a closure is attempted"
                    ],
                    "status": "MUST_DEFINE_BEFORE_ORG_A_CLOSURE"
                }
            ]
            
            added = 0
            for op in new_ops:
                if op["symbol"] not in existing_symbols:
                    op_data["operators"].append(op)
                    added += 1
                    
            if added > 0:
                with open(operator_registry_file, "w", encoding="utf-8") as f:
                    json.dump(op_data, f, indent=2)
                print(f"Added {added} operators to operator_registry.json")
            else:
                print("operator_registry.json already has | operator")
        except Exception as e:
            print(f"Error updating operator_registry.json: {e}")

    # 3. Update registry/lexicon_gap_queue.json
    gap_queue_file = root / "registry/lexicon_gap_queue.json"
    if gap_queue_file.exists():
        try:
            with open(gap_queue_file, "r", encoding="utf-8") as f:
                gap_data = json.load(f)
                
            existing_terms = {term["term"] for term in gap_data.get("candidate_new_terms", [])}
            
            new_terms = [
                {
                    "term": "vertical_bar_operator",
                    "aliases": [
                        "vertical_bar",
                        "|"
                    ],
                    "status": "GAP_OPEN",
                    "default_claim_status": "PROVISIONAL",
                    "reason_for_induction": "CRITICAL_PATH_RESOLUTION_PATCH_001 target",
                    "source_context": {
                        "source_type": "research_output",
                        "source_path_or_note": "CRITICAL_PATH_RESOLUTION_PATCH_001"
                    },
                    "proposed_definition": "Define the vertical bar as the admissible distinction-participation separator inside grouped expressions.",
                    "induction_timestamp": "2026-06-18T23:22:13.000000"
                },
                {
                    "term": "orientation_space_O",
                    "aliases": [
                        "orientation_space",
                        "O"
                    ],
                    "status": "GAP_OPEN",
                    "default_claim_status": "PROVISIONAL",
                    "reason_for_induction": "CRITICAL_PATH_RESOLUTION_PATCH_001 target",
                    "source_context": {
                        "source_type": "research_output",
                        "source_path_or_note": "CRITICAL_PATH_RESOLUTION_PATCH_001"
                    },
                    "proposed_definition": "Define Orientation Space as the space of admissible participation directions available to distinction organizations.",
                    "induction_timestamp": "2026-06-18T23:22:13.000000"
                }
            ]
            
            added = 0
            for term in new_terms:
                if term["term"] not in existing_terms:
                    gap_data["candidate_new_terms"].append(term)
                    added += 1
                    
            if added > 0:
                with open(gap_queue_file, "w", encoding="utf-8") as f:
                    json.dump(gap_data, f, indent=2)
                print(f"Added {added} terms to lexicon_gap_queue.json")
            else:
                print("lexicon_gap_queue.json already has vertical_bar_operator and orientation_space_O")
        except Exception as e:
            print(f"Error updating lexicon_gap_queue.json: {e}")

if __name__ == "__main__":
    main()
