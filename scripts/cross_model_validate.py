import argparse
import json
import subprocess
import sys
from pathlib import Path
import numpy as np

def compare_results(cpp_out, ref_out, metrics):
    """Compare key metrics between C++ and Reference outputs."""
    with open(cpp_out, 'r') as f:
        cpp_data = json.load(f)
    with open(ref_out, 'r') as f:
        ref_data = json.load(f)

    # Simplified comparison: check last step
    cpp_last = cpp_data[-1] if isinstance(cpp_data, list) else cpp_data
    ref_last = ref_data[-1] if isinstance(ref_data, list) else ref_data

    results = {"pass": True, "details": []}
    for m in metrics:
        v_cpp = cpp_last.get(m)
        v_ref = ref_last.get(m)
        if v_cpp is not None and v_ref is not None:
            diff = abs(v_cpp - v_ref) / (max(abs(v_ref), 1e-9))
            status = "pass" if diff < 0.1 else "fail"
            if status == "fail": results["pass"] = False
            results["details"].append({"metric": m, "cpp": v_cpp, "ref": v_ref, "diff": diff, "status": status})
            
    return results

def main():
    parser = argparse.ArgumentParser(description="Cross-Model Reference Validator")
    parser.add_argument("--tool", required=True)
    args = parser.parse_args()

    with open("registry/tool_manifest.json", "r") as f:
        manifest = json.load(f)

    tool = next((t for t in manifest["tools"] if t["name"] == args.tool), None)
    if not tool or not tool.get("has_reference_implementation"):
        print(f"Tool {args.tool} has no reference implementation.")
        return

    # Run C++ tool (smoke)
    cpp_out = Path(f"outputs/validation/{args.tool}_vs_ref/cpp")
    cpp_out.mkdir(parents=True, exist_ok=True)
    config_path = cpp_out / "config.json"
    
    # Tool-specific config adaptation
    base_config = {"steps": 10, "nx": 32, "ny": 32, "nz": 32, "n": 32, "num_nodes": 32, "width": 32, "height": 32}
    if args.tool == "ca_admissibility_sim_v1_cpp":
        base_config.update({
            "D": 0.1,
            "delta_R": 0.01,
            "gamma_R": 0.01,
            "initial_residue": 0.0,
            "source_strength": 1.0,
            "source_radius": 5
        })
    
    with open(config_path, 'w') as f:
        json.dump(base_config, f)

    print(f"Running C++ tool: {args.tool}...")
    subprocess.run(["python", tool["entry_point"], "--config", str(config_path), "--out", str(cpp_out)])

    # Run Reference (may need different config keys)
    ref_out = Path(f"outputs/validation/{args.tool}_vs_ref/ref")
    ref_out.mkdir(parents=True, exist_ok=True)
    
    ref_config = dict(base_config)
    if args.tool == "ca_admissibility_sim_v1_cpp":
        ref_config["grid_size"] = base_config["width"]
        ref_config["diffusion_rate"] = base_config["D"]
        ref_config["residue_growth"] = base_config["delta_R"]
        ref_config["residue_decay"] = base_config["gamma_R"]
        
    ref_config_path = ref_out / "config_ref.json"
    with open(ref_config_path, 'w') as f:
        json.dump(ref_config, f)

    print(f"Running Reference: {tool['reference_implementation']}...")
    subprocess.run(["python", tool["reference_implementation"], "--config", str(ref_config_path), "--out", str(ref_out)])

    # Compare
    def find_results(d):
        for f in ["summary.json", "metrics.json", "reference_results.json"]:
            p = d / f
            if p.exists():
                with open(p, 'r') as j:
                    data = json.load(j)
                    # If it's a list, take the last element
                    if isinstance(data, list): data = data[-1]
                    # If it has a 'final_metrics' or 'report' key, use that
                    if "final_metrics" in data: return data["final_metrics"]
                    if "report" in data: return data["report"]
                    return data
        return None

    cpp_res = find_results(cpp_out)
    ref_res = find_results(ref_out)
    
    if cpp_res and ref_res:
        res = compare_results_data(cpp_res, ref_res, tool["metrics"])
        print(json.dumps(res, indent=2))
    else:
        print(f"Could not find output files for comparison. CPP found: {cpp_res is not None}, Ref found: {ref_res is not None}")

def compare_results_data(cpp_res, ref_res, metrics):
    results = {"pass": True, "details": []}
    for m in metrics:
        v_cpp = cpp_res.get(m)
        v_ref = ref_res.get(m)
        if v_cpp is not None and v_ref is not None:
            diff = abs(v_cpp - v_ref) / (max(abs(v_ref), 1e-9))
            status = "pass" if diff < 0.2 else "fail" # Loose threshold for different implementations
            if status == "fail": results["pass"] = False
            results["details"].append({"metric": m, "cpp": v_cpp, "ref": v_ref, "diff": diff, "status": status})
    return results

if __name__ == "__main__":
    main()
