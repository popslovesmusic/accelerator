import json
import os
from datetime import datetime

def validate_long_horizon():
    result_path = "validation/results/epistemic_climate_regulation_results.json"
    val_out_path = "validation/results/long_horizon_non_globalization_validation_result.json"
    
    report = {
        "validation_id": "VAL-ECR-LH-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        measurements = data.get("measurements", {})
        if measurements.get("globalization_wind_shear", 0) > 0.5: # Arbitrary threshold
             report["status"] = "fail"
             report["governance_violations"].append("high globalization wind shear detected in long-horizon monitoring")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_long_horizon()
    print(json.dumps(res, indent=2))
