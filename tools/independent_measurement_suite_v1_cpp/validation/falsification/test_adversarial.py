import unittest
import numpy as np
import subprocess
import os
import json
from tools.independent_measurement_suite_v1_cpp.sim_governed import (
    calculate_ks_distance, calculate_dtw
)

class TestAdversarial(unittest.TestCase):
    def test_empty_or_nan_data(self):
        # Empty arrays should return 0 distance
        self.assertEqual(calculate_ks_distance(np.array([]), np.array([])), 0.0)
        self.assertEqual(calculate_dtw(np.array([]), np.array([])), 0.0)
        
    def test_adversarial_cli_misuse(self):
        # Verify that running with a non-existent input file produces a non-zero exit code
        cmd = [".venv/Scripts/python.exe", "tools/independent_measurement_suite_v1_cpp/sim_governed.py", 
               "--input", "non_existent_file.json", "--output", "outputs/temp_test_out.json"]
               
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        
    def test_adversarial_schema_violation(self):
        # Create a malformed config with invalid types
        malformed = {
            "sample_a": {
                "data": ["not_a_number", 2, 3] # String instead of number
            },
            "sample_b": {
                "data": [4, 5, 6]
            }
        }
        
        temp_input = "outputs/temp_malformed_input.json"
        temp_output = "outputs/temp_malformed_output.json"
        os.makedirs("outputs", exist_ok=True)
        
        with open(temp_input, "w") as f:
            json.dump(malformed, f)
            
        cmd = [".venv/Scripts/python.exe", "tools/independent_measurement_suite_v1_cpp/sim_governed.py", 
               "--input", temp_input, "--output", temp_output]
               
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up
        if os.path.exists(temp_input):
            os.remove(temp_input)
        if os.path.exists(temp_output):
            os.remove(temp_output)
            
        # The parser or script should fail or throw a TypeError
        self.assertNotEqual(result.returncode, 0)

if __name__ == "__main__":
    unittest.main()
