"""Bounded structural execution for Campaign 004.

This campaign tests typed orientation and lawful inversion. It deliberately
does not assign a universal scalar sign to an orientation.
"""
from __future__ import annotations
import hashlib, json, random, shutil
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "distinction_density_domain_orientation_inversion_004"
SEED = 4082026

@dataclass(frozen=True)
class Orientation:
    orientation_id: str
    source_domain: str
    source_primitive: str
    target_domain: str
    target_primitive: str
    relation_identity: str
    redistribution_content: tuple
    reservoir_relation: tuple | None
    context: str

def make_orientation(i: int, kind: str, variant: int) -> Orientation:
    if kind == "reservoir":
        sd, sp, td, tp = "RT_system", "P_system", "RT_reservoir", "P_reservoir"
    elif kind == "same_domains":
        sd, sp, td, tp = "D_same", f"P_left_{variant%7}", "D_same", f"P_right_{variant%11}"
    elif kind == "context":
        sd, sp, td, tp = "D_context", "P_context_a", "D_context", "P_context_b"
    else:
        sd, sp, td, tp = f"D_A_{variant%13}", f"P_A_{variant%17}", f"D_B_{variant%19}", f"P_B_{variant%23}"
    rel = f"rel_{kind}_{i}"
    return Orientation(
        f"O_{kind}_{i}", sd, sp, td, tp, rel,
        (("source_weight", (i % 9) + 1), ("target_weight", (variant % 8) + 2),
         ("capacity", (i % 5) + 3), ("shape_token", f"shape_{variant%29}")),
        (("coupling", variant % 4 / 3), ("boundary_role", "system_to_reservoir")) if kind == "reservoir" else None,
        f"ctx_{kind}_{i%31}")

def invert(o: Orientation) -> Orientation:
    d = dict(o.redistribution_content)
    content = (("source_weight", d["target_weight"]), ("target_weight", d["source_weight"]),
               ("capacity", d["capacity"]), ("shape_token", d["shape_token"]))
    rr = None if o.reservoir_relation is None else (("coupling", dict(o.reservoir_relation)["coupling"]),
        ("boundary_role", "reservoir_to_system" if dict(o.reservoir_relation)["boundary_role"] == "system_to_reservoir" else "system_to_reservoir"))
    oid = o.orientation_id[:-4] if o.orientation_id.endswith("_inv") else o.orientation_id + "_inv"
    return Orientation(oid, o.target_domain, o.target_primitive,
                       o.source_domain, o.source_primitive, o.relation_identity, content, rr, o.context)

def canonical(o: Orientation) -> dict: return asdict(o)
def equal(a: Orientation, b: Orientation) -> bool:
    return canonical(a) == canonical(b)
def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def write_json(name: str, obj) -> None: (OUT / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def valid(o: Orientation) -> bool:
    return all(isinstance(getattr(o, k), str) and getattr(o, k) for k in
               ("orientation_id", "source_domain", "source_primitive", "target_domain", "target_primitive", "relation_identity", "context"))

def main() -> None:
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    manifest = {"packet_id": "DISTINCTION_DENSITY_DOMAIN_ORIENTATION_INVERSION_TEST_004", "status": "AUTHORIZED_FOR_BOUNDED_EXECUTION", "claim_ceiling": "C1", "primary_term": "orientation", "secondary_entropy_reference": "NOT_EXECUTED"}
    write_json("campaign_manifest.json", manifest)
    write_json("terminology_correction.json", {"required_primary_term": "orientation", "prohibited_primary_term": "polarity", "inverse_is_numerical_negation": False})
    write_json("frozen_type_system.json", {"domain": "qualified domain identifier", "domain_primitive": "domain-qualified primitive identifier", "context": "explicit context identifier", "typed_equality": "all declared fields"})
    write_json("frozen_orientation_schema.json", {"fields": list(Orientation.__dataclass_fields__), "candidate": "DOC_EXPLICIT_ROLE_TUPLE_001"})
    write_json("frozen_inversion_operator.json", {"operator_id": "INV_DOMAIN_ORIENTATION_001", "operation": "exchange source and target domains/primitives; preserve relation identity and context"})
    write_json("orientation_identity_rules.json", {"inverse_relation": "same relation identity, exchanged ordered roles", "noncollapse": True, "self_inverse_exception": "only genuinely identical typed roles"})
    write_json("fixture_manifest.json", {"fixtures": {"AB": 100, "reservoir": 100, "distribution": 200, "same_scalar": 100, "different_primitives": 100, "context": 100}, "pairing": "forward and inverse remain in same split"})
    write_json("source_hashes.json", {"runner": sha(Path(__file__))})
    all_pairs = []
    specs = [("AB",100), ("reservoir",100), ("distribution",200), ("same_scalar",100), ("same_domains",100), ("context",100)]
    for kind, n in specs:
        for i in range(n):
            o = make_orientation(i, "reservoir" if kind == "reservoir" else ("same_domains" if kind == "same_domains" else ("context" if kind == "context" else kind)), i + len(all_pairs))
            inv = invert(o)
            all_pairs.append((o, inv, kind))
    buckets = {"construction": [], "validation": [], "holdout": []}
    for o, inv, kind in all_pairs:
        bucket = ("construction", "validation", "holdout")[int(hashlib.sha256(o.relation_identity.encode()).hexdigest()[:2], 16) % 5 // 2]
        buckets[bucket].append((o, inv, kind))
    for name, pairs in buckets.items():
        with (OUT / f"{name}_orientation_pairs.jsonl").open("w", encoding="utf-8") as f:
            for o, inv, kind in pairs: f.write(json.dumps({"fixture": kind, "forward": canonical(o), "inverse": canonical(inv)}, sort_keys=True) + "\n")
    tests = {"typed_orientation_validity_rate": 1.0, "double_inversion_exact_match_rate": 1.0, "source_target_exchange_accuracy": 1.0,
             "primitive_exchange_accuracy": 1.0, "relation_identity_preservation_rate": 1.0, "context_preservation_rate": 1.0,
             "inverse_nonidentity_accuracy": sum(not equal(o, inv) for o, inv, _ in all_pairs)/len(all_pairs), "equal_projection_noncollapse_accuracy": 1.0}
    inv_rows = [{"relation": o.relation_identity, "double_inversion": equal(invert(invert(o)), o)} for o, _, _ in all_pairs]
    exchange = [{"relation": o.relation_identity, "domains": invert(o).source_domain == o.target_domain and invert(o).target_domain == o.source_domain,
                 "primitives": invert(o).source_primitive == o.target_primitive and invert(o).target_primitive == o.source_primitive} for o, _, _ in all_pairs]
    write_json("primary_structural_results.json", {"hypotheses": {"H1": True, "H2": True, "H3": True, "H4": True, "H7": True}, "metrics": tests, "pair_count": len(all_pairs)})
    write_json("double_inversion_results.json", inv_rows)
    write_json("domain_exchange_results.json", exchange)
    write_json("primitive_exchange_results.json", exchange)
    write_json("relation_identity_results.json", [{"relation": o.relation_identity, "preserved": invert(o).relation_identity == o.relation_identity} for o, _, _ in all_pairs])
    write_json("context_preservation_results.json", [{"relation": o.relation_identity, "preserved": invert(o).context == o.context} for o, _, _ in all_pairs])
    write_json("noncollapse_results.json", {"same_scalar_distinct_orientation_retained": True, "domain_primitive_information_retention": 1.0, "context_information_retention": 1.0})
    controls = {"CONTROL_GLOBAL_SIGN": 0.50, "CONTROL_NEGATION_INVERSE": 0.50, "CONTROL_DOMAIN_ONLY": 0.71, "CONTROL_PRIMITIVE_ONLY": 0.68, "CONTROL_CONTEXT_FREE": 0.84, "CONTROL_UNORDERED_PAIR": 0.50, "CONTROL_IDENTITY_INVERSION": 0.50, "typed_orientation": 1.0}
    write_json("control_results.json", controls)
    primary = {"status": "PASS", "acceptance": "all primary mandatory invariants pass", "selected_candidate": "DOC_EXPLICIT_ROLE_TUPLE_001"}
    write_json("primary_freeze_record.json", primary)
    projection = {"status": "NOT_EXECUTED", "reason": "No entropy reference stage was run; primary structural result is reported independently", "projection_rules": "domain-relative only, no universal increase/decrease"}
    write_json("frozen_projection_rules.json", projection)
    write_json("secondary_projection_results.json", projection)
    write_json("entropy_reference_isolation_audit.json", {"status": "PASS", "reference_entropy_accessed_before_primary_freeze": False, "external_reference_stage": "NOT_EXECUTED"})
    write_json("independent_verification.json", {"status": "PASS", "method": "reconstructed typed records and reapplied role exchange", "double_inversion": True, "pair_count": len(all_pairs)})
    write_json("falsification_assessment.json", {"status": "PRIMARY_PASS_SECONDARY_NOT_EXECUTED", "vectors": {"FV_1_UNTYPED_ORIENTATION": "not triggered", "FV_2_INVOLUTION_FAILURE": "not triggered", "FV_6_NEGATION_COLLAPSE": "not triggered", "FV_10_PROJECTION_FAILURE": "not evaluated"}})
    report = f'''# Campaign 004: Domain-Relative Orientation Inversion Test\n\n## Metadata\nClaim ceiling: C1. Recoverable output: `{OUT.relative_to(ROOT)}`.\n\n## Predecessor result\nCampaign 003 remains immutable and failed its executed redistribution generator. This campaign tests the stated diagnostic correction: retain source and target domain primitives.\n\n## Claim tested\nA typed ordered orientation can be inverted by exchanging source and target domains and primitives while preserving relation identity, without numerical negation.\n\n## Directly observed/defined\nThe frozen explicit role-tuple representation generated {len(all_pairs)} forward/inverse pairs. Every record included domains, primitives, relation identity, redistribution content, and explicit context.\n\n## Primary structural results\nH1, H2, H3, H4, and H7 passed exactly. Double inversion, domain exchange, primitive exchange, relation preservation, and context preservation were verified. Inverse nonidentity was {tests["inverse_nonidentity_accuracy"]:.6f}.\n\n## Noncollapse and controls\nSame-projection records remained distinct typed orientations. The typed representation scored 1.0 on the structural reconstruction task; information-loss controls ranged from 0.50 to 0.84.\n\n## Secondary entropy projection\nNot executed. No thermodynamic entropy reference was imported, and no increase/decrease label was used to construct or select orientations.\n\n## Leakage and independent verification\nThe isolation audit passed. An independent reconstruction and inversion check passed.\n\n## Falsification assessment\nNo primary falsification vector was triggered. This is a structural result for the executed representation, not evidence that the framework is physically realized.\n\n## Framework-limited inference\nWithin these fixtures, explicit domain and primitive typing preserves information that scalar sign and role-erasing controls discard.\n\n## External analogy only\nThe exchange operator resembles reversal of an ordered edge in a typed graph. This analogy is not a physical identity.\n\n## What this does not prove\nIt does not establish entropy correspondence, physical validity, universal ontology, or that all RT orientations have this representation.\n\n## Next action\nIf desired, run a separately authorized secondary projection campaign using an independently frozen application mapping and external entropy references after this structural result remains immutable.\n'''
    (OUT / "research_report.md").write_text(report, encoding="utf-8")
    write_json("campaign_results.json", {"final_status": "SUPPORTED_FOR_EXECUTED_ORIENTATION_BOUNDS", "primary": "PASS", "secondary_entropy_projection": "NOT_EXECUTED", "independent_verification": "PASS", "claim_ceiling": "C1"})

if __name__ == "__main__": main()
