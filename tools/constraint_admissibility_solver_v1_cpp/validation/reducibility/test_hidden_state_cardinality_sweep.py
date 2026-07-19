import unittest
import json
import os

class TestHiddenStateCardinalitySweep(unittest.TestCase):
    def test_sweep_log_integrity(self):
        output_file = "tools/constraint_admissibility_solver_v1_cpp/validation/reducibility/reducibility_search_output.json"
        
        # Verify the file is generated and contains valid sweep parameters
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, "r") as f:
            data = json.load(f)
            
        self.assertIn("hidden_state_cardinality", data)
        self.assertGreaterEqual(data["hidden_state_cardinality"], 0)

if __name__ == "__main__":
    unittest.main()
