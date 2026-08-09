import unittest
import random
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import solve_csp_native

class TestSymbolicIdentityLeakage(unittest.TestCase):
    def test_opacity_under_rename_and_order(self):
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
        
        # 1. Baseline
        w1, _, _ = solve_csp_native(variables, constraints)
        self.assertIsNone(w1)
        
        # 2. Rename variables to opaque identifiers, randomize ordering
        opaque_vars = [
            {"name": "VAR_A", "domain": ["0", "1"]},
            {"name": "VAR_B", "domain": ["0", "1"]},
            {"name": "VAR_C", "domain": ["0", "1"]}
        ]
        opaque_constraints = [
            {"id": "c_triad", "type": "triad_closure", "variables": ["VAR_A", "VAR_B", "VAR_C"]},
            {"id": "c_e12", "type": "projection_membership", "variables": ["VAR_A"], "parameters": {"allowed_values": ["1"]}},
            {"id": "c_e23", "type": "projection_membership", "variables": ["VAR_B"], "parameters": {"allowed_values": ["1"]}},
            {"id": "c_e31", "type": "projection_membership", "variables": ["VAR_C"], "parameters": {"allowed_values": ["0"]}}
        ]
        
        # Randomize order
        random.seed(42)
        random.shuffle(opaque_vars)
        random.shuffle(opaque_constraints)
        
        w2, _, _ = solve_csp_native(opaque_vars, opaque_constraints)
        self.assertIsNone(w2) # Must remain UNSAT

if __name__ == "__main__":
    unittest.main()
