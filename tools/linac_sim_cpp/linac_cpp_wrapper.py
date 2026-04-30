import os
import subprocess
import json
import pandas as pd
import numpy as np

class LinacEngineCPP:
    def __init__(self, binary_path="linac_sim_cpp/linac_sim_benchmark.exe"):
        self.binary_path = binary_path

    def run_benchmark(self):
        """Runs the built-in benchmark and returns the precision report."""
        subprocess.run([self.binary_path], check=True)
        report_path = "linac_sim_cpp/outputs/v2p3_precision_report.json"
        if os.path.exists(report_path):
            with open(report_path, "r") as f:
                return json.load(f)
        return None

    def run_simulation(self, config):
        """
        Future: Run arbitrary configs by passing them to a CLI-version of the C++ engine.
        For now, we have the benchmark.
        """
        # Save config to temp file
        config_path = "linac_sim_cpp/configs/last_run.json"
        with open(config_path, "w") as f:
            json.dump(config, f)
        
        # In a real implementation, we'd call the binary with --config config_path
        # subprocess.run([self.binary_path, "--config", config_path])
        pass

if __name__ == "__main__":
    engine = LinacEngineCPP()
    report = engine.run_benchmark()
    if report:
        print("C++ Engine Precision Report:")
        print(json.dumps(report, indent=4))
