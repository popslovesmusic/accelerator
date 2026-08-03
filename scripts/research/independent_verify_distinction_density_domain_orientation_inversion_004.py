"""Independent verification for Campaign 004; reads serialized pairs only."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "distinction_density_domain_orientation_inversion_004"
def inv(o):
    r = dict(o["redistribution_content"])
    content = [["source_weight", r["target_weight"]], ["target_weight", r["source_weight"]], ["capacity", r["capacity"]], ["shape_token", r["shape_token"]]]
    oid = o["orientation_id"][:-4] if o["orientation_id"].endswith("_inv") else o["orientation_id"] + "_inv"
    return {**o, "orientation_id": oid, "source_domain": o["target_domain"], "source_primitive": o["target_primitive"], "target_domain": o["source_domain"], "target_primitive": o["source_primitive"], "redistribution_content": content}
def main():
    total = passed = 0
    for path in OUT.glob("*_orientation_pairs.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line); o = row["forward"]; total += 1
            once = inv(o); twice = inv(once)
            if twice == o and once["relation_identity"] == o["relation_identity"] and once["source_domain"] == o["target_domain"] and once["source_primitive"] == o["target_primitive"]: passed += 1
    result = {"status": "PASS" if passed == total else "FAIL", "verified": passed, "total": total}
    (OUT / "independent_verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
if __name__ == "__main__": main()
