import json
import os
import sys
import unittest
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import (
    solve_csp_native, extract_unsatisfied_core
)

class TestCoreStability(unittest.TestCase):
    def test_core_stability_evaluation(self):
        variables = [
            {"name": "x", "domain": ["0", "1"]},
            {"name": "y", "domain": ["0", "1"]}
        ]
        
        # A simple unsatisfiable set of constraints
        constraints = [
            {"id": "c1", "type": "coupling_membership", "variables": ["x", "y"], "parameters": {"allowed_pairs": [["0", "0"]]}},
            {"id": "c2", "type": "projection_membership", "variables": ["x"], "parameters": {"allowed_values": ["1"]}},
            {"id": "c3", "type": "projection_membership", "variables": ["y"], "parameters": {"allowed_values": ["1"]}}
        ]
        
        core, core_type, verified = extract_unsatisfied_core(variables, constraints)
        
        self.assertTrue(verified)
        self.assertEqual(core_type, "subset_minimal")
        # Either {c1, c2} or {c1, c3} is a minimal unsatisfiable core.
        self.assertGreater(len(core), 0)
        self.assertLess(len(core), len(constraints))
        
        # Write results file
        results = {
            "experiment_name": "unsatisfied_core_characterization",
            "constraints_evaluated": len(constraints),
            "core_size_returned": len(core),
            "core_type_labeled": core_type,
            "minimality_verified": verified,
            "verification_method": "greedy_deletion_filter"
        }
        
        out_dir = "tools/constraint_admissibility_solver_v1_cpp/validation/numerical"
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "core_characterization_results.json"), "w") as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    unittest.main()
