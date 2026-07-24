import os
import sys
import json
import sqlite3
import re
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Insert project root into sys.path to allow imports
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.governance.enforce_governance_integrity import check_integrity
from scripts.query_governance import build_db_snapshot_freshness_result


def get_current_commit(root):
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN"


def run_gov_001_authority_audit(root, results):
    """GOV-001: Authority Audit (Verify SSOT ownership and canonical authority)"""
    module_results = {"status": "PASS", "errors": [], "warnings": []}
    
    gemini_path = root / "GEMINI.md"
    agents_path = root / "AGENTS.md"
    
    if not gemini_path.exists():
        module_results["status"] = "FAIL"
        module_results["errors"].append("SSOT Error: GEMINI.md does not exist.")
    else:
        content = gemini_path.read_text(encoding="utf-8")
        if "Role" not in content or "Prime Directive" not in content:
            module_results["status"] = "FAIL"
            module_results["errors"].append("SSOT Error: GEMINI.md is missing Role or Prime Directive declarations.")
            
    if not agents_path.exists():
        module_results["status"] = "FAIL"
        module_results["errors"].append("SSOT Error: AGENTS.md does not exist.")
    else:
        content = agents_path.read_text(encoding="utf-8")
        if "Role" not in content or "Prime Directive" not in content:
            module_results["status"] = "FAIL"
            module_results["errors"].append("SSOT Error: AGENTS.md is missing Role or Prime Directive declarations.")
            
    results["GOV-001"] = module_results
    return module_results["status"] == "PASS"


def run_gov_002_registry_audit(root, results):
    """GOV-002: Registry Audit (Verify canonical registries are internally consistent)"""
    module_results = {"status": "PASS", "errors": [], "warnings": []}
    
    manifest_path = root / "registry/governance_manifest.json"
    lexicon_val_path = root / "registry/lexicon_validation_registry.json"
    gap_queue_path = root / "registry/lexicon_gap_queue.json"
    
    # 1. Existence and Parse checks
    for path, name in [
        (manifest_path, "Unified Manifest"),
        (lexicon_val_path, "Lexicon Registry"),
        (gap_queue_path, "Gap Queue")
    ]:
        if not path.exists():
            module_results["status"] = "FAIL"
            module_results["errors"].append(f"Registry Error: {name} file missing.")
            continue
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                json.load(f)
        except Exception as e:
            module_results["status"] = "FAIL"
            module_results["errors"].append(f"Registry Error: Failed to parse {name}: {e}")
            
    # 2. Node/Edge consistency check if parsed successfully
    if module_results["status"] == "PASS":
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            nodes = manifest.get("nodes", {})
            edges = manifest.get("edges", [])
            
            for nid, node in nodes.items():
                if not node.get("type"):
                    module_results["status"] = "FAIL"
                    module_results["errors"].append(f"Manifest Error: Node '{nid}' missing type.")
                    
            for edge in edges:
                src = edge.get("source")
                tgt = edge.get("target")
                if src not in nodes and "results/" not in src and "docs/" not in src:
                    module_results["status"] = "FAIL"
                    module_results["errors"].append(f"Manifest Error: Edge source '{src}' not found in nodes.")
        except Exception as e:
            module_results["status"] = "FAIL"
            module_results["errors"].append(f"Manifest Consistency Exception: {e}")

    results["GOV-002"] = module_results
    return module_results["status"] == "PASS"


def run_gov_003_governance_integrity_audit(root, results):
    """GOV-003: Governance Integrity Audit (Verify protected assets against integrity records)"""
    module_results = {"status": "PASS", "errors": [], "warnings": []}
    
    try:
        res = check_integrity(root)
        if res["status"] != "success":
            module_results["status"] = "FAIL"
            module_results["errors"].extend(res["errors"])
        module_results["warnings"].extend(res["warnings"])
    except Exception as e:
        module_results["status"] = "FAIL"
        module_results["errors"].append(f"Governance Integrity Exception: {e}")
        
    results["GOV-003"] = module_results
    return module_results["status"] == "PASS"


def run_gov_004_database_freshness_audit(root, results):
    """GOV-004: Database Freshness Audit (Verify repository indexing and snapshot freshness)"""
    module_results = {"status": "PASS", "errors": [], "warnings": []}
    
    db_path = root / "registry/db/acellorator_index.sqlite"
    if not db_path.exists():
        module_results["status"] = "FAIL"
        module_results["errors"].append("Database Error: SQLite database is missing.")
        results["GOV-004"] = module_results
        return False
        
    try:
        # Check SQLite connectivity
        conn = sqlite3.connect(str(db_path))
        conn.close()
        
        # Check freshness using the query governance utility
        fresh_res = build_db_snapshot_freshness_result(str(db_path))
        status = fresh_res.get("db_snapshot_status")
        
        if status == "stale":
            module_results["status"] = "WARNING"
            module_results["warnings"].append(f"Database Warning: snapshot is stale. {fresh_res.get('reason')}")
        elif status != "fresh":
            module_results["status"] = "FAIL"
            module_results["errors"].append(f"Database Error: snapshot is in '{status}' status. {fresh_res.get('reason')}")
    except Exception as e:
        module_results["status"] = "FAIL"
        module_results["errors"].append(f"Database Freshness Exception: {e}")
        
    results["GOV-004"] = module_results
    return module_results["status"] in ["PASS", "WARNING"]


def run_gov_005_executable_evidence_audit(root, results):
    """GOV-005: Executable Evidence Audit (Verify executable evidence exists for governed claims)"""
    module_results = {"status": "PASS", "errors": [], "warnings": []}
    
    claim_reg_path = root / "registry/claim_registry.json"
    if claim_reg_path.exists():
        try:
            with open(claim_reg_path, "r", encoding="utf-8") as f:
                claim_data = json.load(f)
            claims = claim_data.get("claims", [])
            missing_evidence = []
            
            for claim in claims:
                evidence_list = claim.get("evidence", [])
                for evidence in evidence_list:
                    path_str = evidence.get("path") or evidence.get("diff_report")
                    if path_str:
                        path = root / path_str
                        if not path.exists():
                            missing_evidence.append(path_str)
                            
            if missing_evidence:
                module_results["status"] = "WARNING"
                module_results["warnings"].append(
                    f"Evidence Warning: {len(missing_evidence)} referenced evidence files are missing: {', '.join(missing_evidence[:5])}"
                )
        except Exception as e:
            module_results["status"] = "FAIL"
            module_results["errors"].append(f"Executable Evidence Exception: {e}")
    else:
        module_results["status"] = "WARNING"
        module_results["warnings"].append("Evidence Warning: Claim registry file is missing.")
        
    results["GOV-005"] = module_results
    return module_results["status"] in ["PASS", "WARNING"]


def run_gov_006_validation_pipeline_audit(root, results):
    """GOV-006: Validation Pipeline Audit (Verify validation tooling executes successfully)"""
    module_results = {"status": "PASS", "errors": [], "warnings": []}
    
    validate_script = root / "scripts/global_validate.py"
    if not validate_script.exists():
        module_results["status"] = "FAIL"
        module_results["errors"].append("Pipeline Error: scripts/global_validate.py does not exist.")
    else:
        # Check imports and syntax by running quick test
        try:
            res = subprocess.run(
                [sys.executable, str(validate_script), "--quick"],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=30
            )
            if res.returncode != 0:
                module_results["status"] = "FAIL"
                module_results["errors"].append(f"Pipeline Error: global_validate quick run failed: {res.stderr}")
        except Exception as e:
            module_results["status"] = "FAIL"
            module_results["errors"].append(f"Pipeline Exception during execution: {e}")
            
    results["GOV-006"] = module_results
    return module_results["status"] == "PASS"


def run_gov_007_workflow_audit(root, results):
    """GOV-007: Workflow Audit (Verify documented governance workflow matches implemented tooling)"""
    module_results = {"status": "PASS", "errors": [], "warnings": []}
    
    required_scripts = [
        "scripts/query_governance.py",
        "scripts/db/snapshot_registries.py",
        "scripts/governance/enforce_governance_integrity.py"
    ]
    
    for s in required_scripts:
        path = root / s
        if not path.exists():
            module_results["status"] = "FAIL"
            module_results["errors"].append(f"Workflow Error: Tooling script '{s}' does not exist.")
            
    results["GOV-007"] = module_results
    return module_results["status"] == "PASS"


def run_gov_008_agent_compliance_audit(root, results):
    """GOV-008: Agent Compliance Audit (Verify agent instructions comply with governance policy)"""
    module_results = {"status": "PASS", "errors": [], "warnings": []}
    
    # Verify compliant references and rules in agent docs
    gemini_path = root / "GEMINI.md"
    if gemini_path.exists():
        try:
            content = gemini_path.read_text(encoding="utf-8")
            if "compliance_charter" not in content.lower() and "compliance" not in content.lower():
                module_results["status"] = "WARNING"
                module_results["warnings"].append("Compliance Warning: GEMINI.md does not reference compliance standards.")
        except Exception as e:
            module_results["status"] = "FAIL"
            module_results["errors"].append(f"Agent Compliance Exception: {e}")
            
    results["GOV-008"] = module_results
    return module_results["status"] in ["PASS", "WARNING"]


def run_gov_009_repository_health_certification(root, results, module_statuses):
    """GOV-009: Repository Health Certification (Issue repository health certificate)"""
    overall_status = "PASS"
    if "FAIL" in module_statuses.values():
        overall_status = "FAIL"
    elif "WARNING" in module_statuses.values():
        overall_status = "WARNING"
        
    cert = {
        "certificate_version": "1.0.0",
        "issued_commit": get_current_commit(root),
        "issued_timestamp": datetime.now(timezone.utc).isoformat(),
        "repository_integrity": module_statuses.get("GOV-001", "FAIL"),
        "governance_integrity": module_statuses.get("GOV-003", "FAIL"),
        "registry_status": module_statuses.get("GOV-002", "FAIL"),
        "database_snapshot_status": module_statuses.get("GOV-004", "FAIL"),
        "validation_status": module_statuses.get("GOV-006", "FAIL"),
        "agent_compliance_status": module_statuses.get("GOV-008", "FAIL"),
        "overall_status": overall_status
    }
    
    cert_path = root / "repository_health_certificate.json"
    try:
        with open(cert_path, "w", encoding="utf-8") as f:
            json.dump(cert, f, indent=2)
        print(f"Issued repository health certificate at {cert_path}")
    except Exception as e:
        print(f"Error: Failed to write health certificate: {e}", file=sys.stderr)
        return "FAIL", cert
        
    return overall_status, cert


def main():
    parser = argparse.ArgumentParser(description="Repository Governance Audit Surface")
    parser.add_argument("--root", default=".", help="Project root directory")
    args = parser.parse_args()
    
    root = Path(args.root).resolve()
    results = {}
    
    # Run GOV-001 through GOV-008
    run_gov_001_authority_audit(root, results)
    run_gov_002_registry_audit(root, results)
    run_gov_003_governance_integrity_audit(root, results)
    run_gov_004_database_freshness_audit(root, results)
    run_gov_005_executable_evidence_audit(root, results)
    run_gov_006_validation_pipeline_audit(root, results)
    run_gov_007_workflow_audit(root, results)
    run_gov_008_agent_compliance_audit(root, results)
    
    # Collect statuses
    module_statuses = {mod: results[mod]["status"] for mod in results}
    
    # Run GOV-009 to certify and generate json
    overall_status, cert = run_gov_009_repository_health_certification(root, results, module_statuses)
    
    report = {
        "overall_status": overall_status,
        "certificate": cert,
        "modules": results
    }
    
    # Save a detailed report in outputs/audits/repository_governance_audit.json
    audit_report_path = root / "outputs/audits/repository_governance_audit.json"
    audit_report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(audit_report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print(f"Repository governance audit completed with overall status: {overall_status}")
    print(f"Detailed audit report saved to {audit_report_path}")
    
    if overall_status == "FAIL":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
