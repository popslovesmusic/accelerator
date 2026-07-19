import unittest
import json
import os
from tools.constraint_admissibility_solver_v1_cpp.validation.reducibility.binary_hidden_state_encoder import BinaryHiddenStateSearcher

class TestBinaryReducibility(unittest.TestCase):
    def test_run_reducibility_search(self):
        # Enumerate allowed and forbidden observable configurations for cycle triad closure
        allowed = [
            ("0", "0", "0"),
            ("0", "0", "1"),
            ("0", "1", "0"),
            ("1", "0", "0"),
            ("1", "1", "1")
        ]
        forbidden = [
            ("0", "1", "1"),
            ("1", "0", "1"),
            ("1", "1", "0")
        ]
        
        searcher = BinaryHiddenStateSearcher(allowed, forbidden, max_h=3)
        result = searcher.search_for_rival()
        
        print(f"Reducibility decision: {result['decision']}")
        if result["decision"] == "REDUCIBLE":
            print(f"Rival found with hidden state H = {result['hidden_state_cardinality']}")
            
        # Verify the decision adheres to the contract
        self.assertIn(result["decision"], ["REDUCIBLE", "NO_RIVAL_WITHIN_COMPLETE_BOUNDS", "INCONCLUSIVE"])
        
        # Save results to a result file to be collated in C4B
        res_dir = "tools/constraint_admissibility_solver_v1_cpp/validation/reducibility"
        os.makedirs(res_dir, exist_ok=True)
        
        output_data = {
            "decision": result["decision"],
            "rival_witness": result["rival_witness"],
            "hidden_state_cardinality": result["hidden_state_cardinality"],
            "search_complete": result["search_complete"],
            "search_scope": "Search space over binary relations plus hidden state from H=0 to 3",
            "explored_candidate_count": result["explored_candidate_count"],
            "provenance": {"environment": "CPython"}
        }
        
        with open(os.path.join(res_dir, "reducibility_search_output.json"), "w") as f:
            json.dump(output_data, f, indent=2)

if __name__ == "__main__":
    unittest.main()
