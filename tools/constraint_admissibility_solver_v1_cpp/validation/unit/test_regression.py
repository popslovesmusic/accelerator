import unittest
import numpy as np
import copy
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import (
    solve_csp_native, solve_csp_oracle, extract_unsatisfied_core, satisfies_constraint
)

class TestRegression(unittest.TestCase):
    def setUp(self):
        self.variables = [
            {"name": "x", "domain": ["0", "1"]},
            {"name": "y", "domain": ["0", "1"]},
            {"name": "z", "domain": ["0", "1"]}
        ]
        
    def test_r01_empty_constraints(self):
        # Empty constraint set must be SAT
        witness, _, complete = solve_csp_native(self.variables, [])
        self.assertTrue(complete)
        self.assertIsNotNone(witness)
        
    def test_r02_empty_domain(self):
        # Empty domain must raise ValueError or exit
        bad_vars = [
            {"name": "x", "domain": []}
        ]
        with self.assertRaises(ValueError):
            solve_csp_native(bad_vars, [])
            
    def test_r03_duplicate_constraints(self):
        # Duplicate constraints must not alter decision
        constraints = [
            {"id": "c1", "type": "triad_closure", "variables": ["x", "y", "z"]},
            {"id": "c1_dup", "type": "triad_closure", "variables": ["x", "y", "z"]}
        ]
        witness, _, complete = solve_csp_native(self.variables, constraints)
        self.assertTrue(complete)
        self.assertIsNotNone(witness)
        
    def test_r04_constraint_order_permutation(self):
        # Permuting constraint order does not change decision
        c1 = {"id": "c_triad", "type": "triad_closure", "variables": ["x", "y", "z"]}
        c2 = {"id": "c_x", "type": "projection_membership", "variables": ["x"], "parameters": {"allowed_values": ["1"]}}
        
        ord_1 = [c1, c2]
        ord_2 = [c2, c1]
        
        w1, _, comp1 = solve_csp_native(self.variables, ord_1)
        w2, _, comp2 = solve_csp_native(self.variables, ord_2)
        
        self.assertEqual(w1 is None, w2 is None)
        
    def test_r05_variable_order_permutation(self):
        # Permuting variables list does not change decision
        constraints = [
            {"id": "c_triad", "type": "triad_closure", "variables": ["x", "y", "z"]}
        ]
        vars_1 = copy.deepcopy(self.variables)
        vars_2 = list(reversed(self.variables))
        
        w1, _, _ = solve_csp_native(vars_1, constraints)
        w2, _, _ = solve_csp_native(vars_2, constraints)
        
        self.assertEqual(w1 is None, w2 is None)
        
    def test_r06_opaque_symbol_renaming(self):
        # Symbol renaming (e.g. x -> A, y -> B) preserves decision
        constraints = [
            {"id": "c1", "type": "coupling_membership", "variables": ["x", "y"]}
        ]
        renamed_vars = [
            {"name": "A", "domain": ["0", "1"]},
            {"name": "B", "domain": ["0", "1"]}
        ]
        renamed_constraints = [
            {"id": "c1", "type": "coupling_membership", "variables": ["A", "B"]}
        ]
        w1, _, _ = solve_csp_native(self.variables, constraints)
        w2, _, _ = solve_csp_native(renamed_vars, renamed_constraints)
        
        self.assertEqual(w1 is None, w2 is None)
        
    def test_r07_core_irreducibility(self):
        # Deleting any constraint from the core makes the remaining set satisfiable
        constraints = [
            {"id": "c_triad", "type": "triad_closure", "variables": ["x", "y", "z"]},
            {"id": "c_x", "type": "projection_membership", "variables": ["x"], "parameters": {"allowed_values": ["1"]}},
            {"id": "c_y", "type": "projection_membership", "variables": ["y"], "parameters": {"allowed_values": ["1"]}},
            {"id": "c_z", "type": "projection_membership", "variables": ["z"], "parameters": {"allowed_values": ["0"]}}
        ]
        
        core, core_type, verified = extract_unsatisfied_core(self.variables, constraints)
        self.assertTrue(verified)
        self.assertEqual(core_type, "subset_minimal")
        
        # Test irreducibility: remove any constraint in the core and check SAT
        for c_id in core:
            reduced = [c for c in constraints if c["id"] != c_id and c["id"] in core]
            witness, _, complete = solve_csp_native(self.variables, reduced)
            self.assertTrue(complete)
            self.assertIsNotNone(witness) # Should be satisfiable now
            
    def test_r08_nonminimum_core_fixture(self):
        # Core type is reported as subset_minimal
        constraints = [
            {"id": "c_triad", "type": "triad_closure", "variables": ["x", "y", "z"]},
            {"id": "c_x", "type": "projection_membership", "variables": ["x"], "parameters": {"allowed_values": ["1"]}},
            {"id": "c_y", "type": "projection_membership", "variables": ["y"], "parameters": {"allowed_values": ["1"]}},
            {"id": "c_z", "type": "projection_membership", "variables": ["z"], "parameters": {"allowed_values": ["0"]}}
        ]
        _, core_type, _ = extract_unsatisfied_core(self.variables, constraints)
        self.assertEqual(core_type, "subset_minimal")
        
    def test_r09_invalid_composition_typing(self):
        # Invalid composition domains must be rejected
        c = {
            "id": "c1",
            "type": "composition",
            "variables": ["x", "y", "z"],
            "parameters": {
                "domain": ["A", "B"],
                "codomain": ["C", "D"]
            }
        }
        # x is "0" which is not in domain ["A", "B"], so satisfies_constraint must return False
        self.assertFalse(satisfies_constraint({"x": "0", "y": "C", "z": "R"}, c))
        # Check that x="A" (in domain) and y="C" (in codomain) is allowed
        self.assertTrue(satisfies_constraint({"x": "A", "y": "C", "z": "R"}, c))
        # Check that x="C" (not in domain but in codomain) is rejected
        self.assertFalse(satisfies_constraint({"x": "C", "y": "C", "z": "R"}, c))
        
    def test_r10_bound_exhaustion_indeterminate(self):
        # Restricting max nodes must return complete=False (INDETERMINATE)
        constraints = [
            {"id": "c_triad", "type": "triad_closure", "variables": ["x", "y", "z"]}
        ]
        witness, _, complete = solve_csp_native(self.variables, constraints, max_nodes=1)
        self.assertFalse(complete)
        self.assertIsNone(witness)

if __name__ == "__main__":
    unittest.main()
