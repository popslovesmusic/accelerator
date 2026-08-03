import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load_json(relative):
    path = ROOT / relative
    return path, json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def result(packet_id, checks, evidence_paths, limitations):
    failed = [c for c in checks if not c["passed"]]
    return {
        "packet_id": packet_id,
        "status": "PASS_BOUNDED_STRUCTURAL_VALIDATION" if not failed else "FAIL_BOUNDED_STRUCTURAL_VALIDATION",
        "checks": checks,
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "evidence_paths": evidence_paths,
        "limitations": limitations,
        "claim_ceiling": "C1",
    }


def check(name, passed, detail):
    return {"name": name, "passed": bool(passed), "detail": detail}


def validate_056():
    source_path, source = load_json("departments/analysis_intake/chat_captures/RT_ASYM_OBSERVATION_ORIENTATION_EXCLUSION_INDUCTION_20260728_001.json")
    formal = source.get("provisional_formalization", {})
    sequence = source.get("conceptual_sequence", [])
    checks = [
        check("source_capture_valid", source.get("capture_type") == "CHAT_SEMANTIC_CAPTURE", source.get("capture_type")),
        check("claim_ceiling_c1", source.get("claim_ceiling") == "C1_MODEL_RELATIVE", source.get("claim_ceiling")),
        check("six_step_sequence", len(sequence) == 6 and [x.get("ordinal") for x in sequence] == list(range(1, 7)), len(sequence)),
        check("formalization_keys_present", all(k in formal for k in ("orientation_space", "orientation_exclusion", "reference_orientation", "asym_condition", "bounded_projection", "expanded_chain")), sorted(formal)),
        check("interpretive_constraints_present", len(source.get("interpretive_constraints", [])) >= 7, len(source.get("interpretive_constraints", []))),
    ]
    return result(source["packet_id"], checks, [str(source_path.relative_to(ROOT))], ["No theorem proof or external physical validation."])


def validate_057():
    source_path, source = load_json("departments/analysis_intake/chat_captures/RT_BOUNDARY_ORIENTATION_ASYM_INDUCTION_20260728_001.json")
    crawl_path, crawl = load_json("departments/analysis/crawl_reports/analysis_crawl_20260728_boundary_orientation_asym_001.json")
    checks = [
        check("source_capture_valid", source.get("capture_type") == "CHAT_SEMANTIC_CAPTURE", source.get("capture_type")),
        check("literal_preservation", source.get("literal_first_contact", {}).get("preservation_status") == "PRESERVED_LITERAL", source.get("literal_first_contact", {}).get("preservation_status")),
        check("c1_model_relative", source.get("epistemic_status", {}).get("claim_ceiling") == "C1_MODEL_RELATIVE", source.get("epistemic_status", {}).get("claim_ceiling")),
        check("boundary_orientation_chain_present", "boundary interaction" in source.get("executive_claim", {}).get("statement", "").lower() and "reference orientation" in source.get("executive_claim", {}).get("statement", "").lower(), source.get("executive_claim", {}).get("compact_form")),
        check("crawl_obligations_identified", any(f.get("proof_status") == "OBLIGATIONS_IDENTIFIED" for f in crawl.get("findings", [])), "crawl findings inspected"),
    ]
    return result(source["packet_id"], checks, [str(source_path.relative_to(ROOT)), str(crawl_path.relative_to(ROOT))], ["Repository comparison is not a theorem proof."])


def validate_059():
    base = ROOT / "departments/analysis/campaigns/RT_MTO_OTM_FINITE_FIXTURE_001"
    names = ["finite_fixture_report.json", "orientation_fixture_report.json", "architectural_decision_fixture_report.json", "independent_cross_validation_report.json", "adversarial_counterexample_report.json", "human_review_packet.json"]
    reports = {name: json.loads((base / name).read_text(encoding="utf-8")) for name in names}
    checks = [
        check("finite_fixture_passed", reports["finite_fixture_report.json"].get("overall_result") == "PASS_BOUNDED_FIXTURES" and reports["finite_fixture_report.json"].get("failed") == 0, reports["finite_fixture_report.json"].get("overall_result")),
        check("orientation_fixture_passed", reports["orientation_fixture_report.json"].get("overall_result") == "PASS_BOUNDED_FIXTURES" and reports["orientation_fixture_report.json"].get("failed") == 0, reports["orientation_fixture_report.json"].get("overall_result")),
        check("architectural_fixture_passed", reports["architectural_decision_fixture_report.json"].get("overall_result") == "PASS_BOUNDED_ARCHITECTURAL_FIXTURES", reports["architectural_decision_fixture_report.json"].get("overall_result")),
        check("independent_cross_validation_passed", reports["independent_cross_validation_report.json"].get("overall_result") == "PASS_CROSS_VALIDATED_FIXTURES" and reports["independent_cross_validation_report.json"].get("failed") == 0, reports["independent_cross_validation_report.json"].get("overall_result")),
        check("counterexamples_preserved", reports["adversarial_counterexample_report.json"].get("overall_result") == "COUNTEREXAMPLES_FOUND_BOUNDARY_REOPENED", reports["adversarial_counterexample_report.json"].get("overall_result")),
        check("human_review_pending", reports["human_review_packet.json"].get("human_decision_required") is True, reports["human_review_packet.json"].get("review_status")),
    ]
    return result("RT_INDUCTION_MTO_OTM_CALCULUS_001", checks, [str((base / n).relative_to(ROOT)) for n in names], ["Fixtures validate the implemented bounded cases, not the general calculus."])


def validate_060():
    source_path, source = load_json("departments/analysis_intake/chat_captures/RT_INDUCTION_RECURSIVE_PATTERN_AND_DOMAIN_LIFT_001.json")
    defs = source.get("definitions", {})
    lift = source.get("domain_lift", {})
    mto = source.get("MTO_OTM", {})
    checks = [
        check("source_capture_valid", source.get("packet_type") == "PROVISIONAL_INDUCTION", source.get("packet_type")),
        check("preservation_declared", source.get("status") == "PRESERVE_LITERAL" and source.get("review_mode") == "NOT_REVIEWED", source.get("status")),
        check("core_definitions_present", all(k in defs for k in ("absolute_primitive", "A_E", "D_A_E", "composition_operator", "RT")), sorted(defs)),
        check("domain_lift_sequence_complete", lift.get("sequence") == ["Primitive_n", "Aspect_n", "RT_n", "Primitive_(n+1)", "Aspect_(n+1)", "RT_(n+1)"], lift.get("sequence")),
        check("mto_otm_roles_present", mto.get("MTO", {}).get("role") and mto.get("OTM", {}).get("role") and len(mto.get("recursion", [])) >= 4, mto.get("recursion")),
        check("domain_termination_declared", mto.get("termination") == "Within a domain, recursion terminates when no further lawful aspects are discoverable.", mto.get("termination")),
        check("orientation_field_declared", "orientation_field" in source and source["orientation_field"].get("field", {}).get("carrier"), source.get("orientation_field", {}).get("field", {}).get("carrier")),
        check("provisional_identity_boundary", source.get("identity_and_type", {}).get("status") == "PROVISIONAL", source.get("identity_and_type", {}).get("status")),
    ]
    return result(source["packet_id"], checks, [str(source_path.relative_to(ROOT))], ["This is a schema/invariant validation of the preserved proposal; it does not validate the proposed calculus against an external model."])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    results = [validate_056(), validate_057(), validate_059(), validate_060()]
    payload = {
        "campaign_id": "INTAKE_VALIDATION_20260803_001",
        "status": "BOUNDED_EVIDENCE_VALIDATION",
        "claim_ceiling": "C1",
        "results": results,
        "interpretation": "PASS means the preserved artifact satisfies declared structural checks; it does not establish mathematical truth, physical validity, or canonical status.",
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out.relative_to(ROOT)), "statuses": {r["packet_id"]: r["status"] for r in results}}, indent=2))


if __name__ == "__main__":
    main()
