import unittest
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import solve_csp_native

class TestBoundExhaustion(unittest.TestCase):
    def test_node_limit_exhaustion(self):
        # A large domain that requires many backtracking steps
        variables = [
            {"name": f"x{i}", "domain": [str(j) for j in range(10)]} for i in range(5)
        ]
        
        # A set of contradictions to force exhaustive search
        constraints = [
            {"id": "c_fail", "type": "coupling_membership", "variables": ["x0", "x1"], "parameters": {"allowed_pairs": []}}
        ]
        
        # Restrict max nodes to 2 (well below the required search nodes)
        witness, nodes, complete = solve_csp_native(variables, constraints, max_nodes=2)
        
        self.assertFalse(complete)
        self.assertIsNone(witness)

if __name__ == "__main__":
    unittest.main()
