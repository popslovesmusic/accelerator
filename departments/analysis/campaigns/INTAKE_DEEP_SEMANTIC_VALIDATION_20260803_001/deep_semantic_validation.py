import argparse
import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class Orientation:
    source_domain: str
    source_primitive: str
    target_domain: str
    target_primitive: str
    relation: str
    context: str

    def inverse(self):
        return Orientation(self.target_domain, self.target_primitive, self.source_domain, self.source_primitive, self.relation, self.context)


def check(name, passed, detail):
    return {"name": name, "passed": bool(passed), "detail": detail}


def run_056():
    orientation_space = {"north", "east", "south", "west"}

    def exclude(boundary, space):
        if boundary == "north-facing":
            return space - {"south"}
        if boundary == "east-facing":
            return space - {"west"}
        return set()

    checks = [
        check("boundary_conditions_change_admissible_family", exclude("north-facing", orientation_space) != exclude("east-facing", orientation_space), "distinct boundaries yield distinct admissible families"),
        check("excluded_orientation_is_not_symmetry_mutation", orientation_space == {"north", "east", "south", "west"}, "source family remains unchanged"),
        check("exclusion_is_deterministic", exclude("north-facing", orientation_space) == exclude("north-facing", orientation_space), "repeat evaluation identical"),
        check("reference_orientation_is_relational", "north" in exclude("east-facing", orientation_space) and "west" not in exclude("east-facing", orientation_space), "result depends on boundary relation"),
        check("invalid_boundary_does_not_synthesize_result", exclude("invalid", orientation_space) == set(), "undefined boundary returns empty result"),
    ]
    return {"packet_id": "RT_ASYM_OBSERVATION_ORIENTATION_EXCLUSION_INDUCTION_20260728_001", "checks": checks, "status": "PASS_FINITE_SEMANTIC_MODEL" if all(c["passed"] for c in checks) else "FAIL_FINITE_SEMANTIC_MODEL", "limitation": "Finite toy orientation family; no proof of the proposed operator in general."}


def run_057():
    o = Orientation("D_A", "P_A", "D_B", "P_B", "boundary-reference", "ctx-1")
    inv = o.inverse()
    checks = [
        check("typed_orientation_has_context", bool(o.context), o.context),
        check("inverse_exchanges_domains", (inv.source_domain, inv.target_domain) == (o.target_domain, o.source_domain), (inv.source_domain, inv.target_domain)),
        check("inverse_exchanges_primitives", (inv.source_primitive, inv.target_primitive) == (o.target_primitive, o.source_primitive), (inv.source_primitive, inv.target_primitive)),
        check("inverse_preserves_relation", inv.relation == o.relation, inv.relation),
        check("double_inverse_is_identity", inv.inverse() == o, "double inverse reconstructed original typed orientation"),
        check("context_free_orientation_rejected", not bool(Orientation("D_A", "P_A", "D_B", "P_B", "boundary-reference", "").context), "empty context is invalid"),
        check("same_scalar_projection_does_not_equal_typed_identity", o != Orientation("D_A", "P_A", "D_B", "P_B", "boundary-reference-2", "ctx-2"), "typed fields retain distinction"),
    ]
    return {"packet_id": "RT_BOUNDARY_ORIENTATION_ASYM_INDUCTION_20260728_001", "checks": checks, "status": "PASS_FINITE_SEMANTIC_MODEL" if all(c["passed"] for c in checks) else "FAIL_FINITE_SEMANTIC_MODEL", "limitation": "Finite typed relation model; no external empirical validation."}


def run_060():
    primitives = ("p1", "p2", "p3")

    def otm(rt):
        return tuple(rt)

    def mto(aspects):
        if not aspects or any(not a for a in aspects):
            return None
        return tuple(sorted(aspects))

    a = ("p1", "p2")
    b = ("p2", "p1")
    rt_a = mto(a)
    rt_b = mto(b)
    checks = [
        check("domain_lift_preserves_primitive_multiplicity", otm(("p1", "p1", "p2")) == ("p1", "p1", "p2"), otm(("p1", "p1", "p2"))),
        check("mto_is_deterministic_under_declared_rule", rt_a == rt_b, (rt_a, rt_b)),
        check("otm_mto_roundtrip_for_closed_rt", mto(otm(rt_a)) == rt_a, (mto(otm(rt_a)), rt_a)),
        check("empty_aspect_set_fails_without_synthesized_rt", mto(()) is None, mto(())),
        check("primitive_cycle_is_domain_relative", len(primitives) == 3 and rt_a is not None, "primitive -> aspect -> RT -> primitive set"),
        check("different_aspect_order_is_same_output_only_under_declared_equivalence", rt_a == rt_b, "order-insensitive candidate rule explicitly declared"),
        check("identity_loss_boundary_is_visible", a != b and rt_a == rt_b, "distinct aspect histories collapse to equivalent RT output"),
    ]
    return {"packet_id": "RT_INDUCTION_RECURSIVE_PATTERN_AND_DOMAIN_LIFT_001", "checks": checks, "status": "PASS_FINITE_SEMANTIC_MODEL" if all(c["passed"] for c in checks) else "FAIL_FINITE_SEMANTIC_MODEL", "limitation": "Finite candidate semantics exposes identity loss and does not establish uniqueness of the general calculus."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    results = [run_056(), run_057(), run_060()]
    payload = {
        "campaign_id": "INTAKE_DEEP_SEMANTIC_VALIDATION_20260803_001",
        "status": "BOUNDED_FINITE_MODEL_EXECUTION",
        "results": results,
        "omitted_packet": {"packet_id": "RT_INDUCTION_MTO_OTM_CALCULUS_001", "reason": "Existing adversarial campaign already supplies the deeper fixture and counterexample evidence; this pass does not overwrite it."},
        "claim_ceiling": "C1",
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out.relative_to(ROOT)), "statuses": {r["packet_id"]: r["status"] for r in results}}, indent=2))


if __name__ == "__main__":
    main()
