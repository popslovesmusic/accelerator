"""Independent provisional P127/P128 executable reimplementation.

This module implements only the executable semantics authorized by
RT_P127_P128_STANDIN_SEMANTICS_ADOPTION_001. Its evidence ceiling is C1.
"""


def _relation_is_typed(record):
    return record.get("relation_type") == "SourceRelation"


def _contexts_are_aligned(record):
    left = record.get("context")
    right = record.get("target_context")
    return isinstance(left, str) and isinstance(right, str) and bool(left) and left == right


def _profile_is_declared(record, environment):
    return record.get("profile") in environment


def _witness_is_bound(record):
    witness = record.get("witness")
    return isinstance(witness, dict) and witness.get("token") == record.get("source_payload")


def _history_is_compatible(record):
    sequence = record.get("history")
    if not isinstance(sequence, list) or len(sequence) == 0:
        return False
    if not all(isinstance(entry, dict) and "step" in entry and "state" in entry for entry in sequence):
        return False
    positions = [entry["step"] for entry in sequence]
    if not all(isinstance(position, int) and not isinstance(position, bool) for position in positions):
        return False
    if not all(first < second for first, second in zip(positions, positions[1:])):
        return False
    return sequence[-1]["state"] == record.get("target")


def candidate_representable(record, environment):
    """Evaluate bounded representability with the authorized precedence."""
    # P127 / adopted typed_relation_rule.
    if not _relation_is_typed(record):
        return "REJECT_TYPE"
    # P127 / adopted context_rule.
    if not _contexts_are_aligned(record):
        return "REJECT_CONTEXT"
    # P127 / adopted profile_rule.
    if not _profile_is_declared(record, environment):
        return "REJECT_PROFILE"
    # P127 / adopted witness_rule.
    if not _witness_is_bound(record):
        return "REJECT_WITNESS"
    # P127 / adopted history_rule.
    if not _history_is_compatible(record):
        return "REJECT_HISTORY"
    # P127 / adopted representability_success.
    return "REPRESENTABLE"


def _threshold_result(record, environment):
    profile = record.get("profile")
    if profile not in environment:
        # P128 / adopted profile_rule.
        return "REJECT_PROFILE"

    amount = record.get("distinction")
    numeric = isinstance(amount, (int, float)) and not isinstance(amount, bool)
    if not numeric or amount <= 0:
        # P128 / adopted distinction_rule invalid_or_nonpositive result.
        return "REJECT_DISTINCTION"
    if amount <= environment[profile]:
        # P128 / adopted distinction_rule less-than-or-equal threshold result.
        return "REJECT_SUBTHRESHOLD"
    # P128 / adopted distinction_rule success result.
    return "NON_COLLAPSED"


def candidate_noncollapsed(record, environment):
    """Evaluate bounded non-collapse against the declared profile threshold."""
    return _threshold_result(record, environment)


def candidate_admissible(record, environment):
    """Compose the two authorized bounded success predicates."""
    representability = candidate_representable(record, environment)
    separation = candidate_noncollapsed(record, environment)
    # Adoption authority / admissibility_rule.
    return representability == "REPRESENTABLE" and separation == "NON_COLLAPSED"
