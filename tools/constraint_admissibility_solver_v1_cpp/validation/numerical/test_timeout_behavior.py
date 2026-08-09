import unittest
import time
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import solve_csp_native

class TestTimeoutBehavior(unittest.TestCase):
    def test_execution_timeout(self):
        # A large domain that requires many backtracking steps to solve
        variables = [
            {"name": f"x{i}", "domain": [str(j) for j in range(20)]} for i in range(8)
        ]
        
        # A contradiction to force deep search
        constraints = [
            {"id": "c_fail", "type": "coupling_membership", "variables": ["x0", "x1"], "parameters": {"allowed_pairs": []}}
        ]
        
        # Restrict execution time to a negative limit to guarantee timeout
        witness, _, complete = solve_csp_native(variables, constraints, max_time=-1.0)
        
        self.assertFalse(complete)
        self.assertIsNone(witness)

if __name__ == "__main__":
    unittest.main()
