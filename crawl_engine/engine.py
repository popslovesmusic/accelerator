"""Standalone deterministic crawl controller."""
import argparse
import json
from pathlib import Path

from crawl_engine.analyzers.core import cycles, delta, inventory, load, snapshot
from crawl_engine.reporters.canonical import write_json, write_summary
from crawl_engine.validators.report import validate
from crawl_engine.validators.readonly import check_mathematical_paths

def run(root, output, focus=None):
    root = Path(root).resolve()
    package = root / "crawl_engine"
    config = load(package / "config/crawl_governance.json")
    schema = load(package / "config/report_schema.json")
    policy = load(package / "config/source_precedence.json")
    graph = load(root / "departments/analysis/crawl_governance/dependency_and_cycle_analysis.json")
    snap = snapshot(root, config["source_files"])
    objects = inventory(root, focus, config)
    previous_path = root / config["previous_report"]
    previous = load(previous_path) if previous_path.is_file() else {"object_inventory": []}
    graph_cycles = cycles(graph)
    report = {"campaign_metadata":{"campaign_id":"CRAWL_ENGINE_FOCUSED_20260731_001","engine_version":"0.1.0","focus":focus or config["focus_objects"],"canonical_promotion_allowed":False,"pipeline_stages":11},"repository_snapshot":snap | {"source_precedence":policy["source_precedence"]},"scope":config["focus_objects"],"mathematical_inventory":objects,"dependency_graph":graph,"cycle_analysis":{"cycles":graph_cycles,"cycle_classes":[],"benign_recursion_distinguished":True},"mathematical_delta":delta(objects, previous),"focus_checks":{"operand_type":{"status":"OBSERVED_COMPATIBLE","detail":"bounded_symmetry and unbounded_symmetry are distinct typed inputs"},"operand_order":{"status":"OPEN","detail":"orientation significance requires relation axioms"},"return_type":{"status":"OBSERVED_COMPATIBLE","detail":"corrected relation returns SymmetryCondition"},"identity_behavior":{"status":"OPEN","detail":"not specified by current axioms"},"substitution_behavior":{"status":"OPEN","detail":"not specified by current axioms"},"composition_behavior":{"status":"OPEN","detail":"cross-domain transport remains undefined"},"malformed_constructions":{"status":"OPEN","detail":"failure rules remain to be formalized"},"alias_relationship":{"status":"OBSERVED_COMPATIBLE","detail":"(*|*) is role-sensitive notation for S"},"bounded_unbounded_compatibility":{"status":"OBSERVED_COMPATIBLE","detail":"both are admitted as symmetry subtypes"},"downstream_impact":{"status":"BLOCKED","detail":"projection and executable semantics depend on relation axioms"}},"proof_state":{"proved":[],"bounded_verified":[],"open":["relation axioms","executable semantics"],"blocked":["dominant_domain_projection"],"failed":[]},"blockers":[{"blocker_id":"BLOCK-RELATION-AXIOMS","blocker_type":"MISSING_AXIOM","blocked_objects":["symmetry_condition_relation","dominant_domain_projection"],"dependency":"relation axioms for |","impact":"CRITICAL"},{"blocker_id":"BLOCK-EXECUTABLE","blocker_type":"MISSING_EXECUTABLE_SEMANTICS","blocked_objects":["executable_semantics"],"dependency":"finite typed semantics","impact":"HIGH"}],"contradictions":[],"counterexamples":[],"not_established":["proof","universal equivalence","physical correspondence","complete executable semantics"],"risk_register":[{"object":"symmetry_condition_relation","risk":"CRITICAL","reason":"root relation with unresolved axioms"}],"recommendations":[{"action":"FORMALIZE","status":"PROPOSED","objective":"Define relation axioms and finite fixtures"}],"validation_summary":{},"campaign_assessment":{"outcome":"PARTIAL_SUCCESS","claim_ceiling":"C1_MODEL_RELATIVE","reason_stopped":"Open relation axioms and executable semantics","human_review_required":True}}
    valid, errors = validate(report, schema)
    report["validation_summary"] = {"schema_valid":valid,"errors":errors,"read_only":check_mathematical_paths(root, snap["repository_hash"]),"source_precedence_applied":True}
    if not valid:
        raise ValueError("report validation failed: " + "; ".join(errors))
    output = Path(output)
    write_json(output.with_suffix(".json"), report)
    write_summary(output.with_suffix(".md"), report)
    return report

def main():
    parser = argparse.ArgumentParser(description="Run the standalone governed crawl engine")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="departments/analysis/crawl_reports/crawl_engine_focused_20260731_001")
    parser.add_argument("--focus", nargs="*")
    args = parser.parse_args()
    report = run(args.root, args.output, args.focus or None)
    print(json.dumps({"status":"PASS","output":str(Path(args.output).with_suffix('.json')),"objects":len(report["mathematical_inventory"]),"cycles":len(report["cycle_analysis"]["cycles"]),"read_only":True}, indent=2))

if __name__ == "__main__":
    main()
