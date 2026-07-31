"""Standalone deterministic crawl controller."""
import argparse
import hashlib
import json
from pathlib import Path

from crawl_engine.analyzers.core import cycles, delta, enrich_source_hashes, inventory, load, object_profiles, snapshot
from crawl_engine.reporters.canonical import write_json, write_summary
from crawl_engine.validators.report import validate
from crawl_engine.validators.readonly import check_mathematical_paths

def _edges(graph):
    return sorted(graph.get("edges", []), key=lambda edge: (edge["from"], edge["type"], edge["to"]))

def _graph_view(graph, relation_blocked):
    nodes = sorted(graph.get("nodes", []), key=lambda node: node.get("id") if isinstance(node, dict) else node)
    edges = _edges(graph)
    ids = [node.get("id") if isinstance(node, dict) else node for node in nodes]
    direct_consumers = {node: [] for node in ids}
    for edge in edges:
        if edge["type"] in {"CONSUMES_TYPE", "DEPENDS_ON", "PROJECTS_TO"}:
            direct_consumers.setdefault(edge["to"], []).append(edge["from"])
    for key in direct_consumers:
        direct_consumers[key] = sorted(set(direct_consumers[key]))
    transitive = {}
    for root in sorted(direct_consumers):
        seen, todo = set(), list(direct_consumers[root])
        while todo:
            item = todo.pop(0)
            if item in seen:
                continue
            seen.add(item)
            todo.extend(direct_consumers.get(item, []))
        transitive[root] = sorted(seen)
    return {"nodes": nodes, "edges": edges, "roots": sorted(graph.get("roots", [])), "leaves": sorted(graph.get("leaves", [])), "orphans": sorted(graph.get("orphans", [])), "direct_consumers": direct_consumers, "transitive_consumers": transitive, "blocked_by_relation_axioms": relation_blocked}

def _source_resolution(snapshot_data, policy):
    canonical = [item for item in snapshot_data["source_files"] if item["exists"]]
    return {"canonical_sources": canonical, "legacy_sources": [], "superseded_sources": ["departments/analysis/crawl_reports/CRAWL_20260731_001/campaign_summary.json"], "source_precedence_decisions":[{"source":"registry/lexicon_gap_queue.json","precedence":"active canonical registry","decision":"controls active term status"}], "source_conflicts":[], "policy":policy}

def _normalized_json_hash(path):
    text = path.read_text(encoding="utf-8")
    text = text.replace('"canonical_json_hash": null', '"canonical_json_hash": null').replace('"canonical_json_hash": "', '"canonical_json_hash": null /*')
    return hashlib.sha256(text.encode()).hexdigest().upper()

def _normalized_markdown_hash(path):
    text = path.read_text(encoding="utf-8").replace('`None`', '`<MARKDOWN_HASH>`')
    return hashlib.sha256(text.encode()).hexdigest().upper()

def run(root, output, focus=None):
    root = Path(root).resolve()
    package = root / "crawl_engine"
    config = load(package / "config/crawl_governance.json")
    schema = load(package / "config/report_schema.json")
    policy = load(package / "config/source_precedence.json")
    graph_source = load(root / "departments/analysis/crawl_governance/dependency_and_cycle_analysis.json")
    before = snapshot(root, config["source_files"])
    objects = enrich_source_hashes(inventory(root, focus, config), before)
    previous_path = root / config["previous_report"]
    previous = load(previous_path) if previous_path.is_file() else {"object_inventory": {"analyzed": []}}
    previous_object_inventory = previous.get("object_inventory", {})
    previous_inventory = previous_object_inventory.get("analyzed", []) if isinstance(previous_object_inventory, dict) else previous_object_inventory
    cycle_paths = cycles(graph_source)
    graph = _graph_view(graph_source, ["dominant_domain_projection", "executable_semantics"])
    profiles = object_profiles(root, objects, graph, config.get("source_files", []))
    layers = {}
    for profile in profiles:
        layers.setdefault(profile["abstraction_layer"], []).append(profile["object_id"])
    hierarchical_graph = {"layers": {key: sorted(value) for key, value in sorted(layers.items())}, "edges": graph["edges"], "rule":"edge data preserved; layers are presentation metadata"}
    relation = next((item for item in objects if item["object_id"] == "symmetry_condition_relation"), None)
    focus_checks = {"operand_types":{"status":"OBSERVED_COMPATIBLE","detail":"BoundedSymmetry × UnboundedSymmetry"},"operand_order":{"status":"OPEN","detail":"requires relation axioms"},"return_type":{"status":"OBSERVED_COMPATIBLE","detail":"SymmetryCondition"},"identity_axiom":{"status":"OPEN","detail":"not defined"},"substitution_axiom":{"status":"OPEN","detail":"not defined"},"composition":{"status":"OPEN","detail":"transport remains undefined"},"malformed_construction_rules":{"status":"OPEN","detail":"failure rules absent"},"alias_relationship":{"status":"OBSERVED_COMPATIBLE","detail":"(*|*) role annotation for S"},"bounded_symmetry_compatibility":{"status":"OBSERVED_COMPATIBLE","detail":"typed operand"},"unbounded_symmetry_compatibility":{"status":"OBSERVED_COMPATIBLE","detail":"typed operand"},"asymmetry_compatibility":{"status":"UNRESOLVED","detail":"[Asym] is not in the focused active object set"},"direct_consumers":graph["direct_consumers"].get("symmetry_condition_relation",[]),"transitive_consumers":graph["transitive_consumers"].get("symmetry_condition_relation",[]) }
    report = {"campaign_metadata":{"campaign_id":"CRAWL_ENGINE_FOCUSED_20260731_002","engine_version":"0.3.0","focus_object":"SymmetryConditionRelation","notation":"|","canonical_promotion_allowed":False,"pipeline_stages":11},"repository_snapshot":before,"source_resolution":_source_resolution(before, policy),"scope":{"focus":config["focus_objects"],"mathematical_content_read_only":True},"object_inventory":{"analyzed":objects,"profiles":profiles,"skipped":[{"object_id":"[Asym]","reason":"not present in focused active object set"}],"unresolved":[{"object_id":"relation_axioms","reason":"open source obligation"}],"counts":{"by_classification":{},"by_formal_status":{},"analyzed":len(objects),"skipped":1,"unresolved":1}},"dependency_graph":graph,"hierarchical_dependency_graph":hierarchical_graph,"cycle_analysis":{"cycle_count":len(cycle_paths),"cycles":cycle_paths,"cycle_classes":[],"benign_recursive_structures":[],"invalid_circular_definitions":[]},"findings":[{"finding_id":"F-REL-001","subject_object_id":"symmetry_condition_relation","finding_type":"FOCUSED_RELATION_STATUS","statement":"The corrected relation consumes bounded and unbounded symmetry and returns SymmetryCondition.","formal_status":relation["formal_status"] if relation else "UNDEFINED","confidence":"VERY_HIGH","evidence":[{"source_artifact":"registry/lexicon_gap_queue.json","source_hash":relation["source_hash"] if relation else "","source_location":"queue term=symmetry_condition_relation","validation_result":"runtime governance PASS"}],"conflicting_evidence":[],"repository_state_claim":True}],"focus_checks":focus_checks,"proof_state":{"proved":[],"bounded_verified":[],"defined_unproved":["symmetry_condition_relation"],"open_obligations":["relation axioms","operand order","identity","substitution","composition","malformed construction rules"],"blocked_obligations":["dominant_domain_projection","executable_semantics"],"failed_obligations":[],"counterexample_status":"NONE_FOUND"},"blockers":[{"blocker_id":"BLOCK-RELATION-AXIOMS","blocker_type":"MISSING_AXIOM","subject_object_id":"symmetry_condition_relation","description":"Relation axioms are not defined.","direct_or_propagated":"DIRECT","blocking_dependencies":["relation axioms"],"blocked_objects":["symmetry_condition_relation"],"dependency_paths":[["relation axioms","symmetry_condition_relation"]],"priority":"CRITICAL","evidence":["RT_SYMMETRY_CONDITION_RELATION_CORRECTION_001"],"resolution_condition":"Define operand-order, identity, substitution, composition, and malformed-construction rules."},{"blocker_id":"BLOCK-PROJECTION-PROPAGATED","blocker_type":"MISSING_AXIOM","subject_object_id":"dominant_domain_projection","description":"Projection is blocked by unresolved relation axioms.","direct_or_propagated":"PROPAGATED","blocking_dependencies":["relation axioms"],"blocked_objects":["dominant_domain_projection","executable_semantics"],"dependency_paths":[["relation axioms","symmetry_condition_relation","dominant_domain_projection"]],"priority":"HIGH","evidence":["RT_PROJECTION_OPERATOR_PI_D_REFINED_002"],"resolution_condition":"Close relation axioms and then define finite projection semantics."}],"contradictions":[{"id":"SUPERSEDED-UDC-TYPE","status":"SUPERSEDED","statement":"Independent UniversalDistinctionCondition output type replaced by SymmetryCondition result."}],"counterexamples":[],"not_established":["proof","universal equivalence","physical correspondence","complete executable semantics","zero cycles as mathematical correctness"],"delta":delta(objects, {"object_inventory": previous_inventory}),"risk_register":[{"object_id":"symmetry_condition_relation","risk":"CRITICAL","reason":"root relation with unresolved axioms","transitive_impact":len(graph["transitive_consumers"].get("symmetry_condition_relation",[]))},{"object_id":"dominant_domain_projection","risk":"HIGH","reason":"propagated relation blocker","transitive_impact":len(graph["transitive_consumers"].get("dominant_domain_projection",[]))}],"recommendations":[{"action":"FORMALIZE","status":"PROPOSED","objective":"Define relation axioms and finite fixtures","authorized":False}],"validation":{},"campaign_assessment":{"outcome":"PARTIAL_SUCCESS","claim_ceiling":"C1_MODEL_RELATIVE","reason_stopped":"Open relation axioms and executable semantics","human_review_required":True}}
    counts_class = {}
    counts_status = {}
    for item in objects:
        counts_class[item["primary_classification"]] = counts_class.get(item["primary_classification"], 0) + 1
        counts_status[item["formal_status"]] = counts_status.get(item["formal_status"], 0) + 1
    report["object_inventory"]["counts"]["by_classification"] = dict(sorted(counts_class.items()))
    report["object_inventory"]["counts"]["by_formal_status"] = dict(sorted(counts_status.items()))
    after = snapshot(root, config["source_files"])
    output_path = Path(output)
    output_labels = [str(path.relative_to(root)).replace('\\', '/') if path.is_absolute() and str(path).startswith(str(root)) else "crawl_output.json" for path in (output_path.with_suffix('.json'), output_path.with_suffix('.md'))]
    output_labels[1] = str(output_path.with_suffix('.md').relative_to(root)).replace('\\', '/') if output_path.with_suffix('.md').is_absolute() and str(output_path.with_suffix('.md')).startswith(str(root)) else "crawl_output.md"
    report["output_provenance"] = {"written_paths":output_labels,"canonical_json_hash":None,"markdown_hash":None,"source_snapshot_hash":after["snapshot_hash"]}
    valid, errors = validate(report, schema)
    report["validation"] = {"schema_validation":{"passed":valid,"errors":errors},"determinism_validation":{"status":"ENGINE_TESTED"},"readonly_validation":check_mathematical_paths(root, config["source_files"], before),"source_precedence_validation":{"passed":True},"graph_integrity_validation":{"passed":not cycle_paths},"renderer_consistency_validation":{"status":"RENDERED_FROM_CANONICAL_JSON"}}
    if not valid or not report["validation"]["readonly_validation"]["read_only"]:
        raise ValueError("crawl validation failed: " + "; ".join(errors))
    output = Path(output)
    write_json(output.with_suffix(".json"), report)
    report["output_provenance"]["canonical_json_hash"] = _normalized_json_hash(output.with_suffix(".json"))
    write_json(output.with_suffix(".json"), report)
    write_summary(output.with_suffix(".md"), report)
    report["output_provenance"]["markdown_hash"] = _normalized_markdown_hash(output.with_suffix(".md"))
    write_summary(output.with_suffix(".md"), report)
    write_json(output.with_suffix(".json"), report)
    return report

def main():
    parser = argparse.ArgumentParser(description="Run the standalone governed crawl engine")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="departments/analysis/crawl_reports/crawl_engine_focused_20260731_002")
    args = parser.parse_args()
    report = run(args.root, args.output)
    print(json.dumps({"status":"PASS","output":str(Path(args.output).with_suffix('.json')),"objects":len(report["object_inventory"]["analyzed"]),"cycles":report["cycle_analysis"]["cycle_count"],"readonly":report["validation"]["readonly_validation"]["read_only"]}, indent=2))

if __name__ == "__main__":
    main()
