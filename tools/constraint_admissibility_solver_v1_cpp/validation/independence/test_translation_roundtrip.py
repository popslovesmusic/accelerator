import unittest
from tools.constraint_admissibility_solver_v1_cpp.validation.independence.pysat_encoder import PySatEncoder

class TestTranslationRoundtrip(unittest.TestCase):
    def test_roundtrip_mapping(self):
        variables = [
            {"name": "x", "domain": ["A", "B", "C"]},
            {"name": "y", "domain": ["1", "2"]}
        ]
        
        encoder = PySatEncoder(variables, [])
        
        # Verify mapping consistency
        for (var_name, val), lit in encoder.var_val_to_lit.items():
            mapped_var, mapped_val = encoder.lit_to_var_val[lit]
            self.assertEqual(var_name, mapped_var)
            self.assertEqual(val, mapped_val)
            
        # Verify variable counts match total domain sizes
        self.assertEqual(len(encoder.var_val_to_lit), 5) # 3 + 2 = 5

if __name__ == "__main__":
    unittest.main()
