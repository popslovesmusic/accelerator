import json
import argparse
import os
import sqlite3
import datetime
try:
    from scripts.orientation_retrieval import retrieve_artifacts
    from scripts.db.db_health_check import run_db_health_check
    from tools.inference_governance.candidate_builder import build_bounded_candidate_set_v1
    from tools.inference_governance.candidate_policy import get_candidate_policy, hash_candidate_universe
    from tools.inference_governance.request_normalization import hash_json_value, normalize_text
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from scripts.orientation_retrieval import retrieve_artifacts
    from scripts.db.db_health_check import run_db_health_check
    from tools.inference_governance.candidate_builder import build_bounded_candidate_set_v1
    from tools.inference_governance.candidate_policy import get_candidate_policy, hash_candidate_universe
    from tools.inference_governance.request_normalization import hash_json_value, normalize_text

def generate_execution_plan(query, db_path, limit=10):
    # 1. Gather Orientation Context
    normalized_query = normalize_text(query, lowercase=True)
    retrieval = retrieve_artifacts(db_path, normalized_query, limit=limit, explain=True)
    db_health, _ = run_db_health_check(db_path, "registry/db/schema.sql")
    
    plan = {
        "execution_plan": {
            "task_id": f"PLAN-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "query": query,
            "mode": "advisory_plan_only",
            "orientation_context": {
                "current_command_evidence": [],
                "canonical_authority": [],
                "historical_residue": [],
                "supersession_cautions": [],
                "db_health": {
                    "status": db_health["status"],
                    "artifact_count": db_health["row_counts"].get("artifacts", 0)
                },
                "retrieval_warnings": []
            },
            "candidate_actions": [],
            "recommended_sequence": [],
            "stop_conditions": [
                "If action requires un-authorized mutation of SSOT registries.",
                "If tool health check fails for recommended engine.",
                "If current evidence contradicts plan assumptions."
            ],
            "warnings": []
        }
    }

    # Populate orientation context from retrieval
    for res in retrieval["results"]:
        status = res["orientation_status"]
        if status == "current_command_evidence":
            plan["execution_plan"]["orientation_context"]["current_command_evidence"].append(res["path"])
        elif status == "canonical_active":
            plan["execution_plan"]["orientation_context"]["canonical_authority"].append(res["path"])
        elif status in ["historical_residue", "archived", "deprecated"]:
            plan["execution_plan"]["orientation_context"]["historical_residue"].append(res["path"])
        
        if "cautions" in res and res["cautions"]:
            plan["execution_plan"]["orientation_context"]["supersession_cautions"].extend(res["cautions"])

    # 2. Generate Candidate Actions (Advisory)
    candidate_universe = [
        {
            "candidate_id": "ACT-001",
            "canonical_name": "audit",
            "eligibility_status": "ELIGIBLE",
            "authority_status": str(db_health.get("status", "unknown")).strip().upper() or "UNKNOWN",
            "freshness_status": "FRESH",
            "compatibility_status": "AVAILABLE",
            "rank_score": 1.0,
            "rank_components": {
                "query": normalized_query,
                "reason": "always_available",
            },
            "provenance": {
                "query": normalized_query,
                "retrieval_count": len(retrieval.get("results", [])),
            },
            "policy_rule_id": "execution_plan_always_audit",
        },
        {
            "candidate_id": "ACT-002",
            "canonical_name": "validation",
            "eligibility_status": "ELIGIBLE" if ("dynamics" in normalized_query or "sim" in normalized_query) else "OUT_OF_SCOPE",
            "authority_status": str(db_health.get("status", "unknown")).strip().upper() or "UNKNOWN",
            "freshness_status": "FRESH" if db_health.get("status") == "pass" else "UNKNOWN",
            "compatibility_status": "AVAILABLE" if ("dynamics" in normalized_query or "sim" in normalized_query) else "OUT_OF_SCOPE",
            "rank_score": 0.9,
            "rank_components": {
                "query": normalized_query,
                "reason": "keyword_validation_trigger",
            },
            "provenance": {
                "query": normalized_query,
                "retrieval_count": len(retrieval.get("results", [])),
            },
            "policy_rule_id": "execution_plan_validation_trigger",
        },
    ]
    candidate_policy = get_candidate_policy("execution_plan_action_candidates_v1")
    candidate_set = build_bounded_candidate_set_v1(
        candidate_type="ACTION",
        candidate_policy=candidate_policy,
        universe_candidates=candidate_universe,
        authority_hash=hash_json_value({
            "db_health_status": db_health.get("status"),
            "artifact_count": db_health.get("row_counts", {}).get("artifacts", 0),
        }),
        freshness_hash=hash_json_value({
            "retrieval_query": normalized_query,
            "retrieval_count": len(retrieval.get("results", [])),
        }),
        universe_hash=hash_candidate_universe(
            candidate_universe,
            candidate_type="ACTION",
            candidate_policy_id="execution_plan_action_candidates_v1",
            policy_version=str(candidate_policy.get("policy_version") or "1.0.0"),
        ),
        operation_code="execution_plan",
        candidate_policy_id="execution_plan_action_candidates_v1",
        candidate_policy_version=str(candidate_policy.get("policy_version") or "1.0.0"),
    )
    plan["execution_plan"]["candidate_actions"] = [
        {
            "action_id": candidate["candidate_id"],
            "action_type": candidate["canonical_name"],
            "description": (
                f"Perform a structural audit for query: {normalized_query}"
                if candidate["candidate_id"] == "ACT-001"
                else "Run tool health and rigor endorsement check for associated engines."
            ),
            "recommended_agent": "Codex",
            "risk_level": "low" if candidate["candidate_id"] == "ACT-001" else "medium",
            "claim_impact": "none" if candidate["candidate_id"] == "ACT-001" else "provisional_context",
            "candidate_provenance": candidate.get("provenance", {}),
        }
        for candidate in candidate_set.get("eligible_candidates", [])
    ]
    plan["execution_plan"]["candidate_set"] = candidate_set
    plan["execution_plan"]["candidate_set_hash"] = candidate_set.get("candidate_set_hash")
    plan["execution_plan"]["candidate_policy_id"] = candidate_set.get("candidate_policy_id")
    plan["execution_plan"]["candidate_exclusions"] = candidate_set.get("excluded_candidates", [])

    # Recommended sequence
    plan["execution_plan"]["recommended_sequence"] = [action["action_id"] for action in plan["execution_plan"]["candidate_actions"]]
    plan["execution_plan"]["normalized_query"] = normalized_query

    print(json.dumps(plan, indent=2))
    return plan

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate advisory execution plans.")
    parser.add_argument("--query", required=True, help="Topic for the execution plan.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=10, help="Limit retrieval results.")
    
    args = parser.parse_args()
    generate_execution_plan(args.query, args.db, args.limit)
