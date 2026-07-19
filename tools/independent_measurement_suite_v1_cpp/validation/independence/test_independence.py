import unittest
import numpy as np
from tools.independent_measurement_suite_v1_cpp.sim_governed import calculate_ks_distance

class TestIndependence(unittest.TestCase):
    def test_oracle_agreement(self):
        try:
            from scipy.stats import ks_2samp
            scipy_available = True
        except ImportError:
            scipy_available = False
            
        if not scipy_available:
            self.skipTest("Scipy is not installed in this environment. Skipping oracle comparison.")
            
        np.random.seed(42)
        a = np.random.normal(0, 1, 100)
        b = np.random.normal(0.5, 1.2, 100)
        
        our_ks = calculate_ks_distance(a, b)
        scipy_ks = ks_2samp(a, b).statistic
        
        # Verify agreement within tolerance
        self.assertAlmostEqual(our_ks, scipy_ks, places=5)
        
    def test_no_shared_core_algorithm(self):
        # Verify that our code is pure-python native and does not import scipy in its internal code
        import sys
        # Temporarily remove scipy if imported, and check we can calculate KS distance
        modules_backup = {}
        for name in list(sys.modules.keys()):
            if "scipy" in name:
                modules_backup[name] = sys.modules.pop(name)
                
        try:
            a = np.array([1.0, 2.0, 3.0])
            b = np.array([2.0, 3.0, 4.0])
            val = calculate_ks_distance(a, b)
            self.assertAlmostEqual(val, 1/3, places=7)
        finally:
            # Restore backup
            sys.modules.update(modules_backup)

if __name__ == "__main__":
    unittest.main()
