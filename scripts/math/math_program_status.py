import json
import os
import argparse
try:
    from scripts.math.math_program_validate import validate_math_program
except ImportError:
    from math_program_validate import validate_math_program

def summarize_math_status():
    val = validate_math_program()
    mv = val["math_program_validation"]
    
    summary = {
        "math_program_status": {
            "overall_status": mv["status"],
            "readiness": mv["readiness_summary"],
            "domain_inventory": {
                domain: {
                    "status": info.get("status"),
                    "item_count": info.get("object_count") or info.get("entry_count") or info.get("chain_count") or info.get("theorem_count")
                }
                for domain, info in mv["domain_status"].items()
            },
            "critical_gaps": len(mv["closure_gaps"]),
            "unresolved_questions": len(mv["open_questions"])
        }
    }
    
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize formal math program status.")
    parser.add_argument("--out", help="Path to save status report.")
    args = parser.parse_args()
    
    status = summarize_math_status()
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, 'w') as f:
            json.dump(status, f, indent=2)
        print(f"Status report saved to {args.out}")
    else:
        print(json.dumps(status, indent=2))
