import unittest
import numpy as np
from tools.independent_measurement_suite_v1_cpp.sim_governed import (
    calculate_ks_distance, run_bootstrap_ci
)

class TestNumerical(unittest.TestCase):
    def test_seed_sensitivity(self):
        # Setting different seeds should produce different bootstrap CIs but close value bounds
        np.random.seed(1)
        a = np.random.normal(0, 1, 100)
        b = np.random.normal(1, 1, 100)
        
        np.random.seed(42)
        ci_1 = run_bootstrap_ci(a, b, num_iterations=50)
        
        np.random.seed(100)
        ci_2 = run_bootstrap_ci(a, b, num_iterations=50)
        
        self.assertNotEqual(ci_1, ci_2)
        self.assertLess(abs(ci_1[0] - ci_2[0]), 0.1) # bounded error
        
    def test_precision_sensitivity(self):
        # float32 vs float64 should be very close
        np.random.seed(42)
        a_f64 = np.random.normal(0, 1, 100)
        b_f64 = np.random.normal(0.5, 1, 100)
        
        a_f32 = a_f64.astype(np.float32)
        b_f32 = b_f64.astype(np.float32)
        
        ks_64 = calculate_ks_distance(a_f64, b_f64)
        ks_32 = calculate_ks_distance(a_f32, b_f32)
        
        self.assertAlmostEqual(ks_64, ks_32, places=6)
        
    def test_bootstrap_convergence(self):
        # Confidence interval width should decrease as sample size N increases
        np.random.seed(42)
        
        # Small sample size N=10
        a_small = np.random.normal(0, 1, 15)
        b_small = np.random.normal(1, 1, 15)
        ci_small = run_bootstrap_ci(a_small, b_small, num_iterations=100)
        width_small = ci_small[1] - ci_small[0]
        
        # Large sample size N=150
        a_large = np.random.normal(0, 1, 150)
        b_large = np.random.normal(1, 1, 150)
        ci_large = run_bootstrap_ci(a_large, b_large, num_iterations=100)
        width_large = ci_large[1] - ci_large[0]
        
        # CI width should shrink
        self.assertLess(width_large, width_small)

if __name__ == "__main__":
    unittest.main()
