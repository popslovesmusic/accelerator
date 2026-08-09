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
                    obj["status"] = "qualified_definition_candidate"
                    obj["qualification_test_references"] = ["QUAL_ORG_A_001", "QUAL_ORG_A_002"]
                    updated = True
                elif obj["object_id"] == "ECON_APP_SIGMA_D_001":
                    obj["status"] = "qualified_equivalence_candidate"
                    obj["qualification_test_references"] = ["QUAL_SIGMA_D_001", "QUAL_SIGMA_D_002"]
                    updated = True
            
            if updated:
                with open(formal_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated formal_object_registry.json for Org_a and Sigma_D qualification")
            else:
                print("Org_a or Sigma_D objects not found in formal_object_registry.json")
        except Exception as e:
            print(f"Error updating formal_object_registry.json: {e}")

    # 2. Update registry/lexicon_gap_queue.json
    gap_file = root / "registry/lexicon_gap_queue.json"
    if gap_file.exists():
        try:
            with open(gap_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            updated = False
            for term in data.get("candidate_new_terms", []) + data.get("queue", []):
                if term["term"] == "Org_a":
                    term["status"] = "GAP_QUALIFIED_DEFINITION_CANDIDATE"
                    updated = True
                elif term["term"] == "Sigma_D":
                    term["status"] = "GAP_QUALIFIED_EQUIVALENCE_CANDIDATE"
                    updated = True
                    
            if updated:
                with open(gap_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated lexicon_gap_queue.json for term qualification statuses")
            else:
                print("Terms not found in lexicon_gap_queue.json queue")
        except Exception as e:
            print(f"Error updating lexicon_gap_queue.json: {e}")
 
    # 3. Update docs/economics/ssot/procedural_economics_ssot.md
    ssot_file = root / "docs/economics/ssot/procedural_economics_ssot.md"
    if ssot_file.exists():
        try:
            content = ssot_file.read_text(encoding="utf-8")
            
            # Target line for ECON_DEBT_0001
            target_line_1 = "| ECON_DEBT_0001 | FOUNDATIONAL | PARTIALLY_RESOLVED_PENDING_DERIVATION_PASS | CRITICAL | Org_a axioms defined in L115 (ORG_A_AX_001, ORG_A_AX_002, ORG_A_AX_003); awaiting formal derivation from core primitives. | formal Sigma_D construction, continuity derivation, recovery derivation | economics_app |"
            replacement_1 = "| ECON_DEBT_0001 | FOUNDATIONAL | QUALIFIED_CANDIDATE_PENDING_FORMAL_DERIVATION | CRITICAL | Org_a axioms structurally qualified; awaiting formal derivation. | formal Sigma_D construction, continuity derivation, recovery derivation | economics_app |"
            
            # Target line for ECON_DEBT_0002
            target_line_2 = "| ECON_DEBT_0002 | FOUNDATIONAL | PARTIALLY_RESOLVED_PENDING_QUALIFICATION_PASS | CRITICAL | Sigma_D admissible equivalence criteria candidate defined; awaiting qualification. | identity_app, recovery_app, deformation validation | economics_app |"
            replacement_2 = "| ECON_DEBT_0002 | FOUNDATIONAL | QUALIFIED_CANDIDATE_PENDING_REC_D_FORMALIZATION | CRITICAL | Sigma_D criteria structurally qualified; awaiting Rec_D registration. | identity_app, recovery_app, deformation validation | economics_app |"
            
            updated = False
            if target_line_1 in content:
                content = content.replace(target_line_1, replacement_1)
                updated = True
            if target_line_2 in content:
                content = content.replace(target_line_2, replacement_2)
                updated = True
                
            if updated:
                ssot_file.write_text(content, encoding="utf-8")
                print("Successfully annotated ECON_DEBT_0001 and ECON_DEBT_0002 to qualified candidate statuses")
            else:
                print("Debt rows not found in procedural_economics_ssot.md")
        except Exception as e:
            print(f"Error updating procedural_economics_ssot.md: {e}")

    # 4. Update docs/economics/evidence/simulation_evidence_registry.json
    sim_ev_file = root / "docs/economics/evidence/simulation_evidence_registry.json"
    if sim_ev_file.exists():
        try:
            with open(sim_ev_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            updated = False
            for ev in data.get("evidence_objects", []):
                if ev["evidence_id"] == "ECON_EVIDENCE_0002":
                    ev["observables_status"] = "Topology observables are candidate evidence for Rec_D recovery behavior only, not final proof of Sigma_D equivalence."
                    updated = True
                    break
                    
            if updated:
                with open(sim_ev_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("Successfully updated simulation_evidence_registry.json with Rec_D annotation")
            else:
                print("ECON_EVIDENCE_0002 not found in simulation_evidence_registry.json")
        except Exception as e:
            print(f"Error updating simulation_evidence_registry.json: {e}")

    # 5. Update docs/textbook/mono_process_textbook_complete.md
    textbook_file = root / "docs/textbook/mono_process_textbook_complete.md"
    if textbook_file.exists():
        try:
            textbook_content = textbook_file.read_text(encoding="utf-8")
            if "### Qualification Status of Org_a and Sigma_D" not in textbook_content:
                
                new_section = (
                    "### Qualification Status of Org_a and Sigma_D\n\n"
                    "The operators and signatures defined in this stage are structurally qualified but remain mathematically open. "
                    "They are subject to the following constraints:\n\n"
                    "- **Org_a Axioms Status:** The axioms of $\\text{Org}_a$ (Inventory Preservation, Admissibility Conservation, Topological Consistency) "
                    "are structurally qualified as consistent definition candidates, but they are not theorem-closed. "
                    "Formal derivation from the primitive mismatch evaluation $D(A|B) > \\epsilon_a$ and the recursive closure relation $\\iff_R$ is still required.\n"
                    "- **Sigma_D Equivalence Status:** $\\Sigma_D$ equivalence is structurally qualified as a candidate relation, "
                    "but its completeness remains dependent on the formalization of $\\text{Rec}_D$ under registered perturbation classes.\n"
                    "- **Simulation Limits:** Existing multi-model simulation campaigns (such as `SIM_TOPOLOGY_001_EXECUTABLE`) "
                    "provide supporting evidence for candidate recovery behavior criteria under perturbation, but they do not close the formal math program debts.\n"
                    "- **Status of Debts:** In alignment with procedural governance, the foundational debt items `ECON_DEBT_0001` and `ECON_DEBT_0002` "
                    "remain **OPEN** in qualified-candidate status.\n\n"
                    "**Formal Block B.0.6: Stage 1 Qualification Status**\n"
                    "$$ \\text{Stage\\_1\\_Status} := \\text{STRUCTURALLY\\_QUALIFIED\\_NOT\\_FORMALLY\\_CLOSED} $$\n\n"
                    "---\n\n"
                )
                
                # We insert this right after "No \Sigma_D equivalence class should be closed before the \text{Org}_a axioms are formally derived.\n\n---\n\n"
                # (which represents the end of the Sigma_D section commentary, right before "### Core Operators" or similar).
                # Wait, the Sigma_D section ends with:
                # `ECON_DEBT_0002 must not be marked closed until the qualification and derivation passes succeed.\n\n---\n\n`
                # Let's search for this pattern and insert right after it.
                target_point = "`ECON_DEBT_0002` must not be marked closed until the qualification and derivation passes succeed.\n\n---\n\n"
                replacement_point = target_point + new_section
                
                if target_point in textbook_content:
                    textbook_content = textbook_content.replace(target_point, replacement_point)
                    print("Successfully inserted Qualification Status section in mono_process_textbook_complete.md")
                else:
                    # Fallback check
                    marker = "---\n\n### Core Operators"
                    if marker in textbook_content:
                        textbook_content = textbook_content.replace(marker, new_section + "### Core Operators")
                        print("Fallback insertion of Qualification Status section in mono_process_textbook_complete.md")
            else:
                print("Qualification Status section already exists in mono_process_textbook_complete.md")
                
            with open(textbook_file, "w", encoding="utf-8") as f:
                f.write(textbook_content)
                
        except Exception as e:
            print(f"Error updating mono_process_textbook_complete.md: {e}")

if __name__ == "__main__":
    main()
