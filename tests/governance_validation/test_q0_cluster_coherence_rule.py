from ._helpers import load_json, sha256_file


def test_q0_cluster_coherence_rule_is_live_and_narrow():
    rule = load_json("governance/core_rules/GOVERNANCE_Q0_CLUSTER_COHERENCE_001.json")

    assert rule["rule_id"] == "GOVERNANCE_Q0_CLUSTER_COHERENCE_001"
    assert rule["title"] == "Q0 Resolution Cluster Coherence"
    assert rule["status"] == "LIVE"
    assert rule["authority_type"] == "CORE_GOVERNANCE_RULE"
    assert rule["scope"] == "Governance cluster selection and resolution packet construction for Q0_COMPETING_AUTHORITY_AND_WRITE_PATHS only."
    assert rule["effect"] == "Constrains cluster selection and packet construction; does not authorize any inventoried surface."
    assert "Queue proximity alone does not establish cluster coherence" in rule["statement"]
    assert rule["constraints"] == [
        "Every included ambiguity must have a documented relationship to the same governed authority domain.",
        "Every excluded neighboring ambiguity must remain unchanged.",
        "A cluster must be small enough to validate and roll back independently.",
        "Cross-domain ambiguity records must not be combined merely because they share a candidate file or registry.",
        "Selection creates no authority and resolves no ambiguity.",
    ]
    assert rule["prohibited_interpretations"] == [
        "queue proximity means cluster membership",
        "selection means authority",
        "selection means resolution",
        "a bounded cluster may ignore cross-domain evidence",
        "packet construction may promote live authority",
    ]
    assert rule["source_patch_id"] == "PATCH_GOVERNANCE_Q0_CLUSTER_SELECTION_AND_RESOLUTION_PACKET_006"
    assert sha256_file("governance/core_rules/GOVERNANCE_Q0_CLUSTER_COHERENCE_001.json") == rule["hash"] if "hash" in rule else True

