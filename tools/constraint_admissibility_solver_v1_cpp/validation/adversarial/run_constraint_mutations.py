import os
import sys
import json
import subprocess
import shutil

MUTATIONS = [
    {
        "id": "MUT-CSP-001",
        "description": "Drop exactly-one clauses in PySAT",
        "target": "self.clauses.append(lits)\n            \n            # At most one value can be selected",
        "replacement": "# self.clauses.append(lits)\n            \n            # At most one value can be selected",
        "file": "tools/constraint_admissibility_solver_v1_cpp/validation/independence/pysat_encoder.py"
    },
    {
        "id": "MUT-CSP-002",
        "description": "Replace exactly-one with at-least-one",
        "target": "self.clauses.append([-lits[i], -lits[j]])",
        "replacement": "# self.clauses.append([-lits[i], -lits[j]])",
        "file": "tools/constraint_admissibility_solver_v1_cpp/validation/independence/pysat_encoder.py"
    },
    {
        "id": "MUT-CSP-003",
        "description": "Reverse a compatibility relation",
        "target": "return vals[0] == vals[1]",
        "replacement": "return vals[0] != vals[1]",
        "file": "tools/constraint_admissibility_solver_v1_cpp/sim_governed.py"
    },
    {
        "id": "MUT-CSP-004",
        "description": "Remove a projection restriction",
        "target": "return vals[0] in allowed",
        "replacement": "return True",
        "file": "tools/constraint_admissibility_solver_v1_cpp/sim_governed.py"
    },
    {
        "id": "MUT-CSP-005",
        "description": "Permit an invalid composition",
        "target": "if domain and vals[0] not in domain:\n            return False",
        "replacement": "if domain and vals[0] not in domain:\n            return True",
        "file": "tools/constraint_admissibility_solver_v1_cpp/sim_governed.py"
    },
    {
        "id": "MUT-CSP-006",
        "description": "Delete one triad clause",
        "target": "self.clauses.append([-lit1, -lit2, -lit_v3_inactive])",
        "replacement": "# self.clauses.append([-lit1, -lit2, -lit_v3_inactive])",
        "file": "tools/constraint_admissibility_solver_v1_cpp/validation/independence/pysat_encoder.py"
    },
    {
        "id": "MUT-CSP-007",
        "description": "Duplicate a literal in exactly-one",
        "target": "lits = [self.var_val_to_lit[(var_name, val)] for val in domain]",
        "replacement": "lits = [self.var_val_to_lit[(var_name, val)] for val in domain] + [1]",
        "file": "tools/constraint_admissibility_solver_v1_cpp/validation/independence/pysat_encoder.py"
    },
    {
        "id": "MUT-CSP-008",
        "description": "Swap domain and codomain in composition",
        "target": "domain = params.get(\"domain\", [])\n        codomain = params.get(\"codomain\", [])",
        "replacement": "domain = params.get(\"codomain\", [])\n        codomain = params.get(\"domain\", [])",
        "file": "tools/constraint_admissibility_solver_v1_cpp/sim_governed.py"
    },
    {
        "id": "MUT-CSP-009",
        "description": "Return SAT on timeout",
        "target": "return None, explored_nodes[0], False",
        "replacement": "return {'x':'0'}, explored_nodes[0], False",
        "file": "tools/constraint_admissibility_solver_v1_cpp/sim_governed.py"
    },
    {
        "id": "MUT-CSP-010",
        "description": "Suppress INDETERMINATE decision",
        "target": "decision = \"SAT\" if is_sat_native else (\"UNSAT\" if (complete_native and not is_sat_native) else \"INDETERMINATE\")",
        "replacement": "decision = \"SAT\" if is_sat_native else \"UNSAT\"",
        "file": "tools/constraint_admissibility_solver_v1_cpp/sim_governed.py"
    },
    {
        "id": "MUT-CSP-011",
        "description": "Corrupt witness reconstruction",
        "target": "witness[var_name] = val",
        "replacement": "witness[var_name] = 'CORRUPTED'",
        "file": "tools/constraint_admissibility_solver_v1_cpp/validation/independence/pysat_encoder.py"
    },
    {
        "id": "MUT-CSP-012",
        "description": "Return a non-minimal UNSAT core",
        "target": "core = candidate",
        "replacement": "pass",
        "file": "tools/constraint_admissibility_solver_v1_cpp/sim_governed.py"
    }
]

def main():
    print("Initializing constraint solver mutation testing campaign...")
    
    # Store backups
    backups = {}
    for mut in MUTATIONS:
        filepath = mut["file"]
        if filepath not in backups:
            backup_path = filepath + ".bak"
            shutil.copy(filepath, backup_path)
            backups[filepath] = backup_path
            
    results = {}
    
    try:
        for mut in MUTATIONS:
            print(f"Applying mutation {mut['id']}: {mut['description']}")
            filepath = mut["file"]
            backup_path = backups[filepath]
            
            with open(backup_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if mut["target"] not in content:
                print(f"ERROR: Target string not found for mutation {mut['id']}: {mut['target']}")
                results[mut["id"]] = "target_not_found"
                continue
                
            # Apply mutation
            mutated_content = content.replace(mut["target"], mut["replacement"])
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(mutated_content)
                
            # Run the unit and integration tests
            test_cmds = [
                [".venv/Scripts/python.exe", "-m", "tools.constraint_admissibility_solver_v1_cpp.validation.unit.test_regression"],
                [".venv/Scripts/python.exe", "-m", "tools.constraint_admissibility_solver_v1_cpp.validation.independence.test_pysat_equivalence"],
                [".venv/Scripts/python.exe", "-m", "tools.constraint_admissibility_solver_v1_cpp.validation.independence.test_sat_witness_validation"],
                [".venv/Scripts/python.exe", "-m", "tools.constraint_admissibility_solver_v1_cpp.validation.reference.test_reference"]
            ]
            
            detected = False
            for cmd in test_cmds:
                res = subprocess.run(cmd, capture_output=True)
                if res.returncode != 0:
                    detected = True
                    break
                    
            results[mut["id"]] = "detected" if detected else "survived"
            print(f"Mutation {mut['id']} result: {results[mut['id']]}")
            
    finally:
        # Restore backups
        for filepath, backup_path in backups.items():
            shutil.copy(backup_path, filepath)
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
    # Calculate score
    detected_count = sum(1 for v in results.values() if v == "detected")
    overall_score = detected_count / len(MUTATIONS) if MUTATIONS else 0.0
    
    out_dir = "tools/constraint_admissibility_solver_v1_cpp/validation/adversarial"
    os.makedirs(out_dir, exist_ok=True)
    
    with open(os.path.join(out_dir, "mutation_manifest.json"), "w") as f:
        json.dump(MUTATIONS, f, indent=2)
        
    summary = {
        "mutation_score": overall_score,
        "total_mutations": len(MUTATIONS),
        "detected_count": detected_count,
        "results": results
    }
    
    with open(os.path.join(out_dir, "mutation_results.json"), "w") as f:
        json.dump(summary, f, indent=2)
        
    print(f"Mutation audit completed. Score: {overall_score}")

if __name__ == "__main__":
    main()
