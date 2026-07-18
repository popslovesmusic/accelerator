from ._helpers import ROOT, load_json, sha256_file


def test_patch_063_records_rt_aer_namespace_resolution():
    patch = load_json("registry/governance/patches/PATCH_PI_RT_CALCULUS_063.json")
    authority = load_json("docs/governance/rt_aer_namespace_authority_063.json")
    report = load_json("outputs/governance_inventory/rt_aer_namespace_compliance_report_063.json")
    theorem_registry = load_json("registry/theorem_registry.json")
    lexicon_gap_queue_text = (ROOT / "registry/lexicon_gap_queue.json").read_text(encoding="utf-8")

    assert patch["patch_id"] == "PATCH_PI_RT_CALCULUS_063"
    assert patch["status"] == "APPLIED"
    assert patch["rt_core_modified"] is False
    assert patch["new_numeric_quantity_promoted"] is False
    assert patch["core_rule"]["id"] == "RT_AER_NAMESPACE_063_001"

    assert authority["canonical_definition"]["RT"] == "Real Truth"
    assert authority["canonical_definition"]["AER"] == "Affect-Effect Ratio"
    assert authority["canonical_definition"]["deprecation_rule"] == (
        "RTen is deprecated and forbidden in new canonical material."
    )

    summary = report["classification_summary"]
    assert summary["CANONICAL_NAMESPACE_AUTHORITY"] == 2
    assert summary["PROSPECTIVELY_CLARIFIED_SURFACE"] == 1
    assert summary["TERM_INDUCTED_PENDING_VALIDATION"] == 1
    assert summary["DEPRECATED_TERM_OCCURRENCES"] == 0
    assert report["scan_summary"]["rten_occurrences_found"] == 0

    semantic_targets = {entry["semantic_key"]: entry for entry in theorem_registry["semantic_targets"]}
    assert semantic_targets["AFFECT_EFFECT_RATIO"]["canonical_expression"].startswith("AER(phi) :=")
    assert "must use AER rather than RT or RTen" in semantic_targets["AFFECT_EFFECT_RATIO"]["notes"]

    assert '"term": "AER"' in lexicon_gap_queue_text or '"term":  "AER"' in lexicon_gap_queue_text
    assert '"status": "RESOLVED_TO_CANONICAL"' in lexicon_gap_queue_text or '"status":  "RESOLVED_TO_CANONICAL"' in lexicon_gap_queue_text or '"status": "GAP_OPEN"' in lexicon_gap_queue_text or '"status":  "GAP_OPEN"' in lexicon_gap_queue_text
    assert '"Affect-Effect Ratio"' in lexicon_gap_queue_text


def test_patch_063_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["registry/governance/patches/PATCH_PI_RT_CALCULUS_063.json"] == (
        sha256_file("registry/governance/patches/PATCH_PI_RT_CALCULUS_063.json").upper()
    )
    assert hash_registry["hashes"]["docs/governance/rt_aer_namespace_authority_063.json"] == (
        sha256_file("docs/governance/rt_aer_namespace_authority_063.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/rt_aer_namespace_compliance_report_063.json"] == (
        sha256_file("outputs/governance_inventory/rt_aer_namespace_compliance_report_063.json").upper()
    )
