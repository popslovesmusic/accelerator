from ._helpers import load_json


def test_inventory_core_rule_is_live_and_narrow():
    rule = load_json("governance/core_rules/GOVERNANCE_INVENTORY_TRANSITIONAL_EVIDENCE_001.json")

    assert rule["rule_id"] == "GOVERNANCE_INVENTORY_TRANSITIONAL_EVIDENCE_001"
    assert rule["status"] == "LIVE"
    assert rule["authority_type"] == "CORE_GOVERNANCE_RULE"
    assert rule["scope"] == "Governance inventory artifacts and inventory-derived reports only."
    assert rule["effect"] == "Constrains what inventories may do; does not authorize any inventoried surface."
    assert "must not create, replace, merge, supersede, activate, or delete governance authority" in rule["statement"]
    assert rule["constraints"] == [
        "Inventory records are descriptive, not constitutive.",
        "Observed live authority remains live only because of its existing authority source, not because the inventory lists it.",
        "Proposals remain proposals.",
        "Historical surfaces remain historical.",
        "Generated views remain derived and non-authoritative.",
        "Ambiguous surfaces remain unresolved.",
        "Inventory completeness must not be inferred from successful artifact generation.",
        "Inventory registration must be additive.",
    ]
    assert rule["prohibited_interpretations"] == [
        "listed means authorized",
        "classified means resolved",
        "referenced means adopted",
        "generated means authoritative",
        "zero conflicts means complete",
        "zero unknowns means unambiguous",
        "inventory publication means live governance",
    ]

