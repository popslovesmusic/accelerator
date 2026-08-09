import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent.parent
    
    # 1. Update registry/operator_registry.json
    operator_file = root / "registry/operator_registry.json"
    if operator_file.exists():
        try:
            with open(operator_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            updated = False
            for op in data.get("operators", []):
                if op["symbol"] == "|":
                    op["group_closure_status"] = "DEFINITION_CANDIDATE"
                    op["group_closure_symbol"] = "Adm_|^G"
                    op["associativity_default"] = "NON_ASSOCIATIVE_UNTIL_PROVEN"
                    op["permutation_default"] = "NON_PERMUTABLE_UNTIL_PROVEN"
                    op["triadic_special_case"] = True
                    op["orientation_dependency"] = "Preserve_O(G)"
                    updated = True
                    break
                    
            if updated:
                with open(operator_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated operator_registry.json for grouped closure")
            else:
                print("Symbol '|' not found in operator_registry.json")
        except Exception as e:
            print(f"Error updating operator_registry.json: {e}")

    # 2. Update registry/formal_object_registry.json
    formal_file = root / "registry/formal_object_registry.json"
    if formal_file.exists():
        try:
            with open(formal_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            existing_ids = {obj["object_id"] for obj in data.get("objects", [])}
            
            new_obj = {
                "object_id": "OBJ-grouped-bar-closure",
                "object_class": "operator",
                "title": "grouped_bar_closure",
                "status": "definition_candidate",
                "source_bindings": [
                    "registry/lexicon_gap_queue.json"
                ],
                "dependency_links": [
                    "OBJ-vertical-bar"
                ],
                "claim_scope": "universal",
                "governance_bindings": [
                    "charter_v2.3"
                ],
                "runtime_visibility": True,
                "canonical_forms": [
                    "A | B | C",
                    "(A | B) | C",
                    "A | (B | C)",
                    "A_1 | A_2 | ... | A_n"
                ],
                "group_operand_rules": {
                    "minimum_arity": 2,
                    "n_ary_extension": True,
                    "operand_requirement": "Every participant A_i must satisfy Typed_a(A_i) or be explicitly marked as pending admissibility qualification.",
                    "interface_requirement": "Every adjacent or declared interface A_i | A_j must be legally evaluable under D or a registered successor evaluator."
                },
                "group_closure_candidate": {
                    "symbol": "Adm_|^G",
                    "form": "Adm_|^G(A_1,...,A_n; G)"
                },
                "associativity_rules": {
                    "default": "NON_ASSOCIATIVE_UNTIL_PROVEN",
                    "statement": "(A|B)|C is not automatically equivalent to A|(B|C)."
                },
                "permutation_rules": {
                    "default": "NON_PERMUTABLE_UNTIL_PROVEN",
                    "statement": "A|B|C is not automatically equivalent to B|A|C, A|C|B, or any other permutation."
                },
                "triadic_closure_rules": {
                    "status": "FIRST_CLASS_SPECIAL_CASE",
                    "canonical_triad": "A | B | C"
                }
            }
            
            if new_obj["object_id"] not in existing_ids:
                data["objects"].append(new_obj)
                with open(formal_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully added OBJ-grouped-bar-closure to formal_object_registry.json")
            else:
                print("OBJ-grouped-bar-closure already exists in formal_object_registry.json")
        except Exception as e:
            print(f"Error updating formal_object_registry.json: {e}")

    # 3. Update registry/lexicon_gap_queue.json
    gap_file = root / "registry/lexicon_gap_queue.json"
    if gap_file.exists():
        try:
            with open(gap_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            existing_terms = {term["term"] for term in data.get("candidate_new_terms", [])}
            
            new_term = {
                "term": "grouped_bar_closure",
                "aliases": [
                    "grouped_participation",
                    "triadic_participation"
                ],
                "status": "GAP_DEFINITION_CANDIDATE",
                "default_claim_status": "PROVISIONAL",
                "reason_for_induction": "VERTICAL_BAR_OPERATOR_GROUP_CLOSURE_PASS_001 target",
                "source_context": {
                    "source_type": "research_output",
                    "source_path_or_note": "VERTICAL_BAR_OPERATOR_GROUP_CLOSURE_PASS_001"
                },
                "proposed_definition": "Define grouped vertical-bar participation rules for expressions with more than two participants.",
                "induction_timestamp": "2026-06-18T23:27:03.000000"
            }
            
            if new_term["term"] not in existing_terms:
                data["candidate_new_terms"].append(new_term)
                with open(gap_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully added term 'grouped_bar_closure' to lexicon_gap_queue.json")
            else:
                print("Term 'grouped_bar_closure' already exists in lexicon_gap_queue.json")
        except Exception as e:
            print(f"Error updating lexicon_gap_queue.json: {e}")

if __name__ == "__main__":
    main()
