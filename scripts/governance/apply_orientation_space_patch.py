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
                if obj["object_id"] == "OBJ-orientation-space":
                    obj["status"] = "definition_candidate"
                    obj["symbol"] = "O"
                    obj["canonical_form"] = "O(G)"
                    obj["definition"] = "Define Orientation Space O as the admissible space of participation directions governing bar expressions, Org_a preservation, and knot-class selection."
                    obj["participation_graph_model"] = "G := (V, E_|, \u03c4, \u03c1)"
                    obj["orientation_assignment"] = "o \u2208 O(G)"
                    obj["orientation_equivalence"] = "G \u2243_O G' iff there exist o \u2208 O(G), o' \u2208 O(G') such that participation directions, roles, and closure are preserved under iff_R."
                    obj["relationship_to_bar_operator"] = "A|B carries orientation by default. Binary case O(A|B) and group case O(G) record the legal participation direction."
                    obj["relationship_to_Org_a"] = "Org_a must preserve admissible orientation structure across legal transformations."
                    obj["relationship_to_OPEN_BRIDGE_001"] = "Orientation functions as a topological selector constraint on admissible knot-class selection."
                    updated = True
                    break
            
            if updated:
                with open(formal_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated formal_object_registry.json for OBJ-orientation-space")
            else:
                print("OBJ-orientation-space not found in formal_object_registry.json")
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
                    op["orientation_space"] = "O"
                    op["reversal_rule"] = "Reversal is legal only if Rev_|(A,B) or higher grouped orientation equivalence is proven."
                    op["group_preservation_rule"] = "Preserve_O(G -> G') := \u2203o \u2208 O(G), \u2203o' \u2208 O(G') such that G iff_R G' while preserving admissible orientation."
                    op["noncommutative_by_default"] = True
                    updated = True
                    break
                    
            if updated:
                with open(operator_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated operator_registry.json for vertical bar orientation fields")
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
                if term["term"] == "orientation_space_O":
                    term["status"] = "GAP_DEFINITION_CANDIDATE"
                    updated = True
                    break
                    
            if updated:
                with open(gap_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated lexicon_gap_queue.json for term 'orientation_space_O'")
            else:
                print("Term 'orientation_space_O' not found in lexicon_gap_queue.json")
        except Exception as e:
            print(f"Error updating lexicon_gap_queue.json: {e}")

    # 4. Update registry/math/bridge_dependency_registry.json
    bridge_file = root / "registry/math/bridge_dependency_registry.json"
    if bridge_file.exists():
        try:
            with open(bridge_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            updated = False
            for dep in data.get("dependencies", []):
                if dep["bridge_id"] == "OPEN_BRIDGE_001":
                    dep["required_primitive_input"] = "orientation_space_O"
                    updated = True
                    break
                    
            if updated:
                with open(bridge_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated bridge_dependency_registry.json for OPEN_BRIDGE_001 annotation")
            else:
                print("Bridge 'OPEN_BRIDGE_001' not found in bridge_dependency_registry.json")
        except Exception as e:
            print(f"Error updating bridge_dependency_registry.json: {e}")

if __name__ == "__main__":
    main()
