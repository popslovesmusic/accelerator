import argparse
import json
import os
from pathlib import Path
import sys

# Add current dir to sys.path to import from multi_sim_runner if needed
sys.path.append(os.getcwd())
from scripts.multi_sim_runner import MultiSimRunner, log

def run_regression_test(tool_a, tool_b, config_path, run_id):
    log(f"Starting regression test between {tool_a} and {tool_b}")
    
    output_root = Path(f"outputs/regression_{run_id}")
    output_root.mkdir(parents=True, exist_ok=True)
    
    # Generate multi-run config
    multi_config = {
        "run_id": f"reg_{run_id}",
        "mode": "parallel", # can run both at same time
        "output_root": str(output_root),
        "governance": {
            "dry_run_first": False,
            "stop_on_failure": False
        },
        "jobs": [
            {
                "job_id": "tool_a",
                "tool": tool_a,
                "config": config_path,
                "claim_role": "comparison"
            },
            {
                "job_id": "tool_b",
                "tool": tool_b,
                "config": config_path,
                "claim_role": "comparison"
            }
        ]
    }
    
    multi_config_path = output_root / "multi_run_regression.json"
    with open(multi_config_path, 'w') as f:
        json.dump(multi_config, f, indent=2)
        
    # Run
    runner = MultiSimRunner(multi_config_path)
    runner.preflight()
    runner.run()
    
    # Compare
    log("Comparing regression results...")
    metrics = {}
    for res in runner.results:
        jid = res["job_id"]
        out_dir = Path(res["output_dir"])
        metric_files = ["v2p3_report.json", "summary.json", "v2p3_precision_report.json"]
        data = None
        for mf in metric_files:
            path = out_dir / mf
            if path.exists():
                with open(path, 'r') as f:
                    data = json.load(f)
                break
        
        # C4 Extension: If no JSON, try parsing stdout for "Final <Name> Metrics:"
        if not data and "stdout_log" in res:
            try:
                with open(res["stdout_log"], 'r') as f:
                    stdout = f.read()
                if "Final" in stdout and "Metrics:" in stdout:
                    data = {}
                    lines = stdout.split('\n')
                    capture = False
                    for line in lines:
                        if "Final" in line and "Metrics:" in line:
                            capture = True
                            continue
                        if capture and ":" in line:
                            parts = line.split(':')
                            key = parts[0].strip().lower().replace(' ', '_')
                            try:
                                val_str = parts[1].strip().split(' ')[0]
                                data[key] = float(val_str)
                            except:
                                pass
                        elif capture and not line.strip():
                            break
            except:
                pass

        if data:
            metrics[jid] = data
            
    comparison = {
        "tool_a": tool_a,
        "tool_b": tool_b,
        "config_path": config_path,
        "metrics_found": list(metrics.keys()),
        "matches": {},
        "mismatches": {}
    }
    
    if "tool_a" in metrics and "tool_b" in metrics:
        ma = metrics["tool_a"]
        mb = metrics["tool_b"]
        
        # Flatten and compare
        def flatten(d, prefix=""):
            items = []
            if isinstance(d, dict):
                for k, v in d.items():
                    new_key = f"{prefix}.{k}" if prefix else k
                    if isinstance(v, dict):
                        items.extend(flatten(v, new_key).items())
                    else:
                        items.append((new_key, v))
            return dict(items)
            
        fa = flatten(ma)
        fb = flatten(mb)
        
        # C4 Extension: Try to find matches even if prefixes differ (e.g. final_metrics.x vs metrics.x)
        def get_base_key(k):
            return k.split('.')[-1]
            
        base_a = {get_base_key(k): (k, v) for k, v in fa.items()}
        base_b = {get_base_key(k): (k, v) for k, v in fb.items()}
        
        all_base_keys = set(base_a.keys()) | set(base_b.keys())
        
        for bk in all_base_keys:
            if bk in base_a and bk in base_b:
                ka, va = base_a[bk]
                kb, vb = base_b[bk]
                if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                    diff = abs(va - vb)
                    rel_diff = diff / max(abs(va), 1e-9)
                    if diff < 1e-6 or rel_diff < 1e-4:
                        comparison["matches"][bk] = {"va": va, "vb": vb, "diff": diff, "ka": ka, "kb": kb}
                    else:
                        comparison["mismatches"][bk] = {"va": va, "vb": vb, "diff": diff, "rel_diff": rel_diff, "ka": ka, "kb": kb}
                elif va == vb:
                    comparison["matches"][bk] = {"val": va, "ka": ka, "kb": kb}
                else:
                    comparison["mismatches"][bk] = {"va": va, "vb": vb, "ka": ka, "kb": kb}
                    
    report_path = output_root / "regression_report.json"
    with open(report_path, 'w') as f:
        json.dump(comparison, f, indent=2)
        
    log(f"Regression test complete. Report saved to {report_path}")
    return report_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Python/C++ Regression Testing")
    parser.add_argument("--tool-a", type=str, required=True, help="First tool name")
    parser.add_argument("--tool-b", type=str, required=True, help="Second tool name (port)")
    parser.add_argument("--config", type=str, required=True, help="Path to config JSON")
    parser.add_argument("--run-id", type=str, default="default", help="Unique ID for this test")
    args = parser.parse_args()
    
    run_regression_test(args.tool_a, args.tool_b, args.config, args.run_id)
