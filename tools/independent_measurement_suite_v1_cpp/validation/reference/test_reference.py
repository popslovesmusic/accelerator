import unittest
import numpy as np
from tools.independent_measurement_suite_v1_cpp.sim_governed import (
    calculate_ks_distance, run_permutation_test
)

class TestReference(unittest.TestCase):
    def test_negative_control_identical(self):
        np.random.seed(42)
        # Identical normal distributions should have low KS distance and large p-values (not significant)
        a = np.random.normal(0, 1, 100)
        b = np.random.normal(0, 1, 100)
        ks = calculate_ks_distance(a, b)
        p_val = run_permutation_test(a, b, num_permutations=100)
        
        self.assertLess(ks, 0.3)
        self.assertGreater(p_val, 0.05) # non-significant
        
    def test_positive_control_separated(self):
        np.random.seed(42)
        # Completely separated distributions should have large KS distance and small p-values (significant)
        a = np.random.normal(0, 1, 100)
        b = np.random.normal(10, 1, 100)
        ks = calculate_ks_distance(a, b)
        p_val = run_permutation_test(a, b, num_permutations=100)
        
        self.assertGreater(ks, 0.8)
        self.assertLess(p_val, 0.05) # significant

if __name__ == "__main__":
    unittest.main()
