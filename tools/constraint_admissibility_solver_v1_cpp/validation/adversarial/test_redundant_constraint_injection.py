import unittest
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import solve_csp_native

class TestRedundantConstraintInjection(unittest.TestCase):
    def test_redundancy_resilience(self):
        variables = [
            {"name": "x", "domain": ["0", "1"]},
            {"name": "y", "domain": ["0", "1"]}
        ]
        
        # Satisfiable baseline
        constraints = [
            {"id": "c1", "type": "coupling_membership", "variables": ["x", "y"]}
        ]
        
        w1, _, _ = solve_csp_native(variables, constraints)
        self.assertIsNotNone(w1)
        
        # Inject duplicate and redundant constraint
        constraints_with_redundancy = [
            {"id": "c1", "type": "coupling_membership", "variables": ["x", "y"]},
            {"id": "c1_dup", "type": "coupling_membership", "variables": ["x", "y"]},
            {"id": "c2_redundant", "type": "projection_membership", "variables": ["x"], "parameters": {"allowed_values": ["0", "1"]}}
        ]
        
        w2, _, _ = solve_csp_native(variables, constraints_with_redundancy)
        self.assertIsNotNone(w2)
        self.assertEqual(w1["x"], w2["x"])

if __name__ == "__main__":
    unittest.main()
