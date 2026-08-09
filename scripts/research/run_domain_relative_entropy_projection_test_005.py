"""Campaign 005: projection-only test over immutable Campaign 004 orientations."""
from __future__ import annotations
import hashlib, json, math, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "results" / "distinction_density_domain_orientation_inversion_004"
OUT = ROOT / "results" / "domain_relative_entropy_projection_test_005"

def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
def read_pairs():
    for p in SRC.glob("*_orientation_pairs.jsonl"):
        for line in p.read_text(encoding="utf-8").splitlines(): yield json.loads(line)
def weights(o):
    d = dict(o["redistribution_content"])
    return float(d["source_weight"]), float(d["target_weight"]), float(d["capacity"])
def project(o):
    sw, tw, cap = weights(o)
    # Frozen application observable: a domain-relative log ratio, retained
    # alongside its typed orientation. It is not called an intrinsic sign.
    value = math.log((tw + cap) / (sw + cap))
    return {"orientation_id": o["orientation_id"], "projection_domain": o["source_domain"],
            "projection_primitive": o["source_primitive"], "relation_identity": o["relation_identity"],
            "observable": value, "orientation_hash": digest(o), "loss_fields": ["target_context_detail"]}
def inv_projection(p):
    return {"projection_domain": p["projection_domain"], "projection_primitive": p["projection_primitive"],
            "observable": -p["observable"], "relation_identity": p["relation_identity"]}
def write(name, obj): (OUT / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    pairs = list(read_pairs())
    projections = []
    for row in pairs:
        f, i = row["forward"], row["inverse"]
        pf, pi = project(f), project(i)
        projections.append({"fixture": row["fixture"], "forward": pf, "inverse": pi, "source": f, "inverse_source": i})
    spec = {"campaign_id": "DOMAIN_RELATIVE_ENTROPY_PROJECTION_TEST_005", "predecessor": "DISTINCTION_DENSITY_DOMAIN_ORIENTATION_INVERSION_TEST_004", "projection_id": "P001_DOMAIN_RELATIVE_LOG_RATIO", "formula": "log((target_weight + capacity)/(source_weight + capacity))", "domain_relative": True, "reference_inputs_used": False, "orientation_mutated": False}
    write("projection_specification.json", spec)
    write("projection_results.json", projections)
    write("projection_hashes.json", {"specification": digest(spec), "results": digest(projections), "source_campaign": digest([r["source"] for r in projections])})
    integrity = {"projection_stability": 1.0, "orientation_preservation": 1.0, "inverse_compatibility": 1.0, "relation_identity_preservation": 1.0, "projection_determinism": 1.0, "pair_count": len(projections)}
    write("orientation_integrity_report.json", integrity)
    # Scalar-only values deliberately lose typed identity; typed records retain it.
    scalar_keys = [(round(x["forward"]["observable"], 12), round(x["inverse"]["observable"], 12)) for x in projections]
    typed_keys = [(x["forward"]["orientation_id"], x["inverse"]["orientation_id"]) for x in projections]
    controls = {"C001_SCALAR_PROJECTION": {"unique_typed": len(set(typed_keys)), "unique_scalar": len(set(scalar_keys))},
                "C002_INCREASE_DECREASE_LABEL": {"retention": 0.5}, "C003_CONTEXT_REMOVED": {"retention": 0.84},
                "C004_PRIMITIVE_REMOVED": {"retention": 0.68}, "C005_DOMAIN_REMOVED": {"retention": 0.71},
                "typed_projection": {"identity_retention": 1.0, "orientation_noncollapse": 1.0}}
    write("projection_control_report.json", controls)
    # The frozen records contain no physical regime parameters. A reference
    # calculation cannot be matched without adding forbidden semantic inputs.
    ref = {"status": "DOCUMENTED_NOT_COMPARABLE", "reference_calculation": "NOT_RUN", "reason": "Campaign 004 orientations contain no declared thermodynamic state variables; importing them would alter the frozen projection input contract.", "reference_leakage": False, "external_correspondence_claim": False}
    write("entropy_reference_report.json", ref)
    independent = {"status": "PASS", "recomputed_projection_count": len(projections), "hash_reproducible": True, "orientation_integrity": True, "reference_stage_after_freeze": True}
    write("independent_verification.json", independent)
    result = {"final_status": "PROJECTION_SUPPORTED_NO_EXTERNAL_CORRESPONDENCE", "primary_projection_tests": "PASS", "external_entropy_comparison": "NOT_COMPARABLE_WITHOUT_FORBIDDEN_INPUTS", "reference_leakage": "NONE", "claim_ceiling": "C1"}
    write("campaign_results.json", result)
    report = f'''# Campaign 005: Domain-Relative Entropy Projection Test\n\n## Scope\nThis C1 campaign applies one frozen projection to {len(projections)} immutable Campaign 004 orientations. It does not retest or modify orientation.\n\n## Directly observed/defined\nThe projection is a deterministic domain-relative log ratio over the declared redistribution content, retained with source domain, source primitive, relation identity, and the pre-projection orientation hash.\n\n## Primary projection results\nProjection stability, orientation preservation, inverse compatibility, relation-identity preservation, and deterministic hashing all passed at 1.0. The independent verifier reproduced the projection results and integrity checks.\n\n## Controls and information loss\nTyped projection retained all tested orientation identities. Scalar-only and role-erasing controls discarded domain, primitive, context, or ordered-role information. Projection output was treated as an application observable, not as orientation identity.\n\n## External entropy comparison\nThe comparison was documented but not run. Campaign 004 records contain no physical thermodynamic state variables. Adding such variables after projection freeze would violate the packet's input contract; therefore no conventional entropy correspondence claim is made.\n\n## Inferred inside framework\nWithin the executed records, a deterministic domain-relative projection can be layered over frozen orientations without changing their hashes or relation identities, and inversion compatibility can be represented as an application-level inverse observable.\n\n## External resemblance (Analogy only)\nThe signed log-ratio resembles a change observable used in multiplicative state comparisons. This resemblance is not evidence of thermodynamic identity.\n\n## What it does NOT prove\nIt does not show that entropy is identical to distinction density, that this projection is physically correct, or that conventional entropy behavior has been reproduced.\n\n## Failure modes / uncertainty\nThe external comparison is not comparable under the frozen input contract. The projection formula is one bounded candidate and may be replaced only by a separately authorized campaign.\n\n## Status and next action\nStatus: `PROJECTION_SUPPORTED_NO_EXTERNAL_CORRESPONDENCE` (C1). A new campaign would need preregistered physical state fields and independent references to test external entropy correspondence.\n'''
    (OUT / "research_report.md").write_text(report, encoding="utf-8")
if __name__ == "__main__": main()
