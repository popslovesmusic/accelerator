import unittest
import json
import itertools
from tools.constraint_admissibility_solver_v1_cpp.sim_governed import satisfies_constraint
from tools.constraint_admissibility_solver_v1_cpp.validation.independence.pysat_encoder import PySatEncoder

class TestNativeCnfExhaustiveEquivalence(unittest.TestCase):
    def test_triad_equivalence(self):
        variables = [
            {"name": "e12", "domain": ["0", "1"]},
            {"name": "e23", "domain": ["0", "1"]},
            {"name": "e31", "domain": ["0", "1"]}
        ]
        
        constraint = {
            "id": "c_triad",
            "type": "triad_closure",
            "variables": ["e12", "e23", "e31"]
        }
        
        encoder = PySatEncoder(variables, [constraint])
        
        # Enumerate all 2^3 = 8 assignments
        for v12 in ["0", "1"]:
            for v23 in ["0", "1"]:
                for v31 in ["0", "1"]:
                    assignment = {"e12": v12, "e23": v23, "e31": v31}
                    
                    # 1. Native evaluation
                    native_ok = satisfies_constraint(assignment, constraint)
                    
                    # 2. CNF clause satisfaction check
                    # Build CNF assignment (each literal is True/False)
                    lit_assignment = {}
                    for (var_name, val), lit in encoder.var_val_to_lit.items():
                        lit_assignment[lit] = (assignment[var_name] == val)
                        
                    cnf_ok = True
                    for clause in encoder.clauses:
                        clause_satisfied = False
                        for lit in clause:
                            if lit > 0:
                                if lit_assignment[lit]:
                                    clause_satisfied = True
                                    break
                            else:
                                if not lit_assignment[-lit]:
                                    clause_satisfied = True
                                    break
                        if not clause_satisfied:
                            cnf_ok = False
                            break
                            
                    # They must agree exactly
                    self.assertEqual(native_ok, cnf_ok, f"Disagreement on assignment: {assignment}")
                    
    def test_coupling_equivalence(self):
        variables = [
            {"name": "x", "domain": ["A", "B", "C"]},
            {"name": "y", "domain": ["A", "B", "C"]}
        ]
        
        constraint = {
            "id": "c1",
            "type": "coupling_membership",
            "variables": ["x", "y"],
            "parameters": {"allowed_pairs": [["A", "A"], ["B", "C"]]}
        }
        
        encoder = PySatEncoder(variables, [constraint])
        
        for vx in ["A", "B", "C"]:
            for vy in ["A", "B", "C"]:
                assignment = {"x": vx, "y": vy}
                native_ok = satisfies_constraint(assignment, constraint)
                
                # CNF clause satisfaction check
                lit_assignment = {}
                for (var_name, val), lit in encoder.var_val_to_lit.items():
                    lit_assignment[lit] = (assignment[var_name] == val)
                    
                cnf_ok = True
                for clause in encoder.clauses:
                    clause_satisfied = False
                    for lit in clause:
                        if lit > 0:
                            if lit_assignment[lit]:
                                clause_satisfied = True
                                break
                        else:
                            if not lit_assignment[-lit]:
                                clause_satisfied = True
                                break
                    if not clause_satisfied:
                        cnf_ok = False
                        break
                        
                self.assertEqual(native_ok, cnf_ok, f"Disagreement on coupling: {assignment}")

if __name__ == "__main__":
    unittest.main()
