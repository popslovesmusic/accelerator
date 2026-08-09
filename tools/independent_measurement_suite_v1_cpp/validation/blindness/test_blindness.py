import unittest
import numpy as np
import json
import copy
from tools.independent_measurement_suite_v1_cpp.sim_governed import (
    calculate_ks_distance, get_graph_stats
)

class TestBlindness(unittest.TestCase):
    def test_blindness_invariance(self):
        # Construct original input sample
        original = {
            "sample_a": {
                "data": [1.0, 2.0, 3.0, 4.0, 5.0],
                "graph": {
                    "nodes": ["A", "B", "C"],
                    "edges": [["A", "B"], ["B", "C"]]
                }
            },
            "sample_b": {
                "data": [2.0, 3.0, 4.0, 5.0, 6.0],
                "graph": {
                    "nodes": ["A", "B", "C"],
                    "edges": [["B", "C"]]
                }
            },
            "metadata": {
                "model_name": "unknown_model",
                "campaign_verdict": "active"
            }
        }
        
        # Calculate original statistics
        orig_ks = calculate_ks_distance(original["sample_a"]["data"], original["sample_b"]["data"])
        orig_ent_a, orig_clust_a = get_graph_stats(original["sample_a"]["graph"])
        orig_ent_b, orig_clust_b = get_graph_stats(original["sample_b"]["graph"])
        
        # Attack A: Permute node labels in graphs (A -> X, B -> Y, C -> Z)
        modified = copy.deepcopy(original)
        modified["sample_a"]["graph"]["nodes"] = ["X", "Y", "Z"]
        modified["sample_a"]["graph"]["edges"] = [["X", "Y"], ["Y", "Z"]]
        modified["sample_b"]["graph"]["nodes"] = ["X", "Y", "Z"]
        modified["sample_b"]["graph"]["edges"] = [["Y", "Z"]]
        
        # Shuffled keys and dictionaries
        # (Since JSON loading shuffles key orders when keys are hashed, we can represent it by sorting or reversing dict keys)
        # Verify metric invariance
        mod_ks = calculate_ks_distance(modified["sample_a"]["data"], modified["sample_b"]["data"])
        mod_ent_a, mod_clust_a = get_graph_stats(modified["sample_a"]["graph"])
        mod_ent_b, mod_clust_b = get_graph_stats(modified["sample_b"]["graph"])
        
        self.assertEqual(orig_ks, mod_ks)
        self.assertEqual(orig_ent_a, mod_ent_a)
        self.assertEqual(orig_clust_a, mod_clust_a)
        self.assertEqual(orig_ent_b, mod_ent_b)
        self.assertEqual(orig_clust_b, mod_clust_b)

if __name__ == "__main__":
    unittest.main()
