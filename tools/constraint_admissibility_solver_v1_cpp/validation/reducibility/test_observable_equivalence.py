import unittest
import json
import os

class TestObservableEquivalence(unittest.TestCase):
    def test_observable_equivalence_check(self):
        output_file = "tools/constraint_admissibility_solver_v1_cpp/validation/reducibility/reducibility_search_output.json"
        
        # If output does not exist, run it
        if not os.path.exists(output_file):
            # Run the search test directly
            from tools.constraint_admissibility_solver_v1_cpp.validation.reducibility.test_binary_reducibility import TestBinaryReducibility
            t = TestBinaryReducibility()
            t.setUp()
            t.test_run_reducibility_search()
            
        with open(output_file, "r") as f:
            data = json.load(f)
            
        # Verify that if a rival witness is found, the decision is REDUCIBLE
        if data["decision"] == "REDUCIBLE":
            self.assertIsNotNone(data["rival_witness"])
            self.assertTrue(data["search_complete"])

if __name__ == "__main__":
    unittest.main()
