import argparse
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def repaired_exclusion(boundary, orientations):
    if boundary not in {"north-facing", "east-facing"}:
        return "INVALID_BOUNDARY", ()
    excluded = "south" if boundary == "north-facing" else "west"
    remaining = tuple(sorted(x for x in orientations if x != excluded))
    return ("EMPTY_ADMISSIBLE_FAMILY", ()) if not remaining else ("SUCCESS", remaining)


def inverse(o):
    if not o[5]:
        return None
    return (o[2], o[3], o[0], o[1], o[4], o[5])


def mto(aspects, limit=4):
    if not aspects:
        return "EMPTY_INPUT", None, aspects
    if len(aspects) > limit:
        return "DEPTH_LIMIT", None, aspects
    return "SUCCESS", tuple(sorted(aspects)), aspects


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    failures = []
    counts = {"056": 0, "057": 0, "060": 0}

    orientations = ("north", "east", "south", "west")
    for size in range(5):
        for subset in itertools.combinations(orientations, size):
            for boundary in ("north-facing", "east-facing", "invalid"):
                counts["056"] += 1
                first = repaired_exclusion(boundary, subset)
                second = repaired_exclusion(boundary, subset)
                if first != second or first[0] not in {"SUCCESS", "EMPTY_ADMISSIBLE_FAMILY", "INVALID_BOUNDARY"}:
                    failures.append({"family": "056", "case": [boundary, subset], "observed": first})

    domains = ("D0", "D1", "D2")
    primitives = ("P0", "P1", "P2")
    contexts = ("C0", "C1")
    for ds, ps, dt, pt, rel, ctx in itertools.product(domains, primitives, domains, primitives, ("r0", "r1"), contexts):
        o = (ds, ps, dt, pt, rel, ctx)
        counts["057"] += 1
        if inverse(inverse(o)) != o or inverse(o)[4] != rel or inverse(o)[5] != ctx:
            failures.append({"family": "057", "case": o, "observed": inverse(inverse(o))})

    for length in range(0, 7):
        for aspects in itertools.product(("p0", "p1", "p2"), repeat=length):
            counts["060"] += 1
            status, rt, history = mto(aspects)
            expected_status = "EMPTY_INPUT" if length == 0 else ("DEPTH_LIMIT" if length > 4 else "SUCCESS")
            if status != expected_status or history != aspects:
                failures.append({"family": "060", "case": aspects, "observed": [status, rt, history]})
            if status == "SUCCESS" and tuple(sorted(aspects)) != rt:
                failures.append({"family": "060", "case": aspects, "observed": rt})

    payload = {
        "campaign_id": "INTAKE_BROADER_MODEL_CLASS_20260803_001",
        "status": "PASS_BOUNDED_MODEL_CLASS" if not failures else "FAIL_BOUNDED_MODEL_CLASS",
        "counts": counts,
        "total_cases": sum(counts.values()),
        "failures": failures,
        "failure_count": len(failures),
        "frozen_repair_rule": True,
        "claim_ceiling": "C1",
        "limitation": "Generated finite combinations do not establish completeness over all model classes.",
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out.relative_to(ROOT)), "status": payload["status"], "total_cases": payload["total_cases"], "failure_count": payload["failure_count"]}, indent=2))


if __name__ == "__main__":
    main()
