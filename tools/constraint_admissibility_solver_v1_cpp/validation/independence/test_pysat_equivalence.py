import unittest
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import solve_csp_native
from tools.constraint_admissibility_solver_v1_cpp.validation.independence.pysat_encoder import PySatEncoder

class TestPySatEquivalence(unittest.TestCase):
    def test_pysat_native_agreement(self):
        # 1. Triad closure test (satisfiable)
        variables = [
            {"name": "e12", "domain": ["0", "1"]},
            {"name": "e23", "domain": ["0", "1"]},
            {"name": "e31", "domain": ["0", "1"]}
        ]
        constraints = [
            {"id": "c_triad", "type": "triad_closure", "variables": ["e12", "e23", "e31"]}
        ]
        
        witness_native, _, complete = solve_csp_native(variables, constraints)
        self.assertTrue(complete)
        
        encoder = PySatEncoder(variables, constraints)
        dec_pysat, witness_pysat = encoder.solve()
        
        self.assertEqual("SAT" if witness_native is not None else "UNSAT", dec_pysat)
        
        # 2. Contradictory test (unsatisfiable)
        constraints_unsat = [
            {"id": "c_triad", "type": "triad_closure", "variables": ["e12", "e23", "e31"]},
            {"id": "c_e12", "type": "projection_membership", "variables": ["e12"], "parameters": {"allowed_values": ["1"]}},
            {"id": "c_e23", "type": "projection_membership", "variables": ["e23"], "parameters": {"allowed_values": ["1"]}},
            {"id": "c_e31", "type": "projection_membership", "variables": ["e31"], "parameters": {"allowed_values": ["0"]}}
        ]
        
        witness_native_unsat, _, complete = solve_csp_native(variables, constraints_unsat)
        self.assertTrue(complete)
        
        encoder_unsat = PySatEncoder(variables, constraints_unsat)
        dec_pysat_unsat, _ = encoder_unsat.solve()
        
        self.assertEqual("UNSAT", dec_pysat_unsat)

if __name__ == "__main__":
    unittest.main()
