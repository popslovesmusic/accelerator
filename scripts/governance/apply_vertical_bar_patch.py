import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent.parent
    
    # 1. Update registry/formal_object_registry.json
    formal_file = root / "registry/formal_object_registry.json"
    if formal_file.exists():
        try:
            with open(formal_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            updated = False
            for obj in data.get("objects", []):
                if obj["object_id"] == "OBJ-vertical-bar":
                    obj["status"] = "definition_candidate"
                    obj["symbol"] = "|"
                    obj["canonical_form"] = "A | B"
                    obj["definition"] = "Define the vertical bar operator as the primitive admissible participation separator used inside distinction-generating expressions."
                    obj["operand_rules"] = {
                        "valid_operands": [
                            "primitive distinction candidates",
                            "already-admissible distinction expressions",
                            "grouped participation expressions",
                            "domain-specific projections explicitly typed as admissible operands"
                        ],
                        "invalid_operands": [
                            "untyped raw objects",
                            "unverified state labels",
                            "pure scalar quantities without participation type",
                            "projection-only analogies",
                            "semantic placeholders with no admissibility trace"
                        ]
                    }
                    obj["orientation_rules"] = {
                        "order_sensitive": True,
                        "orientation_statement": "A | B is not generally equivalent to B | A."
                    }
                    obj["closure_rules"] = {
                        "local_closure": "A bar expression is locally closed when both operands are admissibly typed and the interface relation is legally evaluable under D.",
                        "grouped_closure": "Grouped bar expressions require a separate group-closure rule."
                    }
                    obj["dependencies"] = []
                    obj["blocked_downstream_objects"] = [
                        "Org_a_axioms",
                        "Sigma_D_equivalence_criteria"
                    ]
                    updated = True
                    break
            
            if updated:
                with open(formal_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated formal_object_registry.json for OBJ-vertical-bar")
            else:
                print("OBJ-vertical-bar not found in formal_object_registry.json")
        except Exception as e:
            print(f"Error updating formal_object_registry.json: {e}")

    # 2. Update registry/operator_registry.json
    operator_file = root / "registry/operator_registry.json"
    if operator_file.exists():
        try:
            with open(operator_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            updated = False
            for op in data.get("operators", []):
                if op["symbol"] == "|":
                    op["status"] = "MUST_DEFINE_BEFORE_ORG_A_CLOSURE"
                    op["arity"] = 2
                    op["order_sensitive"] = True
                    op["admissibility_gate"] = "D(A|B) > epsilon_a"
                    op["noncommutative_by_default"] = True
                    op["group_closure_status"] = "unresolved"
                    updated = True
                    break
                    
            if updated:
                with open(operator_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated operator_registry.json for symbol '|'")
            else:
                print("Symbol '|' not found in operator_registry.json")
        except Exception as e:
            print(f"Error updating operator_registry.json: {e}")

    # 3. Update registry/lexicon_gap_queue.json
    gap_file = root / "registry/lexicon_gap_queue.json"
    if gap_file.exists():
        try:
            with open(gap_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            updated = False
            for term in data.get("candidate_new_terms", []):
                if term["term"] == "vertical_bar_operator":
                    term["status"] = "GAP_DEFINITION_CANDIDATE"
                    updated = True
                    break
                    
            if updated:
                with open(gap_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated lexicon_gap_queue.json for term 'vertical_bar_operator'")
            else:
                print("Term 'vertical_bar_operator' not found in lexicon_gap_queue.json")
        except Exception as e:
            print(f"Error updating lexicon_gap_queue.json: {e}")

if __name__ == "__main__":
    main()
