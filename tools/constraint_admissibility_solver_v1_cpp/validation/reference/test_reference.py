import unittest
import json
import os
import subprocess

class TestReference(unittest.TestCase):
    def setUp(self):
        # Create temporary directories and test configs
        os.makedirs("outputs", exist_ok=True)
        self.input_file = "outputs/temp_solver_input.json"
        self.output_file = "outputs/temp_solver_output.json"
        
    def tearDown(self):
        if os.path.exists(self.input_file):
            os.remove(self.input_file)
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
            
    def test_satisfiable_run(self):
        config = {
            "variables": [
                {"name": "x", "domain": ["A", "B"]},
                {"name": "y", "domain": ["B", "C"]}
            ],
            "constraints": [
                {
                    "id": "c1",
                    "type": "coupling_membership",
                    "variables": ["x", "y"],
                    "parameters": {"allowed_pairs": [["A", "B"], ["B", "C"]]}
                }
            ]
        }
        
        with open(self.input_file, "w") as f:
            json.dump(config, f)
            
        cmd = [".venv/Scripts/python.exe", "tools/constraint_admissibility_solver_v1_cpp/sim_governed.py",
               "--input", self.input_file, "--output", self.output_file]
               
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        
        with open(self.output_file, "r") as f:
            out_data = json.load(f)
            
        self.assertEqual(out_data["decision"], "SAT")
        self.assertEqual(out_data["witness_assignment"]["x"], "A")
        self.assertEqual(out_data["witness_assignment"]["y"], "B")
        
    def test_indeterminate_run(self):
        config = {
            "variables": [
                {"name": "x", "domain": ["A", "B", "C", "D"]},
                {"name": "y", "domain": ["A", "B", "C", "D"]}
            ],
            "constraints": [
                {
                    "id": "c1",
                    "type": "coupling_membership",
                    "variables": ["x", "y"],
                    "parameters": {"allowed_pairs": []}
                }
            ]
        }
        with open(self.input_file, "w") as f:
            json.dump(config, f)
            
        cmd = [".venv/Scripts/python.exe", "tools/constraint_admissibility_solver_v1_cpp/sim_governed.py",
               "--input", self.input_file, "--output", self.output_file, "--max-nodes", "1"]
               
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        
        with open(self.output_file, "r") as f:
            out_data = json.load(f)
            
        self.assertEqual(out_data["decision"], "INDETERMINATE")

if __name__ == "__main__":
    unittest.main()
