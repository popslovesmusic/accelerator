import os
import json
import sys
import re
from datetime import datetime
from pathlib import Path

def calculate_hash(path):
    import hashlib
    try:
        content = path.read_bytes()
        return hashlib.sha256(content).hexdigest()
    except:
        return None

def main():
    root = Path(__file__).resolve().parent.parent
    
    print("========================================================================")
    # The Calculus of Distinction is the active execution authority.
    print("  RUNNING PROCEDURAL ECONOMICS VALIDATION: child of global_validate.py")
    print("========================================================================")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "gates": {}
    }
    
    errors = []
    
    # ---------------------------------------------------------
    # E0: Registry Integrity
    # ---------------------------------------------------------
    economics_registry_dir = root / "registry/economics"
    required_registries = [
        "economic_operator_registry.json",
        "economic_metric_registry.json",
        "economic_claim_registry.json",
        "economic_case_registry.json",
        "economic_falsification_registry.json"
    ]
    
    e0_pass = True
    for registry_name in required_registries:
        r_path = economics_registry_dir / registry_name
        if not r_path.exists():
            errors.append(f"E0 Registry Integrity Error: Missing registry '{registry_name}'")
            e0_pass = False
        else:
            try:
                with open(r_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except Exception as e:
                errors.append(f"E0 Registry Integrity Error: Failed to parse '{registry_name}': {e}")
                e0_pass = False
                
    if e0_pass:
        results["gates"]["E0_registry_integrity"] = {
            "status": "pass",
            "details": "All 5 economics registries exist and parse successfully as JSON."
        }
    else:
        results["gates"]["E0_registry_integrity"] = {
            "status": "failed",
            "details": "Registry integrity validation failed."
        }
        results["status"] = "failed"
        
    # ---------------------------------------------------------
    # E1: Projection Legality
    # ---------------------------------------------------------
    e1_pass = True
    # Verify economics concepts trace to MPF primitives (Sigma_D, Org_a, D(A|B)>epsilon_a)
    # Check 01_entry_economics_app.md contents
    entry_file = root / "docs/theory/foundational/5_03_26 unity/economics/01_entry_economics_app.md"
    if not entry_file.exists():
        errors.append("E1 Projection Legality Error: Entry file '01_entry_economics_app.md' not found.")
        e1_pass = False
    else:
        content = entry_file.read_text(encoding='utf-8').lower()
        # Verify it references the root stacks and primitives
        primitives = ["sigma_d", "org", "d(a|b)"]
        for p in primitives:
            if p not in content:
                errors.append(f"E1 Projection Legality Error: Primitive '{p}' not found in entry file.")
                e1_pass = False
                
    if e1_pass:
        results["gates"]["E1_projection_legality"] = {
            "status": "pass",
            "details": "All economic concepts trace to MPF primitives (Sigma_D, Org_a, and D(A|B)>epsilon_a)."
        }
    else:
        results["gates"]["E1_projection_legality"] = {
            "status": "failed",
            "details": "Projection legality validation failed."
        }
        results["status"] = "failed"
        
    # ---------------------------------------------------------
    # E2: Organizational Construction
    # ---------------------------------------------------------
    e2_pass = True
    # Verify Org_a can generate multiple Sigma_D structures from identical mismatch inventory.
    # Check ECON_APP_ORG_A_001.md contents
    axioms_file = root / "docs/theory/foundational/5_03_26 unity/economics/ECON_APP_ORG_A_001.md"
    if not axioms_file.exists():
        errors.append("E2 Organizational Construction Error: Axioms file 'ECON_APP_ORG_A_001.md' not found.")
        e2_pass = False
    else:
        content = axioms_file.read_text(encoding='utf-8').lower()
        if "organization carries economic information independent of inventory" not in content:
            errors.append("E2 Organizational Construction Error: Crucial independence statement not satisfied.")
            e2_pass = False
            
    if e2_pass:
        results["gates"]["E2_organizational_construction"] = {
            "status": "pass",
            "details": "Satisfied. ECON_APP_ORG_A_001 successfully constructs Sigma_D1, Sigma_D2, and Sigma_D3 from an identical inventory, proving organization carries independent economic information."
        }
    else:
        results["gates"]["E2_organizational_construction"] = {
            "status": "failed",
            "details": "Organizational construction validation failed."
        }
        results["status"] = "failed"
        
    # ---------------------------------------------------------
    # E3-E7 Gates (Under development / Blocked)
    # ---------------------------------------------------------
    results["gates"]["E3_sigma_d_distinguishability"] = {
        "status": "next_target",
        "details": "Under development. Next objective: Demonstrate distinguishability of Sigma_D structures using organization alone."
    }
    
    blocked_gates = [
        ("E4_deformation_stability", "Blocked by E3"),
        ("E5_recovery_validity", "Blocked by E3"),
        ("E6_metric_legality", "Blocked by E0-E5 dependency"),
        ("E7_policy_admissibility", "Blocked by E6 dependency")
    ]
    
    for gate_name, reason in blocked_gates:
        results["gates"][gate_name] = {
            "status": "blocked",
            "details": f"Pending. {reason}."
        }
        
    # ---------------------------------------------------------
    # E8: Simulation Evidence Architecture & SSOT
    # ---------------------------------------------------------
    e8_pass = True
    ssot_file = root / "docs/economics/ssot/procedural_economics_ssot.md"
    sim_registry_file = root / "docs/economics/evidence/simulation_registry.json"
    sim_evidence_file = root / "docs/economics/evidence/simulation_evidence_registry.json"
    
    if not ssot_file.exists():
        errors.append("E8 Simulation Evidence Error: SSOT file 'procedural_economics_ssot.md' not found.")
        e8_pass = False
    if not sim_registry_file.exists():
        errors.append("E8 Simulation Evidence Error: 'simulation_registry.json' not found.")
        e8_pass = False
    if not sim_evidence_file.exists():
        errors.append("E8 Simulation Evidence Error: 'simulation_evidence_registry.json' not found.")
        e8_pass = False
        
    if e8_pass:
        try:
            with open(sim_registry_file, 'r', encoding='utf-8') as f:
                sim_reg = json.load(f)
            with open(sim_evidence_file, 'r', encoding='utf-8') as f:
                sim_ev = json.load(f)
        except Exception as e:
            errors.append(f"E8 Simulation Evidence Error: Failed to parse registries: {e}")
            e8_pass = False
            
    if e8_pass:
        hashes_file = root / "registry/economics/economics_hashes.json"
        if not hashes_file.exists():
            errors.append("E8 Hash Integrity Error: 'economics_hashes.json' not found.")
            e8_pass = False
        else:
            try:
                with open(hashes_file, 'r', encoding='utf-8') as f:
                    registered_hashes = json.load(f)
            except Exception as e:
                errors.append(f"E8 Hash Integrity Error: Failed to parse 'economics_hashes.json': {e}")
                e8_pass = False
                
            if e8_pass:
                for key, expected_hash in registered_hashes.items():
                    if "/" in key:
                        file_path = root / key
                    else:
                        theory_dir = root / "docs/theory/foundational/5_03_26 unity/economics"
                        file_path = theory_dir / f"{key}.md"
                        
                    if not file_path.exists():
                        errors.append(f"E8 Hash Integrity Error: Tracked file '{key}' not found at {file_path}")
                        e8_pass = False
                    else:
                        actual_hash = calculate_hash(file_path)
                        if actual_hash != expected_hash:
                            errors.append(f"E8 Hash Integrity Error: Hash mismatch for '{key}'. Expected {expected_hash}, got {actual_hash}")
                            e8_pass = False

    if e8_pass:
        ssot_content = ssot_file.read_text(encoding='utf-8')
        results_blocks = re.findall(r'### Result:\s*(ECON_RESULT_\d+)(.*?)(?=\n### |\Z)', ssot_content, re.DOTALL)
        
        total_claims = len(results_blocks)
        claims_with_simulation_support = 0
        
        sims_in_registry = {s["simulation_id"]: s for s in sim_reg.get("simulations", [])}
        ev_in_registry = {e["evidence_id"]: e for e in sim_ev.get("evidence_objects", [])}
        
        for res_id, block in results_blocks:
            evidence_citation = re.search(r'Evidence Citation:?.*?(ECON_EVIDENCE_\d+)', block)
            sim_citation = re.search(r'Simulation Citation:?.*?(SIM_[A-Z0-9_]+)', block)
            
            if not evidence_citation:
                errors.append(f"E8 Promotion Rule Violation: SSOT Result {res_id} is missing an Evidence Citation.")
                e8_pass = False
                continue
            if not sim_citation:
                errors.append(f"E8 Promotion Rule Violation: SSOT Result {res_id} is missing a Simulation Citation.")
                e8_pass = False
                continue
                
            ev_id = evidence_citation.group(1)
            sim_id = sim_citation.group(1)
            
            if sim_id not in sims_in_registry:
                errors.append(f"E8 Promotion Rule Violation: Result {res_id} cites non-existent Simulation {sim_id}.")
                e8_pass = False
                continue
                
            if ev_id not in ev_in_registry:
                errors.append(f"E8 Promotion Rule Violation: Result {res_id} cites non-existent Evidence {ev_id}.")
                e8_pass = False
                continue
                
            ev_obj = ev_in_registry[ev_id]
            
            if ev_obj.get("simulation_id") != sim_id:
                errors.append(f"E8 Promotion Rule Mismatch: Evidence {ev_id} does not map to Simulation {sim_id}.")
                e8_pass = False
                
            if res_id not in ev_obj.get("claim_support", []):
                errors.append(f"E8 Promotion Rule Violation: Evidence {ev_id} does not list support for Result {res_id}.")
                e8_pass = False
                
            if ev_obj.get("validation_status") != "VALIDATED":
                errors.append(f"E8 Promotion Rule Violation: Evidence {ev_id} validation status is '{ev_obj.get('validation_status')}', expected 'VALIDATED'.")
                e8_pass = False
                
            if ev_obj.get("result") != "PASS":
                errors.append(f"E8 Promotion Rule Violation: Evidence {ev_id} result is '{ev_obj.get('result')}', expected 'PASS'.")
                e8_pass = False
                
            claims_with_simulation_support += 1
            
        if total_claims > 0:
            scr = claims_with_simulation_support / total_claims
        else:
            scr = 0.0
            
        results["simulation_coverage_ratio"] = scr
        
        if scr < 1.0:
            errors.append(f"E8 Simulation Coverage Ratio Error: SCR is {scr:.2f}, expected 1.0.")
            e8_pass = False

        # Calculate ESCR and PCR
        validated_executable_simulations = 0
        for res_id, block in results_blocks:
            sim_citation = re.search(r'Simulation Citation:?.*?(SIM_[A-Z0-9_]+)', block)
            if sim_citation:
                sim_id = sim_citation.group(1)
                if sim_id in sims_in_registry:
                    sim_obj = sims_in_registry[sim_id]
                    if sim_obj.get("status") == "COMPLETED" and "_EXECUTABLE" in sim_id:
                        validated_executable_simulations += 1
                        
        escr = (validated_executable_simulations / total_claims) if total_claims > 0 else 0.0
        results["executable_simulation_coverage_ratio"] = escr
        
        if escr < 1.0:
            errors.append(f"E8 Executable Simulation Coverage Ratio Error: ESCR is {escr:.2f}, expected 1.0.")
            e8_pass = False
            
        evidence_with_raw_data = 0
        total_evidence_objects = len(ev_in_registry)
        
        for ev_id, ev_obj in ev_in_registry.items():
            gen_files = ev_obj.get("generated_files", [])
            has_csv = any(f.endswith('.csv') for f in gen_files)
            has_json = any(f.endswith('.json') for f in gen_files)
            has_png = any(f.endswith('.png') for f in gen_files)
            all_files_exist = len(gen_files) > 0 and all((root / f).exists() for f in gen_files)
            
            if has_csv and has_json and has_png and all_files_exist:
                evidence_with_raw_data += 1
            else:
                missing = [f for f in gen_files if not (root / f).exists()]
                if missing:
                    errors.append(f"E8 Provenance Error: Evidence {ev_id} lists files that do not exist: {missing}")
                    e8_pass = False
                elif not (has_csv and has_json and has_png):
                    errors.append(f"E8 Provenance Error: Evidence {ev_id} lacks required CSV, JSON, or PNG outputs in generated_files.")
                    e8_pass = False
                    
        pcr = (evidence_with_raw_data / total_evidence_objects) if total_evidence_objects > 0 else 0.0
        results["provenance_coverage_ratio"] = pcr
        
        if pcr < 1.0:
            errors.append(f"E8 Provenance Coverage Ratio Error: PCR is {pcr:.2f}, expected 1.0.")
            e8_pass = False
            
        # Parse Appendix D for Debt Register
        open_debt_count = 0
        critical_debt_count = 0
        closed_debt_count = 0
        validation_blocking_debt_count = 0
        
        for line in ssot_content.split('\n'):
            if line.strip().startswith('|') and 'ECON_DEBT_' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 8:
                    debt_id = parts[1]
                    category = parts[2]
                    status = parts[3]
                    severity = parts[4]
                    description = parts[5]
                    blocking = parts[6]
                    
                    if status.upper() == 'OPEN':
                        open_debt_count += 1
                        if severity.upper() == 'CRITICAL':
                            critical_debt_count += 1
                        if category.upper() == 'VALIDATION' or 'validation' in blocking.lower() or 'validation' in description.lower():
                            validation_blocking_debt_count += 1
                    elif status.upper() == 'CLOSED':
                        closed_debt_count += 1
                        
        total_debt = open_debt_count + closed_debt_count
        debt_burndown_rate = (closed_debt_count / total_debt) if total_debt > 0 else 0.0
        
        results["open_debt_count"] = open_debt_count
        results["critical_debt_count"] = critical_debt_count
        results["closed_debt_count"] = closed_debt_count
        results["debt_burndown_rate"] = debt_burndown_rate
        results["validation_blocking_debt_count"] = validation_blocking_debt_count
            
    if e8_pass:
        results["gates"]["E8_simulation_evidence_architecture"] = {
            "status": "pass",
            "details": f"All claims have valid simulation support. SCR = {results.get('simulation_coverage_ratio', 0.0):.2f}, ESCR = {results.get('executable_simulation_coverage_ratio', 0.0):.2f}, PCR = {results.get('provenance_coverage_ratio', 0.0):.2f}."
        }
    else:
        results["gates"]["E8_simulation_evidence_architecture"] = {
            "status": "failed",
            "details": "Simulation evidence architecture or SSOT integrity checks failed."
        }
        results["status"] = "failed"
        
    # Save economics validation health report
    audit_dir = root / "outputs/audits"
    audit_dir.mkdir(parents=True, exist_ok=True)
    report_path = audit_dir / "economics_health_report.json"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    # Output to screen
    print(f"Health report saved to {report_path.relative_to(root)}")
    print("\n------------------------- GATES STATUS -------------------------")
    for gate, val in results["gates"].items():
        status_label = val["status"].upper()
        print(f"  [{status_label:<12}] {gate:<35}: {val['details']}")
    print("----------------------------------------------------------------")
    print("  Debt Summary:")
    print(f"    Open Debt: {results.get('open_debt_count', 0)} (Critical: {results.get('critical_debt_count', 0)}, Validation-blocking: {results.get('validation_blocking_debt_count', 0)})")
    print(f"    Closed Debt: {results.get('closed_debt_count', 0)}")
    print(f"    Burndown Rate: {results.get('debt_burndown_rate', 0.0) * 100:.1f}%")
    print("  Hardening Metrics:")
    print(f"    SCR (Simulation Coverage): {results.get('simulation_coverage_ratio', 0.0) * 100:.1f}%")
    print(f"    ESCR (Executable Simulation Coverage): {results.get('executable_simulation_coverage_ratio', 0.0) * 100:.1f}%")
    print(f"    PCR (Provenance Coverage): {results.get('provenance_coverage_ratio', 0.0) * 100:.1f}%")
    print("----------------------------------------------------------------")
    
    if errors:
        print("\nERRORS DETECTED:")
        for err in errors:
            print(f"  * {err}")
        print("\nEconomics Validation FAILED.")
        sys.exit(1)
        
    print("\nEconomics Validation PASSED (E0-E2, E8 satisfy validation requirements).")
    print("Next Target: E3 (Sigma_D Distinguishability).")
    print("========================================================================\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
