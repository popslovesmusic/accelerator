import unittest
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import solve_csp_native
from tools.constraint_admissibility_solver_v1_cpp.validation.independence.pysat_encoder import PySatEncoder

class TestBlindFixtureExecution(unittest.TestCase):
    def test_blind_equivalence(self):
        # Normal variables
        variables = [
            {"name": "x", "domain": ["0", "1"]},
            {"name": "y", "domain": ["0", "1"]}
        ]
        constraints = [
            {"id": "c1", "type": "coupling_membership", "variables": ["x", "y"], "parameters": {"allowed_pairs": [["0", "1"]]}}
        ]
        
        # Blinded/Opaque variables
        blind_vars = [
            {"name": "VAR_A", "domain": ["0", "1"]},
            {"name": "VAR_B", "domain": ["0", "1"]}
        ]
        blind_constraints = [
            {"id": "c1", "type": "coupling_membership", "variables": ["VAR_A", "VAR_B"], "parameters": {"allowed_pairs": [["0", "1"]]}}
        ]
        
        # Native checks
        w1_native, _, _ = solve_csp_native(variables, constraints)
        w2_native, _, _ = solve_csp_native(blind_vars, blind_constraints)
        
        self.assertEqual(w1_native is None, w2_native is None)
        
        # PySAT checks
        enc1 = PySatEncoder(variables, constraints)
        dec1, _ = enc1.solve()
        
        enc2 = PySatEncoder(blind_vars, blind_constraints)
        dec2, _ = enc2.solve()
        
        self.assertEqual(dec1, dec2)

if __name__ == "__main__":
    unittest.main()
