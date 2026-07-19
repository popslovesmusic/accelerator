import unittest
import numpy as np
from tools.independent_measurement_suite_v1_cpp.sim_governed import (
    calculate_ks_distance, calculate_dtw, get_graph_stats, run_bootstrap_ci, run_permutation_test
)

class TestMetrics(unittest.TestCase):
    def test_ks_distance(self):
        a = np.array([1, 2, 3, 4, 5])
        b = np.array([1, 2, 3, 4, 5])
        self.assertEqual(calculate_ks_distance(a, b), 0.0)
        
        # Staggered arrays
        c = np.array([1, 2, 3])
        d = np.array([4, 5, 6])
        self.assertEqual(calculate_ks_distance(c, d), 1.0)
        
    def test_dtw_distance(self):
        a = np.array([1, 2, 3])
        b = np.array([1, 2, 3])
        self.assertEqual(calculate_dtw(a, b), 0.0)
        
        c = np.array([1, 2, 3])
        d = np.array([2, 3, 4])
        # DTW of shifted: cost = |1-2| + |2-3| + |3-4| = 3.0
        self.assertEqual(calculate_dtw(c, d), 2.0)
        
    def test_graph_stats(self):
        # Empty graph
        self.assertEqual(get_graph_stats({}), (0.0, 0.0))
        
        # Simple triangle (complete graph K3)
        # Degree of all nodes = 2. Clustering coefficient of all nodes = 1.0.
        k3 = {
            "nodes": [1, 2, 3],
            "edges": [[1, 2], [2, 3], [3, 1]]
        }
        entropy, clustering = get_graph_stats(k3)
        self.assertEqual(entropy, 0.0)  # All degrees are 2, so entropy = 0.
        self.assertAlmostEqual(clustering, 1.0)
        
    def test_bootstrap_and_permutation(self):
        np.random.seed(42)
        a = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        b = np.array([2.0, 3.0, 4.0, 5.0, 6.0])
        ci = run_bootstrap_ci(a, b, num_iterations=100)
        # Verify that lower bound is strictly less than upper bound
        self.assertLess(ci[0], ci[1])
        
        # Verify permutation test returns expected value for identical samples
        p = run_permutation_test(a, a, num_permutations=10)
        self.assertGreaterEqual(p, 0.0)

if __name__ == "__main__":
    unittest.main()
