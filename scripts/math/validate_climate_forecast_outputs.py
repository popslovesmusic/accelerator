import json
import os
from datetime import datetime

def validate_forecast():
    result_path = "validation/results/epistemic_climate_forecast.json"
    val_out_path = "validation/results/climate_forecast_validation_result.json"
    
    report = {
        "validation_id": "VAL-ECF-OUT-VALID-001",
        "status": "pass",
        "projections_verified": False,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        if "projections" in data:
            report["projections_verified"] = True
        else:
             report["status"] = "fail"
             report["governance_violations"].append("missing projections in forecast results")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_forecast()
    print(json.dumps(res, indent=2))
