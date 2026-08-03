"""Independent verifier for Campaign 005 serialized projection outputs."""
import json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "domain_relative_entropy_projection_test_005"
def main():
    rows = json.loads((OUT / "projection_results.json").read_text(encoding="utf-8"))
    ok = 0
    for row in rows:
        f, i = row["source"], row["inverse_source"]
        a = dict(f["redistribution_content"]); b = dict(i["redistribution_content"])
        fv = math.log((float(a["target_weight"])+float(a["capacity"]))/(float(a["source_weight"])+float(a["capacity"])))
        iv = math.log((float(b["target_weight"])+float(b["capacity"]))/(float(b["source_weight"])+float(b["capacity"])))
        if abs(fv-row["forward"]["observable"]) < 1e-12 and abs(iv-row["inverse"]["observable"]) < 1e-12 and abs(fv+iv) < 1e-12 and row["forward"]["relation_identity"] == row["inverse"]["relation_identity"]: ok += 1
    (OUT / "independent_verification.json").write_text(json.dumps({"status":"PASS" if ok == len(rows) else "FAIL", "verified":ok, "total":len(rows), "reference_values_used":False}, indent=2)+"\n", encoding="utf-8")
if __name__ == "__main__": main()
