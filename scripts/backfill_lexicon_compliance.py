import json
import os

CANONICAL_PATH = "registry/lexicon_canonical.json"
VALIDATION_PATH = "registry/lexicon_validation_registry.json"
REPORT_PATH = "registry/reports/lexicon_charter_backfill_report.json"

def backfill():
    if not os.path.exists(CANONICAL_PATH):
        print(f"Error: {CANONICAL_PATH} not found.")
        return

    with open(CANONICAL_PATH, 'r', encoding='utf-8') as f:
        canonical = json.load(f)

    validation_terms = {}
    if os.path.exists(VALIDATION_PATH):
        with open(VALIDATION_PATH, 'r', encoding='utf-8') as f:
            validation = json.load(f)
            validation_terms = validation.get("terms", {})

    total_canonical_terms = 0
    terms_backfilled = 0
    terms_already_compliant = 0
    terms_requiring_manual_review = 0
    framework_label_exemptions = 0

    default_compliance = {
        "charter_version": "2.3",
        "verb_test": "provisional",
        "procedural_fft": "provisional",
        "ontology_residue_check": "provisional",
        "claim_classification": "provisional",
        "data_provenance_status": "not_required",
        "final_compliance_status": "provisional",
        "review_required": True,
        "review_reason": "Canonical term predates charter_compliance schema."
    }

    framework_override = {
        "charter_version": "2.3",
        "verb_test": "provisional",
        "procedural_fft": "provisional",
        "ontology_residue_check": "provisional",
        "claim_classification": "framework_label",
        "data_provenance_status": "not_required",
        "final_compliance_status": "compliant",
        "review_required": True,
        "review_reason": "Canonical term predates charter_compliance schema (Framework Label Exemption)."
    }

    for term_obj in canonical.get("terms", []):
        if term_obj.get("bucket") != "canonical_term":
            continue
        
        total_canonical_terms += 1
        
        if "charter_compliance" in term_obj:
            terms_already_compliant += 1
            continue
        
        term_name = term_obj.get("term")
        is_framework = False
        
        # Check validation registry for status
        v_term = validation_terms.get(term_name, {})
        if v_term.get("ontology_class") == "framework_label" or v_term.get("claim_status") == "FRAMEWORK_LABEL":
            is_framework = True
        elif term_name.endswith("_framework") or term_name == "procedural_continuation_dynamics":
            is_framework = True
        
        if is_framework:
            term_obj["charter_compliance"] = framework_override.copy()
            framework_label_exemptions += 1
        else:
            term_obj["charter_compliance"] = default_compliance.copy()
            terms_backfilled += 1
        
        terms_requiring_manual_review += 1

    # Save canonical
    with open(CANONICAL_PATH, 'w', encoding='utf-8') as f:
        json.dump(canonical, f, indent=2)

    # Emit report
    report = {
        "patch_id": "LEXICON_PATCH_004_BACKFILL_CHARTER_COMPLIANCE_FIELDS",
        "total_canonical_terms": total_canonical_terms,
        "terms_backfilled": terms_backfilled,
        "terms_already_compliant": terms_already_compliant,
        "terms_requiring_manual_review": terms_requiring_manual_review,
        "framework_label_exemptions": framework_label_exemptions
    }
    
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Backfill complete. {terms_backfilled + framework_label_exemptions} terms updated.")
    print(f"Report saved to {REPORT_PATH}")

if __name__ == "__main__":
    backfill()
