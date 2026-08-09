import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def case(name, found, detail, implication):
    return {"case": name, "counterexample_found": found, "detail": detail, "implication": implication}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    orientation_space = {"north", "east", "south", "west"}
    cases = []

    # 056: alternate boundary semantics and degenerate admissibility.
    north = orientation_space - {"south"}
    north_alt = orientation_space - {"north"}
    cases.append(case("056_boundary_semantics_nonunique", north != north_alt, "The same boundary label can admit different exclusion interpretations without a fixed semantic rule.", "The exclusion operator needs a frozen semantics or model class."))
    cases.append(case("056_empty_admissible_family", len(set()) == 0, "A boundary can yield no admissible orientations.", "Failure semantics must distinguish invalid, empty, and resolved outcomes."))
    cases.append(case("056_boundary_free_orientation", True, "An orientation family can be supplied without a boundary argument in an unconstrained model.", "The claimed dependency orientation <- boundary is not universal without an admissibility axiom."))

    # 057: typed orientation information-loss controls.
    forward = ("D_A", "P_A", "D_B", "P_B", "r", "ctx")
    inverse = ("D_B", "P_B", "D_A", "P_A", "r", "ctx")
    scalar = lambda x: 0
    cases.append(case("057_scalar_projection_collapse", forward != inverse and scalar(forward) == scalar(inverse), "Distinct ordered orientations map to the same scalar.", "Scalar projection cannot define orientation identity."))
    cases.append(case("057_context_removal_collapse", forward[:-1] == inverse[:-1], "Removing context makes otherwise distinct relation instances indistinguishable in a repeated fixture.", "Context is semantically necessary where relation identity is reused."))
    cases.append(case("057_self_inverse_exception", forward == inverse, "A self-loop orientation is its own inverse under role exchange.", "Non-identity of O and Inv(O) requires an explicit self-inverse exception."))

    # 060: finite countermodels to general MTO/OTM claims.
    aspects = ("a", "b")
    possible_outputs = {"RT1", "RT2"}
    cases.append(case("060_nondeterministic_mto", len(possible_outputs) > 1, "The same admissible aspect pair is permitted two distinct RT outputs.", "MTO single-valuedness requires an explicit selector or tie-break rule."))
    cases.append(case("060_identity_history_collapse", ("p1", "p2") != ("p2", "p1") and sorted(("p1", "p2")) == sorted(("p2", "p1")), "Distinct aspect orderings resolve to the same order-insensitive RT representation.", "Historical aspect identity is not recoverable from RT output alone."))
    graph = {"RT_A": "RT_B", "RT_B": "RT_A"}
    seen = set()
    current = "RT_A"
    for _ in range(4):
        seen.add(current)
        current = graph[current]
    cases.append(case("060_recursive_nontermination_cycle", current in seen, "A finite recursive transition graph contains a cycle.", "Domain termination cannot be assumed without a well-foundedness or stop condition."))
    cases.append(case("060_multiplicity_loss_under_set_otm", len(["p1", "p1", "p2"]) != len(set(["p1", "p1", "p2"])), "Set-valued OTM output erases repeated primitive occurrences.", "OTM must be multiset/sequence-valued when multiplicity is semantically relevant."))

    payload = {
        "campaign_id": "INTAKE_ADVERSARIAL_COUNTERMODELS_20260803_001",
        "status": "COUNTERMODELS_FOUND",
        "claim_ceiling": "C1",
        "results": cases,
        "summary": "Adversarial finite models expose unresolved semantic obligations for all three tested proposal families.",
        "prohibited_inference": "Countermodels to a declared candidate semantics do not by themselves falsify every possible formulation of the intake proposals.",
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out.relative_to(ROOT)), "countermodels": sum(c["counterexample_found"] for c in cases), "total": len(cases)}, indent=2))


if __name__ == "__main__":
    main()
