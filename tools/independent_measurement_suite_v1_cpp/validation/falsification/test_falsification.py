import unittest
from tools.independent_measurement_suite_v1_cpp.sim_governed import check_leakage

class TestFalsification(unittest.TestCase):
    def test_clean_input_passes(self):
        # A clean input dict with no keywords should pass
        clean_input = {
            "sample_a": {"data": [1, 2, 3]},
            "sample_b": {"data": [4, 5, 6]},
            "metadata": {"session": "blind_run_01"}
        }
        try:
            check_leakage(clean_input)
        except ValueError:
            self.fail("check_leakage raised ValueError unexpectedly on clean input.")
            
    def test_leakage_rejection(self):
        # Inputs with forbidden keywords should raise ValueError
        dirty_inputs = [
            {"sample_a": {"data": [1, 2]}, "metadata": {"model_name": "RT"}},
            {"sample_a": {"data": [1, 2]}, "metadata": {"operator": "mono_process"}}, # Wait, ⇔_r is not directly in the list, but let's check
            {"sample_a": {"data": [1, 2]}, "metadata": {"expected": "mono-process"}},
            {"sample_a": {"data": [1, 2]}, "metadata": {"verdict": "falsification"}}
        ]
        for dirty in dirty_inputs:
            with self.assertRaises(ValueError):
                check_leakage(dirty)

if __name__ == "__main__":
    unittest.main()
