"""Validate refined deterministic crawl configuration and report structure."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "departments/analysis/crawl_governance/refined_crawl_governance_configuration.json"
SCHEMA = ROOT / "departments/analysis/crawl_governance/refined_crawl_report_schema.json"
REPORT = ROOT / "departments/analysis/crawl_reports/analysis_crawl_20260731_symmetry_relation_refined_001.json"
GRAPH = ROOT / "departments/analysis/crawl_governance/dependency_and_cycle_analysis.json"

def load(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)

def main():
    config, schema, report, graph = map(load, (CONFIG, SCHEMA, REPORT, GRAPH))
    required = schema["required"]
    missing = [key for key in required if key not in report]
    if missing:
        raise SystemExit("missing report sections: " + ", ".join(missing))
    allowed_classes = set(config["required_classifications"])
    allowed_statuses = set(config["required_statuses"])
    for obj in report["object_inventory"]:
        if obj["primary_classification"] not in allowed_classes:
            raise SystemExit("invalid classification: " + obj["primary_classification"])
        if obj["formal_status"] not in allowed_statuses:
            raise SystemExit("invalid formal status: " + obj["formal_status"])
    allowed_edges = set(config["required_edge_types"])
    for edge in graph["edges"]:
        if edge["type"] not in allowed_edges:
            raise SystemExit("invalid edge type: " + edge["type"])
    if graph["cycles"]:
        raise SystemExit("unexpected cycle output in bounded current graph")
    if report["campaign_assessment"]["canonical_promotion_allowed"]:
        raise SystemExit("crawl cannot authorize promotion")
    print(json.dumps({"status":"PASS","objects":len(report["object_inventory"]),"edges":len(graph["edges"]),"cycles":len(graph["cycles"]),"canonical_promotion_allowed":False}, indent=2))

if __name__ == "__main__":
    main()
