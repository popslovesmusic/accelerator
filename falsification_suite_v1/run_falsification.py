import os
import json
import argparse
import subprocess
import tempfile
from pathlib import Path

def evaluate_assertion(assertion, metrics):
    """
    Evaluates a string assertion against a dictionary of metrics.
    Example: 'order_parameter < 0.2'
    """
    # Simple parser for <, >, ==, <=, >=
    operators = ['<=', '>=', '<', '>', '==']
    op = None
    for o in operators:
        if o in assertion:
            op = o
            break
            
    if not op:
        return False, "Unknown operator"
        
    metric_name, threshold_str = assertion.split(op)
    metric_name = metric_name.strip()
    threshold = float(threshold_str.strip())
    
    if metric_name not in metrics:
        return False, f"Metric {metric_name} not found"
        
    val = float(metrics[metric_name])
    
    passed = False
    if op == '<': passed = val < threshold
    elif op == '>': passed = val > threshold
    elif op == '==': passed = abs(val - threshold) < 1e-9
    elif op == '<=': passed = val <= threshold
    elif op == '>=': passed = val >= threshold
    
    return passed, f"{val:.4f} {op} {threshold}"

def run_test(test_def, output_root):
    test_name = test_def['name']
    target_script = Path(test_def['target_script']).resolve()
    base_config_path = Path(test_def['base_config']).resolve()
    
    # Strict sanitization for Windows paths
    safe_name = "".join([c if c.isalnum() else "_" for c in test_name])
    test_dir = (output_root / safe_name).resolve()
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load base config
    with open(base_config_path, 'r') as f:
        config = json.load(f)
        
    # 2. Apply overrides (handle nested)
    def apply_overrides(conf, overrides):
        for k, v in overrides.items():
            if isinstance(v, dict) and k in conf and isinstance(conf[k], dict):
                apply_overrides(conf[k], v)
            else:
                conf[k] = v

    apply_overrides(config, test_def.get('overrides', {}))
        
    # 3. Save temporary config
    config_path = test_dir / "test_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f)
        
    # 4. Execute
    try:
        subprocess.run(
            ["python", str(target_script), "--config", str(config_path), "--out", str(test_dir)],
            check=True, capture_output=True, text=True
        )
    except subprocess.CalledProcessError as e:
        return {"name": test_name, "status": "ERROR", "message": e.stderr}

    # 5. Load summary.json
    summary_path = test_dir / "summary.json"
    if not summary_path.exists():
        # Maybe it's in the weird relative path sim.py likes?
        # But we passed absolute test_dir, so it SHOULD be here.
        return {"name": test_name, "status": "ERROR", "message": f"summary.json not found at {summary_path}"}
        
    with open(summary_path, 'r') as f:
        summary = json.load(f)
        
    # Support both 'final_metrics' and 'final' keys
    metrics = summary.get('final_metrics', summary.get('final', {}))
    
    # 6. Evaluate assertions
    assertion_results = []
    all_passed = True
    for assertion in test_def['assertions']:
        passed, msg = evaluate_assertion(assertion, metrics)
        if not passed: all_passed = False
        assertion_results.append({"assertion": assertion, "passed": passed, "message": msg})
        
    return {
        "name": test_name,
        "status": "PASS" if all_passed else "FAIL",
        "assertions": assertion_results
    }

def main():
    parser = argparse.ArgumentParser(description="Unit Test / Falsification Harness")
    parser.add_argument("--config", type=str, required=True, help="Path to test suite JSON")
    parser.add_argument("--out", type=str, default="outputs/falsification_report", help="Output directory")
    args = parser.parse_args()
    
    with open(args.config, 'r') as f:
        suite = json.load(f)
        
    output_root = Path(args.out)
    output_root.mkdir(parents=True, exist_ok=True)
    
    print(f"Executing Falsification Suite: {len(suite['tests'])} tests...")
    
    results = []
    for test_def in suite['tests']:
        print(f"Running: {test_def['name']}...", end="", flush=True)
        res = run_test(test_def, output_root)
        results.append(res)
        print(f" [{res['status']}]")
        if res['status'] == 'FAIL':
            for a in res['assertions']:
                if not a['passed']:
                    print(f"  - FAILED: {a['assertion']} (Result: {a['message']})")

    # Save report
    with open(output_root / "falsification_report.json", 'w') as f:
        json.dump(results, f, indent=2)
        
    total_passed = sum(1 for r in results if r['status'] == 'PASS')
    print(f"\nSuite complete. {total_passed}/{len(results)} tests passed.")

if __name__ == "__main__":
    main()
