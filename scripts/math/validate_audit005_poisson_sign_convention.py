import json
import os
import sys

def validate_poisson_audit():
    registry_path = "registry/math/audit005_poisson_sign_convention_registry.json"
    audit_doc_path = "docs/math/poisson_sign_convention_audit.md"
    solver_cpp_path = "tools/accelerator_sim_v1_cpp/PoissonSolver.cpp"
    lattice_h_path = "tools/accelerator_sim_v1_cpp/LatticeElements.h"
    
    report = {
        "status": "pass",
        "checks": {},
        "errors": []
    }
    
    # Check registry existence
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append(f"Registry missing: {registry_path}")
        report["checks"]["registry_exists"] = "fail"
    else:
        report["checks"]["registry_exists"] = "pass"
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
            report["checks"]["id_match"] = registry.get("id") == "AUDIT-005"
            report["checks"]["internal_consistency_verified"] = registry.get("audit_findings", {}).get("internal_consistency") == "verified"

    # Check audit doc existence
    if not os.path.exists(audit_doc_path):
        report["status"] = "fail"
        report["errors"].append(f"Audit document missing: {audit_doc_path}")
        report["checks"]["audit_doc_exists"] = "fail"
    else:
        report["checks"]["audit_doc_exists"] = "pass"
        with open(audit_doc_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            if "poisson solver" in content and "repulsive" in content and "consistent" in content:
                report["checks"]["policy_content_verified"] = "pass"
            else:
                report["checks"]["policy_content_verified"] = "fail"
                report["errors"].append("Policy document lacks required convention definitions")

    # Verify implementation hasn't changed sign silently (Read-only check)
    if os.path.exists(solver_cpp_path):
        with open(solver_cpp_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "kernel_[i * (ny_/2 + 1) + j] = 1.0 / k2" in content:
                report["checks"]["solver_kernel_verified"] = "pass"
            else:
                report["status"] = "fail"
                report["checks"]["solver_kernel_verified"] = "fail"
                report["errors"].append("Poisson solver kernel mismatch - possible silent sign change")

    if os.path.exists(lattice_h_path):
        with open(lattice_h_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "double ex = -(phi_grid_" in content:
                report["checks"]["force_sign_verified"] = "pass"
            else:
                report["status"] = "fail"
                report["checks"]["force_sign_verified"] = "fail"
                report["errors"].append("Force calculation sign mismatch - possible silent change")

    output_path = "outputs/audits/math_program_validation_after_audit005_poisson_sign_convention.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"audit005_poisson_sign_convention_validation": report}, f, indent=2)
    
    print(json.dumps({"audit005_poisson_sign_convention_validation": report}, indent=2))
    return 0 if report["status"] == "pass" else 1

if __name__ == "__main__":
    sys.exit(validate_poisson_audit())
