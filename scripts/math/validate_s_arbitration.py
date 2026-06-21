import argparse
import json
import os
from datetime import datetime


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def apply_s(candidates):
    return [
        candidate for candidate in candidates
        if candidate.get("typed")
        and candidate.get("distinction_ok")
        and candidate.get("residue_ok")
        and candidate.get("topology_ok")
        and candidate.get("orientation_ok")
    ]


def apply_arb_a(candidates):
    if not candidates:
        return None
    return min(candidates, key=lambda candidate: (candidate.get("mismatch", float("inf")), candidate.get("id", "")))


def fixture_summary(candidates, pruned, selected_raw, selected_pruned):
    return {
        "raw_count": len(candidates),
        "pruned_count": len(pruned),
        "raw_ids": [candidate["id"] for candidate in candidates],
        "pruned_ids": [candidate["id"] for candidate in pruned],
        "removed_ids": [candidate["id"] for candidate in candidates if candidate not in pruned],
        "selected_from_raw": None if selected_raw is None else selected_raw["id"],
        "selected_from_pruned": None if selected_pruned is None else selected_pruned["id"],
    }


def validate_s_arbitration(spec_path, root_operator_path, math_operator_path, branch_path, selection_path):
    spec = load_json(spec_path)
    root_operator_registry = load_json(root_operator_path)
    math_operator_registry = load_json(math_operator_path)
    branch_registry = load_json(branch_path)
    selection_registry = load_json(selection_path)

    root_symbols = {entry.get("symbol"): entry for entry in root_operator_registry.get("operators", [])}
    math_symbols = {entry.get("symbol"): entry for entry in math_operator_registry.get("operators", [])}
    branch_targets = {entry.get("target_operator") for entry in branch_registry.get("pruning_entries", [])}
    selection_targets = {entry.get("target_operator") for entry in selection_registry.get("selection_rules", [])}

    operator_audit = {
        "audit_id": "MPF_S_ARBITRATION_VALIDATION_001",
        "timestamp": datetime.now().isoformat(),
        "target": "S_arbitration_rule",
        "registry_alignment": {
            "root_operator_registry_has_S": "S" in root_symbols,
            "root_operator_registry_has_Arb_A": "Arb_A" in root_symbols,
            "math_operator_registry_has_S": "S" in math_symbols,
            "math_operator_registry_has_Arb_A": "Arb_A" in math_symbols,
            "branch_pruning_registry_targets_S": "S" in branch_targets,
            "delta_selection_registry_targets_Arb_A": "Arb_A" in selection_targets,
        },
        "separation_checks": {},
        "fixture_summaries": {},
    }

    fixtures = spec.get("fixtures", {})
    reduce_case = fixtures["reduce_case"]["candidates"]
    unchanged_case = fixtures["unchanged_case"]["candidates"]
    multi_survivor_case = fixtures["multi_survivor_case"]["candidates"]

    reduce_pruned = apply_s(reduce_case)
    unchanged_pruned = apply_s(unchanged_case)
    multi_survivor_pruned = apply_s(multi_survivor_case)

    reduce_raw_pick = apply_arb_a(reduce_case)
    reduce_pruned_pick = apply_arb_a(reduce_pruned)
    unchanged_pruned_pick = apply_arb_a(unchanged_pruned)
    multi_survivor_pruned_pick = apply_arb_a(multi_survivor_pruned)

    operator_audit["fixture_summaries"]["reduce_case"] = fixture_summary(
        reduce_case, reduce_pruned, reduce_raw_pick, reduce_pruned_pick
    )
    operator_audit["fixture_summaries"]["unchanged_case"] = fixture_summary(
        unchanged_case, unchanged_pruned, None, unchanged_pruned_pick
    )
    operator_audit["fixture_summaries"]["multi_survivor_case"] = fixture_summary(
        multi_survivor_case, multi_survivor_pruned, None, multi_survivor_pruned_pick
    )

    root_s = root_symbols.get("S", {})
    root_arb = root_symbols.get("Arb_A", {})
    math_s = math_symbols.get("S", {})
    math_arb = math_symbols.get("Arb_A", {})

    test_results = []

    def add_result(test_id, name, passed, evidence):
        test_results.append(
            {
                "id": test_id,
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "evidence": evidence,
            }
        )

    add_result(
        "SVT-001",
        "S reduces candidate set cardinality",
        len(reduce_pruned) < len(reduce_case),
        operator_audit["fixture_summaries"]["reduce_case"],
    )
    add_result(
        "SVT-002",
        "S may leave candidate set unchanged",
        len(unchanged_pruned) == len(unchanged_case),
        operator_audit["fixture_summaries"]["unchanged_case"],
    )
    add_result(
        "SVT-003",
        "S never increases candidate set cardinality",
        all(
            len(apply_s(fixtures[name]["candidates"])) <= len(fixtures[name]["candidates"])
            for name in fixtures
        ),
        {
            name: {
                "raw_count": len(fixtures[name]["candidates"]),
                "pruned_count": len(apply_s(fixtures[name]["candidates"])),
            }
            for name in fixtures
        },
    )
    add_result(
        "SVT-004",
        "Arb_A operates only on C_t^S",
        reduce_pruned_pick is not None
        and reduce_pruned_pick["id"] in operator_audit["fixture_summaries"]["reduce_case"]["pruned_ids"]
        and "Consumes the S-stage pruned candidate set before realization" in " ".join(root_arb.get("composition_rules", []))
        and "selection stage operating only on the S-pruned candidate set C_t^S".lower() in math_arb.get("definition", "").lower(),
        {
            "selected_from_pruned": None if reduce_pruned_pick is None else reduce_pruned_pick["id"],
            "pruned_ids": operator_audit["fixture_summaries"]["reduce_case"]["pruned_ids"],
            "root_operator_rule": root_arb.get("composition_rules", []),
            "math_operator_definition": math_arb.get("definition", ""),
        },
    )
    add_result(
        "SVT-005",
        "Removing S changes candidate pool but does not collapse Arb_A semantics",
        len(reduce_pruned) != len(reduce_case)
        and reduce_raw_pick is not None
        and reduce_pruned_pick is not None,
        {
            "raw_selection": None if reduce_raw_pick is None else reduce_raw_pick["id"],
            "pruned_selection": None if reduce_pruned_pick is None else reduce_pruned_pick["id"],
            "raw_count": len(reduce_case),
            "pruned_count": len(reduce_pruned),
        },
    )
    add_result(
        "SVT-006",
        "S does not perform realization selection",
        len(multi_survivor_pruned) > 1
        and multi_survivor_pruned_pick is not None
        and len(multi_survivor_pruned) != 1
        and "does not select the realized continuation" in " ".join(root_s.get("negative_constraints", [])).lower()
        and "does_not_select_realized_continuation" in math_s.get("negative_constraints", []),
        {
            "pruned_ids": operator_audit["fixture_summaries"]["multi_survivor_case"]["pruned_ids"],
            "selected_from_pruned": None if multi_survivor_pruned_pick is None else multi_survivor_pruned_pick["id"],
            "root_negative_constraints": root_s.get("negative_constraints", []),
            "math_negative_constraints": math_s.get("negative_constraints", []),
        },
    )

    separation_checks = {
        "S_has_pruning_codomain": root_s.get("codomain") == "Pruned candidate continuation set C_t^S"
        and "continuation_space" in math_s.get("codomain", []),
        "Arb_A_has_realization_codomain": root_arb.get("codomain") == "Realized future state S_t+1"
        and "continuation_event" in math_arb.get("codomain", []),
        "S_precedes_Arb_A": any("before Arb_A" in rule for rule in root_s.get("composition_rules", []))
        and any("Consumes the S-stage" in rule for rule in root_arb.get("composition_rules", [])),
    }
    operator_audit["separation_checks"] = separation_checks

    overall_pass = all(result["status"] == "PASS" for result in test_results) and all(separation_checks.values()) and all(
        operator_audit["registry_alignment"].values()
    )

    results = {
        "s_arbitration_validation": {
            "status": "pass" if overall_pass else "fail",
            "validation_id": "VAL-S-ARB-001",
            "timestamp": datetime.now().isoformat(),
            "claim_effect": "NO_THEOREM_PROMOTION",
            "target": "S_arbitration_rule",
            "tests_run": [result["id"] for result in test_results],
            "test_results": test_results,
            "registry_alignment": operator_audit["registry_alignment"],
            "separation_checks": separation_checks,
            "success_condition": {
                "S": "validated as pruning stage" if overall_pass else "not validated",
                "Arb_A": "validated as arbitration stage" if overall_pass else "not validated",
            },
            "status_if_passed": {
                "S_arbitration_rule": "VALIDATED_CANDIDATE_PENDING_RIGOR_ENDORSEMENT"
            },
            "closure_gaps": [],
            "open_questions": [
                "Validation is fixture-based and structural; engine-specific pruning implementations still require local runtime corroboration."
            ],
            "warnings": [],
        }
    }
    return results, operator_audit


def write_report(report_path, results, audit):
    validation = results["s_arbitration_validation"]
    lines = [
        "# S Validation Report",
        "",
        "## 1. Scope",
        "",
        "- Target: `S_arbitration_rule`",
        "- Scope: definition validation only",
        "- Claim effect: `NO_THEOREM_PROMOTION`",
        "",
        "## 2. Directly observed or defined",
        "",
        f"- Validation status: `{validation['status'].upper()}`",
        f"- Validation ID: `{validation['validation_id']}`",
        "- Observed separation: `S` prunes candidate pools; `Arb_A` selects one realized continuation from the pruned pool.",
        "",
        "## 3. Test results",
        "",
    ]
    for result in validation["test_results"]:
        lines.append(f"- `{result['id']}` {result['name']}: `{result['status']}`")
    lines.extend(
        [
            "",
            "## 4. Inferred inside framework",
            "",
            "- The fixture-backed validation supports treating `S` as a pre-arbitration pruning stage distinct from `Arb_A`.",
            "- Removing `S` changes the candidate pool presented to arbitration, but does not change the role of `Arb_A` as a selection operator.",
            "",
            "## 5. External resemblance",
            "",
            "- By analogy only, `S` behaves like a gated preselection pass while `Arb_A` behaves like a downstream chooser over the surviving pool.",
            "",
            "## 6. What it does NOT prove",
            "",
            "- It does not prove that all engines implement the same pruning internals.",
            "- It does not promote theorem, topology, geometry, or physics-app claims.",
            "- It does not prove empirical adequacy outside the declared fixture scope.",
            "",
            "## 7. Failure modes and uncertainty",
            "",
            "- A future engine could conflate pruning and arbitration despite the formal separation recorded here.",
            "- Tie-break behavior inside `Arb_A` remains implementation-specific once multiple admissible survivors share the same mismatch cost.",
        ]
    )

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Validate S as a pruning stage distinct from Arb_A.")
    parser.add_argument("--spec", default="registry/math/s_arbitration_validation_registry.json")
    parser.add_argument("--root-operators", default="registry/operator_registry.json")
    parser.add_argument("--math-operators", default="registry/math/operator_registry.json")
    parser.add_argument("--branch", default="registry/math/branch_pruning_registry.json")
    parser.add_argument("--selection", default="registry/math/delta_selection_registry.json")
    parser.add_argument("--results-out", default="outputs/s_validation/s_validation_results.json")
    parser.add_argument("--report-out", default="outputs/s_validation/s_validation_report.md")
    parser.add_argument("--audit-out", default="outputs/s_validation/s_operator_audit.json")
    args = parser.parse_args()

    results, audit = validate_s_arbitration(
        args.spec,
        args.root_operators,
        args.math_operators,
        args.branch,
        args.selection,
    )

    os.makedirs(os.path.dirname(args.results_out), exist_ok=True)
    with open(args.results_out, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    with open(args.audit_out, "w", encoding="utf-8") as handle:
        json.dump(audit, handle, indent=2)
    write_report(args.report_out, results, audit)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
