
import json
import csv
from pathlib import Path

def convert_to_csv():
    trace_path = Path("outputs/runs/h2_collapse_signature/trace.json")
    csv_path = Path("outputs/runs/h2_collapse_signature/trace_for_spectral.csv")
    
    with open(trace_path, "r") as f:
        data = json.load(f)
        
    if not data:
        return
        
    # We only care about phase_error and continuation_mismatch
    target_keys = ["t", "phase_error", "continuation_mismatch", "input_signal"]
    
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=target_keys)
        writer.writeheader()
        for row in data:
            clean_row = {k: row.get(k, 0.0) for k in target_keys}
            writer.writerow(clean_row)
            
    print(f"Converted to CSV: {csv_path}")

if __name__ == "__main__":
    convert_to_csv()
