import unittest
import random
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import solve_csp_native

class TestConstraintOrderInvariance(unittest.TestCase):
    def test_constraint_invariance(self):
        variables = [
            {"name": "x", "domain": ["0", "1"]},
            {"name": "y", "domain": ["0", "1"]}
        ]
        
        # A satisfiable set with constraints that can have multiple witnesses
        constraints = [
            {"id": "c1", "type": "coupling_membership", "variables": ["x", "y"]},
            {"id": "c2", "type": "projection_membership", "variables": ["x"], "parameters": {"allowed_values": ["0", "1"]}}
        ]
        
        # Check that all permutations yield SAT decisions
        random.seed(42)
        for _ in range(10):
            permuted_constraints = list(constraints)
            random.shuffle(permuted_constraints)
            
            witness, _, complete = solve_csp_native(variables, permuted_constraints)
            self.assertTrue(complete)
            self.assertIsNotNone(witness) # Must remain SAT

if __name__ == "__main__":
    unittest.main()
