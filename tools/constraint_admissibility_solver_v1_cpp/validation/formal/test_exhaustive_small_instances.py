import unittest
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import (
    solve_csp_native, satisfies_constraint
)
from tools.constraint_admissibility_solver_v1_cpp.validation.independence.pysat_encoder import PySatEncoder

class TestExhaustiveSmallInstances(unittest.TestCase):
    def test_three_way_unsat_agreement(self):
        # A known UNSAT triad configuration
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
        
        # 1. Native solver
        witness_native, _, complete = solve_csp_native(variables, constraints)
        self.assertTrue(complete)
        self.assertIsNone(witness_native)
        
        # 2. PySAT solver
        encoder = PySatEncoder(variables, constraints)
        dec_pysat, _ = encoder.solve()
        self.assertEqual(dec_pysat, "UNSAT")
        
        # 3. Exhaustive search
        exhaust_sat = False
        for v12 in ["0", "1"]:
            for v23 in ["0", "1"]:
                for v31 in ["0", "1"]:
                    assignment = {"e12": v12, "e23": v23, "e31": v31}
                    if all(satisfies_constraint(assignment, c) for c in constraints):
                        exhaust_sat = True
                        break
        self.assertFalse(exhaust_sat, "Exhaustive search found a witness, but solvers returned UNSAT!")

if __name__ == "__main__":
    unittest.main()
