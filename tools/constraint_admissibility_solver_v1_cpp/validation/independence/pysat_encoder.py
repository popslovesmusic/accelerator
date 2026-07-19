import json
from pysat.solvers import Glucose3

class PySatEncoder:
    def __init__(self, variables, constraints):
        self.variables = variables
        self.constraints = constraints
        
        # Mapping (var_name, val) -> lit
        self.var_val_to_lit = {}
        self.lit_to_var_val = {}
        self.clauses = []
        
        self._build_variables()
        self._build_exactly_one()
        self._build_constraints()
        
    def _build_variables(self):
        lit_counter = 1
        for var in self.variables:
            var_name = var["name"]
            domain = var["domain"]
            for val in domain:
                self.var_val_to_lit[(var_name, val)] = lit_counter
                self.lit_to_var_val[lit_counter] = (var_name, val)
                lit_counter += 1
                
    def _build_exactly_one(self):
        for var in self.variables:
            var_name = var["name"]
            domain = var["domain"]
            
            # At least one value must be selected
            lits = [self.var_val_to_lit[(var_name, val)] for val in domain]
            self.clauses.append(lits)
            
            # At most one value can be selected
            for i in range(len(lits)):
                for j in range(i + 1, len(lits)):
                    self.clauses.append([-lits[i], -lits[j]])
                    
    def _build_constraints(self):
        for constraint in self.constraints:
            c_type = constraint["type"]
            vars_list = constraint["variables"]
            params = constraint.get("parameters", {})
            
            if c_type == "triad_closure":
                # Triad closure constraint on vars_list (typically 3 variables)
                # Violating case: 2 variables are active (!= "0"), and 1 variable is inactive ("0")
                # Active values for each variable
                v1, v2, v3 = vars_list[0], vars_list[1], vars_list[2]
                
                d1 = [val for val in self._get_domain(v1) if val != "0"]
                d2 = [val for val in self._get_domain(v2) if val != "0"]
                d3 = [val for val in self._get_domain(v3) if val != "0"]
                
                # Permutation 1: v1 active, v2 active, v3 inactive ("0")
                if "0" in self._get_domain(v3):
                    lit_v3_inactive = self.var_val_to_lit.get((v3, "0"))
                    for val1 in d1:
                        lit1 = self.var_val_to_lit.get((v1, val1))
                        for val2 in d2:
                            lit2 = self.var_val_to_lit.get((v2, val2))
                            if lit1 and lit2 and lit_v3_inactive:
                                self.clauses.append([-lit1, -lit2, -lit_v3_inactive])
                                
                # Permutation 2: v1 active, v3 active, v2 inactive ("0")
                if "0" in self._get_domain(v2):
                    lit_v2_inactive = self.var_val_to_lit.get((v2, "0"))
                    for val1 in d1:
                        lit1 = self.var_val_to_lit.get((v1, val1))
                        for val3 in d3:
                            lit3 = self.var_val_to_lit.get((v3, val3))
                            if lit1 and lit3 and lit_v2_inactive:
                                self.clauses.append([-lit1, -lit3, -lit_v2_inactive])
                                
                # Permutation 3: v2 active, v3 active, v1 inactive ("0")
                if "0" in self._get_domain(v1):
                    lit_v1_inactive = self.var_val_to_lit.get((v1, "0"))
                    for val2 in d2:
                        lit2 = self.var_val_to_lit.get((v2, val2))
                        for val3 in d3:
                            lit3 = self.var_val_to_lit.get((v3, val3))
                            if lit2 and lit3 and lit_v1_inactive:
                                self.clauses.append([-lit2, -lit3, -lit_v1_inactive])
                                
            elif c_type == "coupling_membership":
                v1, v2 = vars_list[0], vars_list[1]
                allowed_pairs = params.get("allowed_pairs", [])
                
                if allowed_pairs:
                    # If (val1, val2) is not in allowed_pairs, add constraint clause
                    # -lit1 v -lit2
                    for val1 in self._get_domain(v1):
                        lit1 = self.var_val_to_lit.get((v1, val1))
                        for val2 in self._get_domain(v2):
                            lit2 = self.var_val_to_lit.get((v2, val2))
                            if [val1, val2] not in allowed_pairs and list((val1, val2)) not in allowed_pairs:
                                if lit1 and lit2:
                                    self.clauses.append([-lit1, -lit2])
                else:
                    # Require v1 == v2
                    for val1 in self._get_domain(v1):
                        lit1 = self.var_val_to_lit.get((v1, val1))
                        if val1 in self._get_domain(v2):
                            lit2 = self.var_val_to_lit.get((v2, val1))
                            # lit1 -> lit2 and lit2 -> lit1
                            self.clauses.append([-lit1, lit2])
                            self.clauses.append([lit1, -lit2])
                        else:
                            # val1 cannot be chosen
                            self.clauses.append([-lit1])
                            
            elif c_type == "projection_membership":
                v1 = vars_list[0]
                allowed = params.get("allowed_values", [])
                for val1 in self._get_domain(v1):
                    if val1 not in allowed:
                        lit1 = self.var_val_to_lit.get((v1, val1))
                        if lit1:
                            self.clauses.append([-lit1])
                            
            elif c_type == "composition":
                v1, v2, v3 = vars_list[0], vars_list[1], vars_list[2]
                domain = params.get("domain", [])
                codomain = params.get("codomain", [])
                rules = params.get("rules", {})
                
                for val1 in self._get_domain(v1):
                    lit1 = self.var_val_to_lit.get((v1, val1))
                    if domain and val1 not in domain:
                        if lit1:
                            self.clauses.append([-lit1])
                        continue
                        
                    for val2 in self._get_domain(v2):
                        lit2 = self.var_val_to_lit.get((v2, val2))
                        if codomain and val2 not in codomain:
                            if lit2:
                                self.clauses.append([-lit2])
                            continue
                            
                        # Composition output
                        key = f"{val1}*{val2}"
                        expected_val3 = rules.get(key)
                        if expected_val3:
                            if expected_val3 in self._get_domain(v3):
                                lit3 = self.var_val_to_lit.get((v3, expected_val3))
                                if lit1 and lit2 and lit3:
                                    self.clauses.append([-lit1, -lit2, lit3])
                            else:
                                if lit1 and lit2:
                                    self.clauses.append([-lit1, -lit2])
                                    
    def _get_domain(self, var_name):
        for var in self.variables:
            if var["name"] == var_name:
                return var["domain"]
        return []
        
    def solve(self):
        g = Glucose3()
        for clause in self.clauses:
            g.add_clause(clause)
            
        success = g.solve()
        if success:
            model = g.get_model()
            witness = {}
            for lit in model:
                if lit > 0:
                    var_name, val = self.lit_to_var_val[lit]
                    witness[var_name] = val
            return "SAT", witness
        else:
            return "UNSAT", None
