import unittest
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import satisfies_constraint
from tools.constraint_admissibility_solver_v1_cpp.validation.independence.pysat_encoder import PySatEncoder

class TestSatWitnessValidation(unittest.TestCase):
    def test_witness_satisfies_constraints(self):
        variables = [
            {"name": "x", "domain": ["A", "B"]},
            {"name": "y", "domain": ["B", "C"]}
        ]
        constraints = [
            {
                "id": "c1",
                "type": "coupling_membership",
                "variables": ["x", "y"],
                "parameters": {"allowed_pairs": [["A", "B"], ["B", "C"]]}
            }
        ]
        
        encoder = PySatEncoder(variables, constraints)
        dec, witness = encoder.solve()
        
        self.assertEqual(dec, "SAT")
        self.assertIsNotNone(witness)
        
        # Verify witness satisfies all original constraints
        for c in constraints:
            self.assertTrue(satisfies_constraint(witness, c))

if __name__ == "__main__":
    unittest.main()
