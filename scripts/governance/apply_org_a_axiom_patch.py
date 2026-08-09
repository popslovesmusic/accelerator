import json
import re
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
                if obj["object_id"] == "ECON_APP_ORG_A_001":
                    obj["title"] = "Org_a"
                    obj["symbol"] = "Org_a"
                    obj["canonical_form"] = "Org_a(G)"
                    obj["status"] = "definition_candidate"
                    obj["source_bindings"] = ["registry/lexicon_gap_queue.json"]
                    obj["dependency_links"] = [
                        "OBJ-vertical-bar",
                        "OBJ-grouped-bar-closure",
                        "OBJ-orientation-space"
                    ]
                    obj["definition"] = "Define Org_a as admissible organization over distinction-generating participation fields, using vertical-bar closure, grouped-bar closure, and orientation preservation as explicit prerequisites."
                    obj["axiom_ids"] = ["ORG_A_AX_001", "ORG_A_AX_002", "ORG_A_AX_003"]
                    obj["relationship_to_D"] = "Org_a does not create distinction from nothing; it organizes already evaluable admissible distinction participation."
                    obj["relationship_to_iff_R"] = "iff_R supplies the admissible preservation relation under which Org_a transformations are judged."
                    obj["relationship_to_orientation"] = "Org_a must preserve admissible orientation structure across legal transformations."
                    obj["relationship_to_Sigma_D"] = "Sigma_D can now be drafted as an equivalence class or signature of Org_a-closed distinction organizations."
                    updated = True
                    break
            
            if updated:
                with open(formal_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated formal_object_registry.json for ECON_APP_ORG_A_001")
            else:
                print("ECON_APP_ORG_A_001 not found in formal_object_registry.json")
        except Exception as e:
            print(f"Error updating formal_object_registry.json: {e}")

    # 2. Append new operator to registry/operator_registry.json
    operator_file = root / "registry/operator_registry.json"
    if operator_file.exists():
        try:
            with open(operator_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            existing_symbols = {op.get("symbol") for op in data.get("operators", [])}
            
            if "Org_a" not in existing_symbols:
                new_op = {
                  "symbol": "Org_a",
                  "name": "Admissible Organization Operator",
                  "class": "admissible_organization",
                  "canonical_form": "Org_a(G)",
                  "status": "axiom_definition_candidate",
                  "arity": 1,
                  "domain": "Typed grouped participation graph G satisfying Adm_|^G(G) and O(G)",
                  "codomain": "Legally preserved organization of admissible distinction participation",
                  "input_requirements": {
                    "G": "typed grouped participation graph",
                    "requires": [
                      "Adm_|^G(G)",
                      "exists o in O(G) such that Adm_O(G,o)",
                      "Eval_D^G(G)",
                      "D_G(G) > epsilon_a"
                    ],
                    "invalid_inputs": [
                      "untyped operand lists",
                      "binary pairs without declared grouping",
                      "orientation-free structures",
                      "projection-only analogies",
                      "scalar equality classes"
                    ]
                  },
                  "axioms": [
                    {
                      "axiom_id": "ORG_A_AX_001",
                      "name": "Inventory Preservation",
                      "statement": "Legal transformations under Org_a must preserve the admissible distinction inventory of G.",
                      "candidate_form": "Inv_D(G) = Inv_D(G') under G iff_R G'",
                      "meaning": "The organization may deform, regroup, or transform only if the participating distinction inventory remains traceable."
                    },
                    {
                      "axiom_id": "ORG_A_AX_002",
                      "name": "Admissibility Conservation",
                      "statement": "Every legal transformation under Org_a must preserve admissibility of the organized participation field.",
                      "candidate_form": "Org_a(G) and G iff_R G' implies Adm_a(G')",
                      "meaning": "No organization remains legal if transformation causes its distinction participation to fall below epsilon_a or violate typed participation."
                    },
                    {
                      "axiom_id": "ORG_A_AX_003",
                      "name": "Topological Consistency",
                      "statement": "Legal transformations under Org_a must preserve orientation-consistent participation structure.",
                      "candidate_form": "Org_a(G) and G iff_R G' implies G ≃_O G'",
                      "meaning": "The organization is preserved through admissible relational structure, not by visual shape or object identity."
                    }
                  ],
                  "derived_closure_candidate": {
                    "symbol": "Adm_Org",
                    "candidate_formula": "Adm_Org(G) := Adm_|^G(G) \u2227 \u2203o\u2208O(G) Adm_O(G,o) \u2227 Eval_D^G(G) \u2227 D_G(G)>epsilon_a \u2227 InvPres_D(G) \u2227 AdmCons_a(G) \u2227 TopCons_O(G)",
                    "interpretation": "An Org_a expression is admissibly closed only when grouped participation, orientation, distinction evaluation, inventory preservation, admissibility conservation, and topological consistency all hold."
                  },
                  "dependencies": [
                    "VERTICAL_BAR_OPERATOR_DEFINITION_PASS_001",
                    "VERTICAL_BAR_OPERATOR_GROUP_CLOSURE_PASS_001",
                    "ORIENTATION_SPACE_DEFINITION_PASS_001"
                  ],
                  "downstream_unblocks": [
                    "Sigma_D_equivalence_criteria",
                    "ECON_DEBT_0001",
                    "ECON_DEBT_0002"
                  ]
                }
                data["operators"].append(new_op)
                with open(operator_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully added symbol 'Org_a' to operator_registry.json")
            else:
                print("Symbol 'Org_a' already exists in operator_registry.json")
        except Exception as e:
            print(f"Error updating operator_registry.json: {e}")

    # 3. Update registry/lexicon_gap_queue.json
    gap_file = root / "registry/lexicon_gap_queue.json"
    if gap_file.exists():
        try:
            with open(gap_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            updated = False
            # Check in candidate_new_terms
            for term in data.get("candidate_new_terms", []):
                if term["term"] == "Org_a":
                    term["status"] = "GAP_AXIOM_DEFINITION_CANDIDATE"
                    updated = True
                    break
            # Check in queue
            if not updated:
                for term in data.get("queue", []):
                    if term["term"] == "Org_a":
                        term["status"] = "GAP_AXIOM_DEFINITION_CANDIDATE"
                        updated = True
                        break
                    
            if updated:
                with open(gap_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated lexicon_gap_queue.json for term 'Org_a'")
            else:
                print("Term 'Org_a' not found in lexicon_gap_queue.json")
        except Exception as e:
            print(f"Error updating lexicon_gap_queue.json: {e}")

    # 4. Update docs/economics/ssot/procedural_economics_ssot.md
    ssot_file = root / "docs/economics/ssot/procedural_economics_ssot.md"
    if ssot_file.exists():
        try:
            content = ssot_file.read_text(encoding="utf-8")
            
            # Target line for ECON_DEBT_0001
            target_line = "| ECON_DEBT_0001 | FOUNDATIONAL | OPEN | CRITICAL | Org_a axioms not formally defined. | formal Sigma_D construction, continuity derivation, recovery derivation | economics_app |"
            replacement = "| ECON_DEBT_0001 | FOUNDATIONAL | PARTIALLY_RESOLVED_PENDING_DERIVATION_PASS | CRITICAL | Org_a axioms defined as definition candidates; awaiting derivation. | formal Sigma_D construction, continuity derivation, recovery derivation | economics_app |"
            
            if target_line in content:
                content = content.replace(target_line, replacement)
                ssot_file.write_text(content, encoding="utf-8")
                print("Successfully annotated ECON_DEBT_0001 in procedural_economics_ssot.md")
            else:
                print("ECON_DEBT_0001 target row not found in procedural_economics_ssot.md")
        except Exception as e:
            print(f"Error updating procedural_economics_ssot.md: {e}")

    # 5. Update docs/textbook/mono_process_textbook_complete.md
    # (Since this was already added successfully in the first pass, we make sure it is not added twice,
    # but let's check if the section is already there).
    textbook_file = root / "docs/textbook/mono_process_textbook_complete.md"
    if textbook_file.exists():
        try:
            textbook_content = textbook_file.read_text(encoding="utf-8")
            if "### Org_a: Admissible Organization Axioms" not in textbook_content:
                target_insertion_point = "### Core Operators"
                new_section = (
                    "### Org_a: Admissible Organization Axioms\n\n"
                    "The Admissible Organization Operator ($\\text{Org}_a$) organizes admissible distinction participation over structured fields; "
                    "it does not collect objects, semantic classes, or static entities. It is constrained by the following candidate axioms:\n\n"
                    "- **Inventory Preservation ($\\text{ORG\\_A\\_AX\\_001}$):** Legal transformations under $\\text{Org}_a$ must preserve the admissible distinction inventory of the participation graph $G$.\n"
                    "  $$ \\text{Inv}_D(G) = \\text{Inv}_D(G') \\quad \\text{under} \\quad G \\iff_R G' $$\n"
                    "  The organization may deform or couple only if the participating difference trace remains traceable.\n"
                    "- **Admissibility Conservation ($\\text{ORG\\_A\\_AX\\_002}$):** Every legal transformation under $\\text{Org}_a$ must conserve the admissibility of the organized participation field.\n"
                    "  $$ \\text{Org}_a(G) \\land [G \\iff_R G'] \\implies \\text{Adm}_a(G') $$\n"
                    "  No organization remains valid if transformation causes its distinction evaluation to violate admissibility constraints.\n"
                    "- **Topological Consistency ($\\text{ORG\\_A\\_AX\\_003}$):** Legal transformations under $\\text{Org}_a$ must preserve the orientation-consistent topological structure.\n"
                    "  $$ \\text{Org}_a(G) \\land [G \\iff_R G'] \\implies G \\simeq_O G' $$\n"
                    "  The relational crossings and roles of the participation graph must be preserved.\n\n"
                    "**Formal Block B.0.4: Admissible Organization Closure**\n"
                    "$$ \\text{Adm}_{\\text{Org}}(G) := \\text{Adm}_{|}^G(G) \\land [\\exists o \\in O(G), \\text{Adm}_O(G, o)] \\land \\text{Eval}_D^G(G) \\land D_G(G) > \\epsilon_a \\land \\text{InvPres}_D(G) \\land \\text{AdmCons}_a(G) \\land \\text{TopCons}_O(G) $$\n\n"
                    "**Commentary:**\n"
                    "Within these models, these axioms are definition candidates only. They are not fully proven theorems until qualified or derived directly from $D(A|B) > \\epsilon_a$ and $\\iff_R$.\n"
                    "Furthermore, the construction of the signature structure $\\Sigma_D$ depends directly on $\\text{Org}_a$ closure:\n"
                    "$$ \\Sigma_D := [G]_{\\text{Org}_a, \\iff_R, \\simeq_O} $$\n"
                    "No $\\Sigma_D$ equivalence class should be closed before the $\\text{Org}_a$ axioms are formally derived.\n\n"
                    "---\n\n"
                )
                marker = "---\n\n### Core Operators"
                if marker in textbook_content:
                    textbook_content = textbook_content.replace(marker, new_section + "### Core Operators")
                    print("Successfully inserted Org_a axioms section in mono_process_textbook_complete.md")
            else:
                print("Org_a axioms section already exists in mono_process_textbook_complete.md")

            if "| Org_a |" not in textbook_content:
                target_table_row = "| \\| | Vertical Bar Operator | MUST_DEFINE_BEFORE_ORG_A_CLOSURE | Separator for co-participation inside distinction expressions. |"
                new_table_row = "\n| Org_a | Admissible Organization | GAP_AXIOM_DEFINITION_CANDIDATE | Organizes admissible distinction participation over a typed participation graph. |"
                if target_table_row in textbook_content:
                    textbook_content = textbook_content.replace(target_table_row, target_table_row + new_table_row)
                    print("Successfully added Org_a to Core Operators table in mono_process_textbook_complete.md")
            else:
                print("Org_a already exists in Core Operators table")
                
            with open(textbook_file, "w", encoding="utf-8") as f:
                f.write(textbook_content)
                
        except Exception as e:
            print(f"Error updating mono_process_textbook_complete.md: {e}")

if __name__ == "__main__":
    main()
