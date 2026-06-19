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
                if obj["object_id"] == "ECON_APP_SIGMA_D_001":
                    obj["title"] = "Sigma_D"
                    obj["symbol"] = "Sigma_D"
                    obj["canonical_form"] = "Σ_D(G) = Σ_D(G')"
                    obj["status"] = "definition_candidate"
                    obj["source_bindings"] = ["registry/lexicon_gap_queue.json"]
                    obj["definition"] = "Define Sigma_D admissible equivalence criteria using Org_a closure, iff_R preservation, and orientation equivalence."
                    obj["equivalence_rules"] = {
                        "Sigma_D_equivalence": "Σ_D(G) = Σ_D(G') iff G and G' preserve the same Org_a-closed distinction organization under iff_R and orientation equivalence ≃_O.",
                        "requires": [
                          "Adm_Org(G)",
                          "Inv_D(G) = Inv_D(G')",
                          "G iff_R G'",
                          "G ≃_O G'",
                          "Preserve_D_recovery_behavior(G,G')"
                        ]
                      }
                    obj["relationship_to_Org_a"] = "Org_a defines admissible organization closure; Sigma_D defines equivalence of such closed organizations."
                    updated = True
                    break
            
            if updated:
                with open(formal_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated formal_object_registry.json for ECON_APP_SIGMA_D_001")
            else:
                print("ECON_APP_SIGMA_D_001 not found in formal_object_registry.json")
        except Exception as e:
            print(f"Error updating formal_object_registry.json: {e}")

    # 2. Update registry/lexicon_gap_queue.json
    gap_file = root / "registry/lexicon_gap_queue.json"
    if gap_file.exists():
        try:
            with open(gap_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            updated = False
            # Check in candidate_new_terms
            for term in data.get("candidate_new_terms", []):
                if term["term"] == "Sigma_D":
                    term["status"] = "GAP_EQUIVALENCE_DEFINITION_CANDIDATE"
                    updated = True
                    break
            # Check in queue
            if not updated:
                for term in data.get("queue", []):
                    if term["term"] == "Sigma_D":
                        term["status"] = "GAP_EQUIVALENCE_DEFINITION_CANDIDATE"
                        updated = True
                        break
                    
            if updated:
                with open(gap_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated lexicon_gap_queue.json for term 'Sigma_D'")
            else:
                print("Term 'Sigma_D' not found in lexicon_gap_queue.json")
        except Exception as e:
            print(f"Error updating lexicon_gap_queue.json: {e}")

    # 3. Update docs/economics/ssot/procedural_economics_ssot.md
    ssot_file = root / "docs/economics/ssot/procedural_economics_ssot.md"
    if ssot_file.exists():
        try:
            content = ssot_file.read_text(encoding="utf-8")
            
            # Target line for ECON_DEBT_0002
            target_line = "| ECON_DEBT_0002 | FOUNDATIONAL | OPEN | CRITICAL | Sigma_D admissible equivalence criteria undefined. | identity_app, recovery_app, deformation validation | economics_app |"
            replacement = "| ECON_DEBT_0002 | FOUNDATIONAL | PARTIALLY_RESOLVED_PENDING_QUALIFICATION_PASS | CRITICAL | Sigma_D admissible equivalence criteria candidate defined; awaiting qualification. | identity_app, recovery_app, deformation validation | economics_app |"
            
            if target_line in content:
                content = content.replace(target_line, replacement)
                ssot_file.write_text(content, encoding="utf-8")
                print("Successfully annotated ECON_DEBT_0002 in procedural_economics_ssot.md")
            else:
                print("ECON_DEBT_0002 target row not found in procedural_economics_ssot.md")
        except Exception as e:
            print(f"Error updating procedural_economics_ssot.md: {e}")

    # 4. Update docs/textbook/mono_process_textbook_complete.md
    textbook_file = root / "docs/textbook/mono_process_textbook_complete.md"
    if textbook_file.exists():
        try:
            textbook_content = textbook_file.read_text(encoding="utf-8")
            if "### Sigma_D: Admissible Distinction Organization Signature" not in textbook_content:
                
                new_section = (
                    "### Sigma_D: Admissible Distinction Organization Signature\n\n"
                    "The Admissible Distinction Organization Signature ($\\Sigma_D$) represents the equivalence class or signature of "
                    "$\\text{Org}_a$-closed distinction organizations. It is governed by the following core criteria:\n\n"
                    "- **Organizational Signature:** $\\Sigma_D$ is a preserved organization-signature, not an object label, state identity, or static substance representation.\n"
                    "- **Org_a Closure Requirement:** Evaluating $\\Sigma_D$ equivalence requires that both structures satisfy the organizational admissibility closure ($\\text{Adm}_{\\text{Org}}$). "
                    "No equivalence is defined for structures that fail $\\text{Org}_a$ closure.\n"
                    "- **Equivalence Preservation:** Equivalence $\\Sigma_D(G) = \\Sigma_D(G')$ requires the preservation of difference inventory, organization admissibility, "
                    "orientation-consistent topology, trace updates under $\\iff_R$, and recovery capacity:\n"
                    "  $$ G \\sim_{\\Sigma_D} G' := \\text{Adm}_{\\text{Org}}(G) \\land \\text{Adm}_{\\text{Org}}(G') \\land \\text{Inv}_D(G) = \\text{Inv}_D(G') \\land [G \\iff_R G'] \\land G \\simeq_O G' \\land \\text{Rec}_D(G, G') $$\n"
                    "- **Observability Constraints:** Perturbation metrics and simulation observables (such as `recovery_score`, `coupling_score`, `fragility_score`, and `deformation_score`) "
                    "may provide candidate evidence for equivalence testing but do not constitute final algebraic proof.\n\n"
                    "**Formal Block B.0.5: Sigma_D Signature Class**\n"
                    "$$ \\Sigma_D(G) := \\{ G' \\mid G \\sim_{\\Sigma_D} G' \\} $$\n"
                    "$$ \\text{Rec}_D(G, G') := \\text{preservation of admissible recovery behavior under registered perturbation classes} $$\n\n"
                    "**Commentary:**\n"
                    "Within these models, $\\Sigma_D$ remains a definition candidate. The recovery condition $\\text{Rec}_D$ serves as a candidate bridge to simulation evidence "
                    "and must remain qualified until the relevant perturbation classes are formally registered.\n"
                    "`ECON_DEBT_0002` must not be marked closed until the qualification and derivation passes succeed.\n\n"
                    "---\n\n"
                )
                
                # We want to insert the Sigma_D section right after "No \Sigma_D equivalence class should be closed before the \text{Org}_a axioms are formally derived.\n\n"
                # which is before the next "---\n\n### Core Operators"
                target_point = "No \\Sigma_D equivalence class should be closed before the \\text{Org}_a axioms are formally derived.\n\n---\n\n### Core Operators"
                replacement_point = "No \\Sigma_D equivalence class should be closed before the \\text{Org}_a axioms are formally derived.\n\n---\n\n" + new_section + "### Core Operators"
                
                if target_point in textbook_content:
                    textbook_content = textbook_content.replace(target_point, replacement_point)
                    print("Successfully inserted Sigma_D equivalence criteria section in mono_process_textbook_complete.md")
                else:
                    # Fallback check
                    marker = "---\n\n### Core Operators"
                    if marker in textbook_content:
                        textbook_content = textbook_content.replace(marker, new_section + "### Core Operators")
                        print("Fallback insertion of Sigma_D section in mono_process_textbook_complete.md")
            else:
                print("Sigma_D section already exists in mono_process_textbook_complete.md")

            if "| \\Sigma_D |" not in textbook_content:
                # Insert right after the Org_a row in the Core Operators table
                target_table_row = "| Org_a | Admissible Organization | GAP_AXIOM_DEFINITION_CANDIDATE | Organizes admissible distinction participation over a typed participation graph. |"
                new_table_row = "\n| \\Sigma_D | Distinction Organization Signature | GAP_EQUIVALENCE_DEFINITION_CANDIDATE | The equivalence class of Org_a-closed distinction organizations under iff_R and orientation equivalence. |"
                if target_table_row in textbook_content:
                    textbook_content = textbook_content.replace(target_table_row, target_table_row + new_table_row)
                    print("Successfully added Sigma_D to Core Operators table in mono_process_textbook_complete.md")
            else:
                print("Sigma_D already exists in Core Operators table")
                
            with open(textbook_file, "w", encoding="utf-8") as f:
                f.write(textbook_content)
                
        except Exception as e:
            print(f"Error updating mono_process_textbook_complete.md: {e}")

if __name__ == "__main__":
    main()
