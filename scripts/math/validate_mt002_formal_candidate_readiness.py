import json
import os
import argparse

def validate_mt002_readiness(readiness_reg, theorem_reg, blocker_reg):
    results = {
        "mt002_readiness_validation": {
            "status": "pass",
            "theorem_id": "MT-002",
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(readiness_reg, 'r') as f: readiness_data = json.load(f)
        with open(theorem_reg, 'r') as f: theorem_data = json.load(f)
        with open(blocker_reg, 'r') as f: blocker_data = json.load(f)
    except Exception as e:
        results["mt002_readiness_validation"]["status"] = "fail"
        results["mt002_readiness_validation"]["errors"].append(f"Load error: {e}")
        return results

    # Verify target theorem
    if readiness_data["readiness_summary"]["theorem_id"] != "MT-002":
        results["mt002_readiness_validation"]["status"] = "fail"
        results["mt002_readiness_validation"]["errors"].append(f"Registry target mismatch: expected MT-002, found {readiness_data['readiness_summary']['theorem_id']}")

    # Check blockers
    blocker_ids = [b["id"] for b in blocker_data.get("blockers", [])]
    for blocker in readiness_data.get("blocker_status", []):
        if blocker["blocker_id"] not in blocker_ids:
             results["mt002_readiness_validation"]["status"] = "warning"
             results["mt002_readiness_validation"]["warnings"].append(f"Unknown blocker ID in readiness registry: {blocker['blocker_id']}")

    # Check readiness level against evidence ladder
    if readiness_data["readiness_summary"]["readiness_level"] == "formal":
         results["mt002_readiness_validation"]["status"] = "fail"
         results["mt002_readiness_validation"]["errors"].append("MT-002 cannot be marked 'formal' in a readiness review.")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate MT-002 formal-candidate readiness.")
    parser.add_argument("--readiness", default="registry/math/mt002_formal_candidate_readiness_registry.json")
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    parser.add_argument("--blockers", default="registry/math/theorem_promotion_blocker_registry.json")
    
    args = parser.parse_args()
    res = validate_mt002_readiness(args.readiness, args.theorems, args.blockers)
    print(json.dumps(res, indent=2))
