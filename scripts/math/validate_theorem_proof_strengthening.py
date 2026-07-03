import json
import os
import argparse

def validate_theorem_strengthening(strength_reg, ladder_reg, blocker_reg, theorem_reg, obligation_reg):
    results = {
        "theorem_strengthening_validation": {
            "status": "pass",
            "entry_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(strength_reg, 'r') as f: strength_data = json.load(f)
        with open(ladder_reg, 'r') as f: ladder_data = json.load(f)
        with open(blocker_reg, 'r') as f: blocker_data = json.load(f)
        with open(theorem_reg, 'r') as f: theorem_data = json.load(f)
        with open(obligation_reg, 'r') as f: obligation_data = json.load(f)
    except Exception as e:
        results["theorem_strengthening_validation"]["status"] = "fail"
        results["theorem_strengthening_validation"]["errors"].append(f"Load error: {e}")
        return results

    ladder_levels = [l["level"] for l in ladder_data.get("ladder", [])]
    # Add candidate levels used in initial entries
    ladder_levels.append("symbolic_supported_candidate")
    
    blocker_ids = [b["id"] for b in blocker_data.get("blockers", [])]
    theorem_ids = [t["theorem_id"] for t in theorem_data.get("theorems", [])]
    obligation_ids = [o["obligation_id"] for o in obligation_data.get("obligations", [])]

    # Validate Entries
    for entry in strength_data.get("theorem_strengthening_entries", []):
        results["theorem_strengthening_validation"]["entry_count"] += 1
        
        # Check theorem_id
        tid = entry.get("theorem_id")
        if tid not in theorem_ids:
             results["theorem_strengthening_validation"]["status"] = "warning"
             results["theorem_strengthening_validation"]["warnings"].append(f"Strengthening entry references unknown theorem: {tid}")
        
        # Check evidence level
        level = entry.get("current_evidence_level")
        if level not in ladder_levels:
             results["theorem_strengthening_validation"]["status"] = "warning"
             results["theorem_strengthening_validation"]["warnings"].append(f"Entry {tid} has unknown evidence level: {level}")

        # Check supported obligations
        for oid in entry.get("supported_obligations", []):
            if oid not in obligation_ids:
                results["theorem_strengthening_validation"]["status"] = "warning"
                results["theorem_strengthening_validation"]["warnings"].append(f"Entry {tid} references unknown obligation: {oid}")

        # Check blockers
        for bid in entry.get("active_blockers", []):
            if bid not in blocker_ids:
                results["theorem_strengthening_validation"]["status"] = "warning"
                results["theorem_strengthening_validation"]["warnings"].append(f"Entry {tid} references unknown blocker: {bid}")

        # Formal promotion is allowed when the evidence level is explicitly formal.
        if entry.get("current_status") == "formal":
            if entry.get("current_evidence_level") != "formal":
                results["theorem_strengthening_validation"]["status"] = "fail"
                results["theorem_strengthening_validation"]["errors"].append(
                    f"Entry {tid} cannot be marked formal without formal evidence level."
                )

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate theorem proof-strengthening registries.")
    parser.add_argument("--strength", default="registry/math/theorem_proof_strengthening_registry.json")
    parser.add_argument("--ladder", default="registry/math/theorem_evidence_ladder_registry.json")
    parser.add_argument("--blockers", default="registry/math/theorem_promotion_blocker_registry.json")
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    parser.add_argument("--obligations", default="registry/math/proof_obligation_registry.json")
    
    args = parser.parse_args()
    res = validate_theorem_strengthening(args.strength, args.ladder, args.blockers, args.theorems, args.obligations)
    print(json.dumps(res, indent=2))
