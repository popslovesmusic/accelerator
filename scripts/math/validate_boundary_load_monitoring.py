import json
import os
from datetime import datetime

def validate_boundary_load():
    result_path = "validation/results/epistemic_climate_regulation_results.json"
    val_out_path = "validation/results/boundary_load_monitoring_validation_result.json"
    
    report = {
        "validation_id": "VAL-ECR-LOAD-VALID-001",
        "status": "pass",
        "load_monitored": False,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        measurements = data.get("measurements", {})
        if "boundary_load_index" in measurements:
            report["load_monitored"] = True
            if measurements["boundary_load_index"] > 0.8: # Critical threshold
                 report["status"] = "fail"
                 report["governance_violations"].append("critical boundary load index detected")
        else:
             report["status"] = "fail"
             report["governance_violations"].append("boundary load index not tracked in results")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_boundary_load()
    print(json.dumps(res, indent=2))
