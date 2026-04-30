import argparse
import json
import os
import copy
from pathlib import Path
import sys

# Add current dir to sys.path to import from multi_sim_runner if needed
sys.path.append(os.getcwd())
from scripts.multi_sim_runner import MultiSimRunner, log

def run_convergence_sweep(tool_name, base_config_path, sweep_param, sweep_values, run_id):
    log(f"Starting convergence sweep for {tool_name} on {sweep_param}")
    
    with open(base_config_path, 'r') as f:
        base_config = json.load(f)
        
    output_root = Path(f"outputs/convergence_{run_id}")
    output_root.mkdir(parents=True, exist_ok=True)
    
    # Generate multi-run config
    multi_config = {
        "run_id": f"conv_{run_id}",
        "mode": "serial",
        "output_root": str(output_root),
        "governance": {
            "dry_run_first": False,
            "stop_on_failure": True
        },
        "jobs": []
    }
    
    temp_configs_dir = output_root / "configs"
    temp_configs_dir.mkdir(exist_ok=True)
    
    for i, val in enumerate(sweep_values):
        job_config = copy.deepcopy(base_config)
        job_config[sweep_param] = val
        
        config_path = temp_configs_dir / f"config_{i}.json"
        with open(config_path, 'w') as f:
            json.dump(job_config, f, indent=2)
            
        multi_config["jobs"].append({
            "job_id": f"sweep_{i}",
            "tool": tool_name,
            "config": str(config_path),
            "claim_role": "evidence_generation",
            "sweep_val": val # store here instead of 'args'
        })
        
    multi_config_path = output_root / "multi_run_sweep.json"
    with open(multi_config_path, 'w') as f:
        json.dump(multi_config, f, indent=2)
        
    job_to_val = {f"sweep_{i}": val for i, val in enumerate(sweep_values)}
    
    # Run
    runner = MultiSimRunner(multi_config_path)
    runner.preflight()
    runner.run()
    
    # Analyze
    log("Analyzing convergence results...")
    results = []
    for res in runner.results:
        jid = res["job_id"]
        out_dir = Path(res["output_dir"])
        metric_files = ["v2p3_report.json", "summary.json"]
        data = None
        for mf in metric_files:
            path = out_dir / mf
            if path.exists():
                with open(path, 'r') as f:
                    data = json.load(f)
                break
        
        if data:
            results.append({
                "param_value": job_to_val.get(jid),
                "metrics": data
            })
            
    report = {
        "tool": tool_name,
        "sweep_param": sweep_param,
        "results": results,
        "timestamp": runner.results[0].get("timestamp") if runner.results else None
    }
    
    report_path = output_root / "convergence_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    log(f"Convergence sweep complete. Report saved to {report_path}")
    return report_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Numerical Convergence Sweep")
    parser.add_argument("--tool", type=str, required=True, help="Tool name from manifest")
    parser.add_argument("--base-config", type=str, required=True, help="Path to base config JSON")
    parser.add_argument("--param", type=str, required=True, help="Parameter to sweep")
    parser.add_argument("--values", type=float, nargs="+", required=True, help="Values to sweep")
    parser.add_argument("--run-id", type=str, default="default", help="Unique ID for this sweep")
    args = parser.parse_args()
    
    run_convergence_sweep(args.tool, args.base_config, args.param, args.values, args.run_id)
