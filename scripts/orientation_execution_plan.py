import json
import argparse
import os
import sqlite3
from datetime import datetime
try:
    from scripts.orientation_retrieval import retrieve_artifacts
    from scripts.db.db_health_check import run_db_health_check
except ImportError:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from orientation_retrieval import retrieve_artifacts
    from db.db_health_check import run_db_health_check

def generate_execution_plan(query, db_path, limit=10):
    # 1. Gather Orientation Context
    retrieval = retrieve_artifacts(db_path, query, limit=limit, explain=True)
    db_health, _ = run_db_health_check(db_path, "registry/db/schema.sql")
    
    plan = {
        "execution_plan": {
            "task_id": f"PLAN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
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
    # Action: Audit
    plan["execution_plan"]["candidate_actions"].append({
        "action_id": "ACT-001",
        "action_type": "audit",
        "description": f"Perform a structural audit for query: {query}",
        "recommended_agent": "Codex",
        "risk_level": "low",
        "claim_impact": "none"
    })

    # Action: Validation (if tool matches)
    if "dynamics" in query or "sim" in query:
        plan["execution_plan"]["candidate_actions"].append({
            "action_id": "ACT-002",
            "action_type": "validation",
            "description": "Run tool health and certification check for associated engines.",
            "recommended_agent": "Codex",
            "risk_level": "medium",
            "claim_impact": "provisional_context"
        })

    # Recommended sequence
    plan["execution_plan"]["recommended_sequence"] = ["ACT-001"]
    if len(plan["execution_plan"]["candidate_actions"]) > 1:
        plan["execution_plan"]["recommended_sequence"].append("ACT-002")

    print(json.dumps(plan, indent=2))
    return plan

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate advisory execution plans.")
    parser.add_argument("--query", required=True, help="Topic for the execution plan.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=10, help="Limit retrieval results.")
    
    args = parser.parse_args()
    generate_execution_plan(args.query, args.db, args.limit)
