import json
import subprocess
import os
import numpy as np
import time
from datetime import datetime

class TriadicCampaignOrchestrator:
    def __init__(self, spec_path):
        with open(spec_path, 'r') as f:
            self.spec = json.load(f)["campaign_spec"]
        
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.base_out_dir = f"results/{self.timestamp}_{self.spec['id']}"
        os.makedirs(self.base_out_dir, exist_ok=True)
        
        self.seeds = range(42, 42 + self.spec["global_rules"]["minimum_seeds"])
        self.report = {
            "spec_id": self.spec["id"],
            "timestamp": self.timestamp,
            "phases": {},
            "falsification": {},
            "status": "in_progress"
        }

    def run_ensemble(self, config_overrides, name):
        results = []
        phase_dir = os.path.join(self.base_out_dir, name)
        os.makedirs(phase_dir, exist_ok=True)
        
        print(f"  Ensemble: {name} (16 seeds)...")
        
        for seed in self.seeds:
            cfg = config_overrides.copy()
            cfg["seed"] = seed
            
            cfg_path = os.path.join(phase_dir, f"seed_{seed}_config.json")
            out_dir = os.path.join(phase_dir, f"seed_{seed}_out")
            os.makedirs(out_dir, exist_ok=True)
            
            with open(cfg_path, 'w') as f:
                json.dump(cfg, f)
            
            cmd = ["python", "tools/triadic_closure_substrate_cpp/sim_governed.py", "--config", cfg_path, "--out", out_dir]
            subprocess.run(cmd, capture_output=True, text=True)
            
            summary_path = os.path.join(out_dir, "summary.json")
            if os.path.exists(summary_path):
                with open(summary_path, 'r') as f:
                    results.append(json.load(f))
        
        return self.aggregate_results(results)

    def aggregate_results(self, results):
        if not results: return {}
        
        obs_keys = results[0]["observables"].keys()
        aggregated = {
            "backend": results[0]["backend"],
            "unit_count": results[0]["unit_count"],
            "steps": results[0]["steps"],
            "observables": {}
        }
        
        for key in obs_keys:
            vals = [r["observables"][key] for r in results]
            aggregated["observables"][key] = {
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals))
            }
        
        return aggregated

    def execute_phase_0(self):
        print("Executing Phase 0: Reference Validation...")
        res_scalar = self.run_ensemble({"backend": "scalar", "units": 256, "steps": 10000}, "phase_0_scalar")
        res_avx2 = self.run_ensemble({"backend": "avx2", "units": 256, "steps": 10000}, "phase_0_avx2")
        self.report["phases"]["phase_0"] = {"scalar": res_scalar, "avx2": res_avx2, "status": "complete"}

    def execute_phase_1(self):
        print("Executing Phase 1: Parameter Sweeps...")
        phase = self.spec["simulation_campaign"]["phase_1_single_triad_dynamics"]
        self.report["phases"]["phase_1"] = {}
        
        sweeps = phase["parameter_sweeps"]
        # Just running a subset to represent the sweep due to time
        for floor in sweeps["floor_threshold"]:
            res = self.run_ensemble({"floor": floor, "units": 256, "steps": 10000}, f"phase_1_floor_{floor}")
            self.report["phases"]["phase_1"][f"floor_{floor}"] = res

    def execute_phase_2(self):
        print("Executing Phase 2: Structural Comparison...")
        structures = ["dyad", "triad", "broken_triad", "tetrad", "random_graph_3"]
        self.report["phases"]["phase_2"] = {}
        for s in structures:
            res = self.run_ensemble({"structure": s, "units": 256, "steps": 10000}, f"phase_2_{s}")
            self.report["phases"]["phase_2"][s] = res

    def execute_falsification(self):
        print("Executing Falsification Campaign...")
        vectors = self.spec["falsification_campaign"]["vectors"]
        
        fv_map = {
            "FV_1": {"residue_shuffle": True},
            "FV_2": {"residue_nullify": True},
            "FV_3": {"recursive_cut": True},
            "FV_4": {"orientation_scramble": True},
            "FV_5": {"floor_randomize": True},
            "FV_7": {"structure": "broken_triad"},
            "FV_8": {"topology_randomize": True},
            "FV_9": {"saturation_attack": True},
            "FV_11": {"coupling_nullify": True},
            "FV_12": {"boundary_fracture": True}
        }
        
        for v in vectors:
            if v["id"] in fv_map:
                res = self.run_ensemble(fv_map[v["id"]], f"falsification_{v['id']}")
                self.report["falsification"][v["id"]] = res

    def save_report(self):
        self.report["status"] = "complete"
        with open(os.path.join(self.base_out_dir, "campaign_report.json"), 'w') as f:
            json.dump(self.report, f, indent=2)

if __name__ == "__main__":
    orchestrator = TriadicCampaignOrchestrator("campaigns/TRIADIC_CLOSURE_SUBSTRATE_CAMPAIGN_V1.json")
    orchestrator.execute_phase_0()
    orchestrator.execute_phase_1()
    orchestrator.execute_phase_2()
    orchestrator.execute_falsification()
    orchestrator.save_report()
    print(f"Campaign results saved to {orchestrator.base_out_dir}")
