import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / "0022_ordered_orientation_evaluator_fixtures.json").read_text(encoding="utf-8"))
alphabet = set(fixtures["alphabet"])


def evaluate(left, right):
    if left not in alphabet or right not in alphabet:
        return None
    return f"{left}|{right}"


results = []
for case in fixtures["cases"]:
    observed = evaluate(case["left"], case["right"])
    results.append({"id": case["id"], "expected": case["expected"], "observed": observed, "pass": observed == case["expected"]})

ordered_distinction = evaluate("S", "s") != evaluate("s", "S")
required_distinction = fixtures["required_distinction"]["equivalent_without_reorientation"] is False

out = {
    "check_id": "ORDERED_ORIENTATION_EVALUATOR_CHECK_20260726",
    "status": "PASS_BOUNDED_ORDERED_EVALUATOR" if all(r["pass"] for r in results) and ordered_distinction and required_distinction else "FAIL_BOUNDED_ORDERED_EVALUATOR",
    "alphabet": fixtures["alphabet"],
    "orientation_count": len(results),
    "passed": sum(r["pass"] for r in results),
    "failed": sum(not r["pass"] for r in results),
    "ordered_distinction_checked": ordered_distinction,
    "automatic_equivalence_rejected": required_distinction,
    "results": results,
    "limitations": ["finite syntactic alphabet", "placeholder token semantics", "no projection or closure semantics", "no physical interpretation"]
}
(ROOT / "0022_ordered_orientation_evaluator_check_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
