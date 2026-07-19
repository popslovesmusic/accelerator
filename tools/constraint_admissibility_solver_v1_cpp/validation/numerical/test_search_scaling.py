import json
import os
import sys
import time
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import solve_csp_native

def run_scaling_sweep():
    # Sweep variable counts (2 to 6)
    # Sweep domain sizes (2 to 3)
    results = []
    
    for num_vars in range(2, 7):
        for domain_size in range(2, 4):
            # Construct a standard variables set
            domain = [str(i) for i in range(domain_size)]
            variables = [{"name": f"x{i}", "domain": domain} for i in range(num_vars)]
            
            # Simple projection constraints on each variable
            constraints = []
            for i in range(num_vars):
                constraints.append({
                    "id": f"c{i}",
                    "type": "projection_membership",
                    "variables": [f"x{i}"],
                    "parameters": {"allowed_values": ["0"]}
                })
                
            # Measure point
            start_time = time.time()
            witness, nodes, complete = solve_csp_native(variables, constraints)
            elapsed = time.time() - start_time
            
            results.append({
                "num_variables": num_vars,
                "domain_size": domain_size,
                "explored_nodes": nodes,
                "elapsed_seconds": elapsed,
                "decision": "SAT" if witness is not None else "UNSAT",
                "completeness": complete
            })
            
    return results

def main():
    print("Running assignment-space scaling sweep...")
    scaling_data = run_scaling_sweep()
    
    out_dir = "tools/constraint_admissibility_solver_v1_cpp/validation/numerical"
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "search_scaling_results.json"), "w") as f:
        json.dump(scaling_data, f, indent=2)
        
    print("Scaling sweep completed. Results written to search_scaling_results.json")

if __name__ == "__main__":
    main()
