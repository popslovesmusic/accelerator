import json
import subprocess
import os
import numpy as np
from datetime import datetime

class GravityCurvatureOrchestrator:
    def __init__(self, spec_path):
        with open(spec_path, 'r') as f:
            self.spec = json.load(f)["campaign_spec"]
        
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.base_out_dir = f"results/{self.timestamp}_{self.spec['id']}"
        os.makedirs(self.base_out_dir, exist_ok=True)
        
        self.seeds = range(42, 42 + 8) # Using 8 seeds for representativeness in this run
        self.report = {
            "spec_id": self.spec["id"],
            "timestamp": self.timestamp,
            "results": {},
            "falsification": {},
            "status": "in_progress"
        }

    def run_ensemble(self, config_overrides, name):
        results = []
        phase_dir = os.path.join(self.base_out_dir, name)
        os.makedirs(phase_dir, exist_ok=True)
        
        print(f"  Ensemble: {name} ({len(self.seeds)} seeds)...")
        
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
        aggregated = {"backend": results[0]["backend"], "unit_count": results[0]["unit_count"], "steps": results[0]["steps"], "observables": {}}
        for key in obs_keys:
            vals = [r["observables"][key] for r in results]
            aggregated["observables"][key] = {"mean": float(np.mean(vals)), "std": float(np.std(vals))}
        return aggregated

    def execute(self):
        print(f"Executing Campaign: {self.spec['id']}...")
        
        # Phase 1: Local Curvature Baseline
        print("Phase 1: Local Curvature Baseline...")
        self.report["results"]["Phase_1_Baseline"] = self.run_ensemble({"units": 1024, "steps": 5000, "probe_count": 500}, "Phase_1_Baseline")
        
        # Falsification Campaign
        print("Executing Falsification Campaign...")
        fv_configs = {
            "FV_20": {"residue_nullify": True},
            "FV_21": {"orientation_scramble": True},
            "FV_22": {"flatten_cost_gradients": True},
            "FV_24": {"force_boundary_symmetry": True},
            "FV_25": {"coupling_nullify": True}
        }
        
        for fvid, overrides in fv_configs.items():
            print(f"  {fvid}...")
            self.report["falsification"][fvid] = self.run_ensemble({"units": 1024, "steps": 5000, "probe_count": 500, **overrides}, fvid)

    def save_report(self):
        self.report["status"] = "complete"
        with open(os.path.join(self.base_out_dir, "campaign_report.json"), 'w') as f:
            json.dump(self.report, f, indent=2)

if __name__ == "__main__":
    orchestrator = GravityCurvatureOrchestrator("departments/analysis/campaigns/archives/legacy_research_campaigns/GRAVITY_APP_RELATIONAL_CURVATURE_CAMPAIGN_V1.json")
    orchestrator.execute()
    orchestrator.save_report()
    print(f"Campaign results saved to {orchestrator.base_out_dir}")
