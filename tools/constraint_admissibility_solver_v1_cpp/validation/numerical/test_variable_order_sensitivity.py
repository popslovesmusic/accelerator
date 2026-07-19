import unittest
import numpy as np
import copy
import random
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import solve_csp_native

class TestVariableOrderSensitivity(unittest.TestCase):
    def test_order_invariance(self):
        # A contradictory triad instance
        variables = [
            {"name": "e12", "domain": ["0", "1"]},
            {"name": "e23", "domain": ["0", "1"]},
            {"name": "e31", "domain": ["0", "1"]}
        ]
        
        constraints = [
            {"id": "c_triad", "type": "triad_closure", "variables": ["e12", "e23", "e31"]},
            {"id": "c_e12", "type": "projection_membership", "variables": ["e12"], "parameters": {"allowed_values": ["1"]}},
            {"id": "c_e23", "type": "projection_membership", "variables": ["e23"], "parameters": {"allowed_values": ["1"]}},
            {"id": "c_e31", "type": "projection_membership", "variables": ["e31"], "parameters": {"allowed_values": ["0"]}}
        ]
        
        # Original ordering decision
        orig_witness, _, _ = solve_csp_native(variables, constraints)
        self.assertIsNone(orig_witness)
        
        # Test 10 random permutations of variables
        random.seed(42)
        for _ in range(10):
            permuted_vars = list(variables)
            random.shuffle(permuted_vars)
            
            witness, _, complete = solve_csp_native(permuted_vars, constraints)
            self.assertTrue(complete)
            self.assertIsNone(witness) # Must remain UNSAT

if __name__ == "__main__":
    unittest.main()
