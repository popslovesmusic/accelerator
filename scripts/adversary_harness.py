import os
import json
import subprocess
import argparse
import time
import numpy as np
from pathlib import Path
from datetime import datetime

class AdversaryHarness:
    def __init__(self, root_dir="."):
        self.root = Path(root_dir)
        self.manifest_path = self.root / "registry/tool_manifest.json"
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            self.manifest = json.load(f)

    def run_command(self, cmd, out_dir):
        print(f"  [EXEC] {' '.join(cmd)}")
        out_dir.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [ERROR] {result.stderr}")
        return result.returncode == 0, result.stdout

    def execute_micro_attack_suite(self, tool_name, original_config, base_out_dir):
        """
        Executes the mandatory Micro-Attack Suite (Mandated by Falsification Runtime Policy).
        """
        print(f"\n[ADVERSARY] Commencing Micro-Attack Suite for {tool_name}...")
        
        attack_results = {}
        
        # 1. Zero Mismatch Probe (Baseline Sensitivity)
        # Attempt to find a 'coupling' or 'strength' parameter to nullify
        print("  [VECTOR] FV-1: Zero Mismatch Probe...")
        fv1_config = original_config.copy()
        null_params = ["K", "source_strength", "reinforcement_rate", "P_re"]
        nullified = False
        for p in null_params:
            if p in fv1_config:
                fv1_config[p] = 0.0
                nullified = True
        
        if nullified:
            fv1_dir = base_out_dir / "adversary/fv1_zero_probe"
            fv1_cfg_path = fv1_dir / "config.json"
            fv1_dir.mkdir(parents=True, exist_ok=True)
            with open(fv1_cfg_path, 'w') as f: json.dump(fv1_config, f)
            
            cmd = ["python", f"tools/{tool_name}/sim_governed.py", "--config", str(fv1_cfg_path), "--out", str(fv1_dir)]
            success, _ = self.run_command(cmd, fv1_dir)
            
            if success and (fv1_dir / "summary.json").exists():
                with open(fv1_dir / "summary.json") as f:
                    metrics = json.load(f).get("final_metrics", {})
                    # Expect failure (low order parameter or active fraction)
                    op = metrics.get("order_parameter", metrics.get("active_fraction", 1.0))
                    attack_results["FV-1_zero_mismatch"] = "passed" if op < 0.1 else "failed"
            else:
                attack_results["FV-1_zero_mismatch"] = "error"
        else:
            attack_results["FV-1_zero_mismatch"] = "skipped_no_target_param"

        # 2. Seed Variance Check (Stability)
        print("  [VECTOR] FV-2: Seed Variance Check (3 seeds)...")
        seeds = [101, 202, 303]
        seed_metrics = []
        for s in seeds:
            fv2_config = original_config.copy()
            fv2_config["seed"] = s
            fv2_dir = base_out_dir / f"adversary/fv2_seed_{s}"
            fv2_cfg_path = fv2_dir / "config.json"
            fv2_dir.mkdir(parents=True, exist_ok=True)
            with open(fv2_cfg_path, 'w') as f: json.dump(fv2_config, f)
            
            cmd = ["python", f"tools/{tool_name}/sim_governed.py", "--config", str(fv2_cfg_path), "--out", str(fv2_dir)]
            success, _ = self.run_command(cmd, fv2_dir)
            if success and (fv2_dir / "summary.json").exists():
                with open(fv2_dir / "summary.json") as f:
                    seed_metrics.append(json.load(f).get("final_metrics", {}))

        if len(seed_metrics) > 0:
            # Check for high variance in primary metric
            key = "order_parameter" if "order_parameter" in seed_metrics[0] else "active_fraction"
            vals = [m.get(key, 0) for m in seed_metrics]
            std = np.std(vals)
            attack_results["FV-2_seed_variance"] = "passed" if std < 0.1 else f"warning_high_variance_{std:.4f}"
            uncertainty = {
                "metric": key,
                "mean": float(np.mean(vals)),
                "std": float(std),
                "samples": len(vals)
            }
        else:
            attack_results["FV-2_seed_variance"] = "error"
            uncertainty = {}

        return attack_results, uncertainty

    def run_protected_sim(self, tool_name, config_path, out_dir):
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'r') as f:
            config = json.load(f)

        # 1. Execute Standard Run
        print(f"\n[HARNESS] Executing Standard Run for {tool_name}...")
        std_dir = out_dir / "standard"
        cmd = ["python", f"tools/{tool_name}/sim_governed.py", "--config", str(config_path), "--out", str(std_dir)]
        success, _ = self.run_command(cmd, std_dir)
        
        if not success:
            print("[HARNESS] Standard run failed. Aborting protected cycle.")
            return False

        # 2. Execute Adversary Suite
        falsification, uncertainty = self.execute_micro_attack_suite(tool_name, config, out_dir)

        # 3. Finalize Shadow Reports
        print("\n[HARNESS] Finalizing Shadow Reports...")
        shadow_dir = out_dir / "artifacts"
        shadow_dir.mkdir(exist_ok=True)
        
        reports = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "harness_version": "1.0.0"
            },
            "falsification_report": falsification,
            "uncertainty_report": uncertainty
        }
        
        with open(shadow_dir / "shadow_report.json", 'w') as f:
            json.dump(reports, f, indent=4)
        
        # Link main summary to shadow report
        if (std_dir / "summary.json").exists():
            with open(std_dir / "summary.json", 'r') as f:
                std_summary = json.load(f)
            std_summary["adversary_protected"] = True
            std_summary["shadow_report_path"] = "artifacts/shadow_report.json"
            with open(out_dir / "summary.json", 'w') as f:
                json.dump(std_summary, f, indent=4)

        print(f"[SUCCESS] Protected run complete. Results in {out_dir}")
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adversary Harness for Protected Simulations")
    parser.add_argument("--tool", required=True, help="Tool name (folder in tools/)")
    parser.add_argument("--config", required=True, help="Path to config JSON")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()
    
    harness = AdversaryHarness()
    harness.run_protected_sim(args.tool, args.config, args.out)
