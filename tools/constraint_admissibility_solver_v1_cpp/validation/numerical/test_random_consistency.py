import unittest
import random
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import (
    solve_csp_native, solve_csp_oracle, satisfies_constraint
)

class TestRandomConsistency(unittest.TestCase):
    def test_randomized_agreement(self):
        random.seed(42)
        
        for trial in range(30):
            # Generate bounded random CSP
            num_vars = random.randint(2, 4)
            variables = [
                {"name": f"x{i}", "domain": ["0", "1", "2"]} for i in range(num_vars)
            ]
            
            num_constraints = random.randint(1, 3)
            constraints = []
            for c_idx in range(num_constraints):
                c_type = random.choice(["triad_closure", "coupling_membership", "projection_membership"])
                if c_type == "triad_closure":
                    # Closure constraint on 3 variables
                    vars_involved = random.sample([v["name"] for v in variables], min(3, num_vars))
                elif c_type == "coupling_membership":
                    vars_involved = random.sample([v["name"] for v in variables], min(2, num_vars))
                else:
                    vars_involved = [random.choice(variables)["name"]]
                    
                constraints.append({
                    "id": f"c{c_idx}",
                    "type": c_type,
                    "variables": vars_involved,
                    "parameters": {
                        "allowed_values": ["1", "2"],
                        "allowed_pairs": [["0", "1"], ["1", "2"], ["2", "0"]]
                    }
                })
                
            # Run both solvers
            w_native, _, c_native = solve_csp_native(variables, constraints)
            w_oracle, _, c_oracle = solve_csp_oracle(variables, constraints)
            
            if c_native and c_oracle:
                self.assertEqual(w_native is None, w_oracle is None)
                
                if w_native is not None:
                    # Validate witness assignment correctness
                    for c in constraints:
                        self.assertTrue(satisfies_constraint(w_native, c))

if __name__ == "__main__":
    unittest.main()
