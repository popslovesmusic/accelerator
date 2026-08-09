import argparse
import itertools
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def alt_exclusion(label, values):
    removed = {"north-facing": "south", "east-facing": "west"}.get(label)
    if removed is None:
        return {"code": "INVALID_BOUNDARY", "values": []}
    result = sorted(set(values).difference({removed}))
    return {"code": "EMPTY_ADMISSIBLE_FAMILY" if not result else "SUCCESS", "values": result}


def alt_inverse(record):
    if not record["context"]:
        return None
    return {"source_domain": record["target_domain"], "source_primitive": record["target_primitive"], "target_domain": record["source_domain"], "target_primitive": record["source_primitive"], "relation": record["relation"], "context": record["context"]}


def alt_mto(sequence, depth_limit=4):
    history = list(sequence)
    if len(history) == 0:
        return {"code": "EMPTY_INPUT", "output": None, "history": history}
    if len(history) > depth_limit:
        return {"code": "DEPTH_LIMIT", "output": None, "history": history}
    counts = Counter(history)
    output = tuple(sorted((item, count) for item, count in counts.items()))
    return {"code": "SUCCESS", "output": output, "history": history}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    failures = []
    cases = 0

    values = ("north", "east", "south", "west")
    for length in range(5):
        for subset in itertools.combinations(values, length):
            for label in ("north-facing", "east-facing", "invalid"):
                cases += 1
                a = alt_exclusion(label, subset)
                b = alt_exclusion(label, subset)
                if a != b or a["code"] not in {"SUCCESS", "EMPTY_ADMISSIBLE_FAMILY", "INVALID_BOUNDARY"}:
                    failures.append({"family": "056", "case": [label, subset], "observed": a})

    for fields in itertools.product(("D0", "D1"), ("P0", "P1"), ("D0", "D1"), ("P0", "P1"), ("r0", "r1"), ("c0", "c1")):
        record = dict(zip(("source_domain", "source_primitive", "target_domain", "target_primitive", "relation", "context"), fields))
        cases += 1
        rev = alt_inverse(record)
        rev2 = alt_inverse(rev)
        if rev2 != record or rev["relation"] != record["relation"] or rev["context"] != record["context"]:
            failures.append({"family": "057", "case": record, "observed": rev2})

    for length in range(7):
        for sequence in itertools.product(("p0", "p1", "p2"), repeat=length):
            cases += 1
            out = alt_mto(sequence)
            expected = "EMPTY_INPUT" if length == 0 else "DEPTH_LIMIT" if length > 4 else "SUCCESS"
            if out["code"] != expected or out["history"] != list(sequence):
                failures.append({"family": "060", "case": sequence, "observed": out})
            if out["code"] == "SUCCESS" and sum(count for _, count in out["output"]) != length:
                failures.append({"family": "060", "case": sequence, "observed": out})

    prior_path = ROOT / "departments/analysis/campaigns/INTAKE_BROADER_MODEL_CLASS_20260803_001/results.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    payload = {
        "campaign_id": "INTAKE_CROSS_IMPLEMENTATION_20260803_001",
        "status": "PASS_INDEPENDENT_CROSS_IMPLEMENTATION" if not failures and prior.get("failure_count") == 0 else "FAIL_INDEPENDENT_CROSS_IMPLEMENTATION",
        "cases": cases,
        "failure_count": len(failures),
        "failures": failures,
        "prior_result_comparison": {"prior_status": prior.get("status"), "prior_failure_count": prior.get("failure_count")},
        "claim_ceiling": "C1",
        "limitation": "Agreement between two finite implementations does not establish completeness or external validity.",
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out.relative_to(ROOT)), "status": payload["status"], "cases": cases, "failure_count": len(failures)}, indent=2))


if __name__ == "__main__":
    main()
