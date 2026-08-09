"""Provisional executable P127/P128 candidate for finite Notebook 26 comparison.

The rules in this module are provisional executable semantics authorized by
RT_P127_P128_STANDIN_SEMANTICS_ADOPTION_001. They are bounded to C1 execution
reconstruction and are not a canonical mathematical interpretation.
"""


def candidate_representable(record, environment):
    """Return the authorized bounded representability result for a record."""
    # P127; adopted typed_relation_rule: relation_type must be SourceRelation.
    if record.get("relation_type") != "SourceRelation":
        return "REJECT_TYPE"

    # P127; adopted context_rule: nonempty string contexts must be equal.
    context = record.get("context")
    target_context = record.get("target_context")
    if (
        not isinstance(context, str)
        or not isinstance(target_context, str)
        or not context
        or context != target_context
    ):
        return "REJECT_CONTEXT"

    # P127; adopted profile_rule: profile validity is environment membership.
    if record.get("profile") not in environment:
        return "REJECT_PROFILE"

    # P127; adopted witness_rule represents projected and typed witness binding.
    witness = record.get("witness")
    if not isinstance(witness, dict) or witness.get("token") != record.get("source_payload"):
        return "REJECT_WITNESS"

    # P127; adopted history_rule represents history presence and trace compatibility.
    history = record.get("history")
    if not isinstance(history, list) or not history:
        return "REJECT_HISTORY"
    if not all(isinstance(item, dict) and "step" in item and "state" in item for item in history):
        return "REJECT_HISTORY"
    steps = [item["step"] for item in history]
    if not all(isinstance(step, int) and not isinstance(step, bool) for step in steps):
        return "REJECT_HISTORY"
    if not all(left < right for left, right in zip(steps, steps[1:])):
        return "REJECT_HISTORY"
    if history[-1]["state"] != record.get("target"):
        return "REJECT_HISTORY"

    # P127; adopted representability_success for the admitted bounded instance.
    return "REPRESENTABLE"


def candidate_noncollapsed(record, environment):
    """Return the authorized bounded non-collapse result for a record."""
    # P128; adopted profile_rule supplies epsilon_C from environment[profile].
    profile = record.get("profile")
    if profile not in environment:
        return "REJECT_PROFILE"

    # P128; adopted distinction_rule rejects invalid or nonpositive distinction.
    distinction = record.get("distinction")
    if (
        not isinstance(distinction, (int, float))
        or isinstance(distinction, bool)
        or distinction <= 0
    ):
        return "REJECT_DISTINCTION"

    # P128; adopted distinction_rule requires distinction_C(p,q) > epsilon_C.
    if distinction <= environment[profile]:
        return "REJECT_SUBTHRESHOLD"

    # P128; adopted distinction_rule success result.
    return "NON_COLLAPSED"


def candidate_admissible(record, environment):
    """Return true exactly when both adopted bounded predicates succeed."""
    # Adoption authority: admissibility_rule requires both declared successes.
    return (
        candidate_representable(record, environment) == "REPRESENTABLE"
        and candidate_noncollapsed(record, environment) == "NON_COLLAPSED"
    )
