import unittest
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import solve_csp_native
from tools.constraint_admissibility_solver_v1_cpp.validation.independence.pysat_encoder import PySatEncoder

class TestUnsatAgreement(unittest.TestCase):
    def test_unsat_consensus(self):
        variables = [
            {"name": "x", "domain": ["A", "B"]}
        ]
        
        # Impossible projection constraints
        constraints = [
            {"id": "c1", "type": "projection_membership", "variables": ["x"], "parameters": {"allowed_values": ["A"]}},
            {"id": "c2", "type": "projection_membership", "variables": ["x"], "parameters": {"allowed_values": ["B"]}}
        ]
        
        witness_native, _, complete = solve_csp_native(variables, constraints)
        self.assertTrue(complete)
        self.assertIsNone(witness_native)
        
        encoder = PySatEncoder(variables, constraints)
        dec_pysat, _ = encoder.solve()
        
        self.assertEqual(dec_pysat, "UNSAT")

if __name__ == "__main__":
    unittest.main()
