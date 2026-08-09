"""Fail-closed validator for typed S/Arb_A engine traces.

This adapter validates an explicit trace supplied by an engine wrapper. It does
not infer candidate-level semantics from aggregate metrics and never executes an
engine itself.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_EVENTS = {
    "candidate_pool_before_S",
    "candidate_pool_after_S",
    "removed_candidate_reasons",
    "arb_a_input_pool",
    "arb_a_output_selection_or_tie_set",
    "tie_policy_identifier",
    "admissibility_preservation_check",
    "candidate_identity_provenance",
}


def validate_trace(trace: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    invariants = trace.get("invariants", {})
    arb_output = trace.get("arb_a_output", {})

    if trace.get("trace_schema_version") != "1.0.0":
        errors.append("trace_schema_version must equal 1.0.0")
    if not trace.get("engine_id"):
        errors.append("engine_id is required")
    if not trace.get("fixture_id"):
        errors.append("fixture_id is required")

    events = set(trace.get("trace_events", []))
    missing_events = sorted(REQUIRED_EVENTS - events)
    if missing_events:
        errors.append(f"missing required trace events: {missing_events}")

    before = trace.get("s_input_ids", [])
    after = trace.get("s_output_ids", [])
    arb_input = trace.get("arb_a_input_ids", [])
    selected = arb_output.get("selected_id")
    tie_set = arb_output.get("tie_set", [])

    if not isinstance(before, list) or not isinstance(after, list) or not isinstance(arb_input, list):
        errors.append("candidate ID pools must be arrays")
    else:
        if len(after) > len(before):
            errors.append("S increased candidate cardinality")
        if after != arb_input:
            errors.append("Arb_A input pool does not exactly equal S output pool")
        if selected is not None and selected not in arb_input:
            errors.append("Arb_A selected an ID absent from its input pool")

    if not arb_output.get("policy_id"):
        errors.append("tie policy identifier is required")
    if not isinstance(tie_set, list):
        errors.append("tie_set must be an array")
    if len(tie_set) > 1 and not arb_output.get("policy_id"):
        errors.append("non-singleton tie set lacks an explicit policy")

    if invariants.get("s_does_not_increase_cardinality") is not True:
        errors.append("s_does_not_increase_cardinality must be true")
    if invariants.get("arb_a_consumes_s_output") is not True:
        errors.append("arb_a_consumes_s_output must be true")
    if invariants.get("selected_id_is_in_arb_a_input_or_null") is not True:
        errors.append("selected_id_is_in_arb_a_input_or_null must be true")
    if invariants.get("tie_policy_explicit") is not True:
        errors.append("tie_policy_explicit must be true")

    provenance = trace.get("runtime_provenance", {})
    if trace.get("evidence_class") == "REFERENCE_FIXTURE_NOT_ENGINE_EVIDENCE":
        warnings.append("reference fixture validated; no engine evidence is established")
    elif not all(provenance.get(k) for k in ("config_sha256", "tool_sha256", "run_id")):
        errors.append("engine traces require config_sha256, tool_sha256, and run_id provenance")

    return {
        "adapter_id": "ENGINE_TRACE_ADAPTER_SPEC_20260730_005",
        "status": "PASS" if not errors else "FAIL",
        "claim_effect": "NO_THEOREM_PROMOTION",
        "errors": errors,
        "warnings": warnings,
        "engine_evidence": trace.get("evidence_class") != "REFERENCE_FIXTURE_NOT_ENGINE_EVIDENCE",
        "validated_fixture_id": trace.get("fixture_id"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a typed S/Arb_A engine trace.")
    parser.add_argument("--trace", required=True, help="JSON trace emitted by an engine adapter.")
    parser.add_argument("--report-out", help="Optional JSON validation report path.")
    args = parser.parse_args()

    trace = json.loads(Path(args.trace).read_text(encoding="utf-8"))
    result = validate_trace(trace)
    rendered = json.dumps(result, indent=2)
    if args.report_out:
        out = Path(args.report_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
