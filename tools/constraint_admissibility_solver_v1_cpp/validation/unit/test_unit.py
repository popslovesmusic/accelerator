import unittest
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import (
    solve_csp_native, solve_csp_oracle, extract_unsatisfied_core
)

class TestConstraintSolver(unittest.TestCase):
    def setUp(self):
        # Setup a simple variable set (three edges of a triad)
        self.variables = [
            {"name": "e12", "domain": ["0", "1"]},
            {"name": "e23", "domain": ["0", "1"]},
            {"name": "e31", "domain": ["0", "1"]}
        ]
        
    def test_satisfiable_triad(self):
        # A satisfiable triad (all active "1" or all inactive "0")
        constraints = [
            {
                "id": "c1",
                "type": "triad_closure",
                "variables": ["e12", "e23", "e31"]
            }
        ]
        
        witness_native = solve_csp_native(self.variables, constraints)
        witness_oracle = solve_csp_oracle(self.variables, constraints)
        
        self.assertIsNotNone(witness_native)
        self.assertIsNotNone(witness_oracle)
        self.assertEqual(witness_native["e12"], witness_oracle["e12"])
        
    def test_unsatisfiable_triad(self):
        # Contradictory triad: closure requires either all active/inactive,
        # but we add constraints forcing exactly two edges active.
        constraints = [
            {
                "id": "c_triad",
                "type": "triad_closure",
                "variables": ["e12", "e23", "e31"]
            },
            {
                "id": "c_e12",
                "type": "projection_membership",
                "variables": ["e12"],
                "parameters": {"allowed_values": ["1"]}
            },
            {
                "id": "c_e23",
                "type": "projection_membership",
                "variables": ["e23"],
                "parameters": {"allowed_values": ["1"]}
            },
            {
                "id": "c_e31",
                "type": "projection_membership",
                "variables": ["e31"],
                "parameters": {"allowed_values": ["0"]}
            }
        ]
        
        witness_native = solve_csp_native(self.variables, constraints)
        witness_oracle = solve_csp_oracle(self.variables, constraints)
        
        self.assertNullStatus = witness_native is None
        self.assertTrue(self.assertNullStatus)
        self.assertIsNone(witness_oracle)
        
        # Extract minimal unsatisfied core
        core = extract_unsatisfied_core(self.variables, constraints)
        self.assertGreater(len(core), 0)
        self.assertIn("c_triad", core)

if __name__ == "__main__":
    unittest.main()
