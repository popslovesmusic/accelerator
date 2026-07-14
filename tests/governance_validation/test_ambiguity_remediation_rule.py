from ._helpers import (
    EXPECTED_REMEDIATION_ORDER_RULE_HASH,
    EXPECTED_REMEDIATION_ORDER_RULE_ID,
    EXPECTED_REMEDIATION_ORDER_RULE_PATH,
    load_json,
    sha256_file,
)


def test_remediation_order_rule_is_live_narrow_and_non_authoritative():
    rule = load_json(EXPECTED_REMEDIATION_ORDER_RULE_PATH)

    assert rule["rule_id"] == EXPECTED_REMEDIATION_ORDER_RULE_ID
    assert rule["status"] == "LIVE"
    assert rule["authority_type"] == "CORE_GOVERNANCE_RULE"
    assert rule["authority_effect"] == "NONE"
    assert rule["scope"] == "Governance ambiguity classification and remediation queue ordering only."
    assert "Queue position does not resolve an ambiguity or confer authority." in rule["statement"]
    assert rule["constraints"] == [
        "Queue ordering is deterministic and evidence-backed.",
        "Queue position does not change authority state.",
        "A later resolution patch is required to resolve any ambiguity.",
        "The remediation queue is non-authoritative transitional evidence.",
    ]
    assert rule["prohibited_interpretations"] == [
        "queue position means resolved",
        "queue position means approved",
        "classification creates authority",
        "ordering changes surface status",
    ]
    assert rule["source_patch_id"] == "PATCH_GOVERNANCE_AMBIGUITY_RISK_CLASSIFICATION_AND_REMEDIATION_QUEUE_005"
    assert sha256_file(EXPECTED_REMEDIATION_ORDER_RULE_PATH) == EXPECTED_REMEDIATION_ORDER_RULE_HASH

