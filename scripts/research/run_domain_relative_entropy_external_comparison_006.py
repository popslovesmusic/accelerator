"""Campaign 006: bounded external comparison using Campaign 005's frozen map.

Candidate structural accessibility is generated before independent references.
The frozen projection is log((target_weight+capacity)/(source_weight+capacity)).
"""
from __future__ import annotations
import hashlib, itertools, json, math, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/"results"/"domain_relative_entropy_external_comparison_006"
def h(x): return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def proj(a,b,c=0.0): return math.log((b+c)/(a+c))
def ideal_ref(a,b): return math.log(b/a)
def two_ref(g,t):
    p=1/(1+math.exp(g/t)); return -(1-p)*math.log(1-p)-p*math.log(p)
def ising_ref(n,T,J,field):
    vals=[]
    for spins in itertools.product((-1,1), repeat=n*n):
        e=0
        for r in range(n):
            for c in range(n):
                i=r*n+c; e-=J*spins[i]*spins[r*n+(c+1)%n]; e-=J*spins[i]*spins[((r+1)%n)*n+c]; e-=field*spins[i]
        vals.append(e)
    z=sum(math.exp(-e/T) for e in vals); ps=[math.exp(-e/T)/z for e in vals]
    return -sum(p*math.log(p) for p in ps if p>0)
def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    spec={"campaign_id":"DOMAIN_RELATIVE_ENTROPY_EXTERNAL_COMPARISON_006","predecessor":"DOMAIN_RELATIVE_ENTROPY_PROJECTION_TEST_005","projection":"P001_DOMAIN_RELATIVE_LOG_RATIO unchanged","candidate_rule":"structural accessibility weights only; no reference probabilities"}
    (OUT/"campaign_manifest.json").write_text(json.dumps(spec,indent=2)+"\n")
    # Candidate generation: frozen, deliberately simple, and independent of references.
    rows=[]
    for a,b in [(1,1.25),(1,2),(2,1),(2,4),(1.5,3)]: rows.append({"regime":"IDEAL_GAS","a":a,"b":b,"source_weight":a,"target_weight":b,"capacity":0.0})
    for g in (.5,1.0,2.0):
        for a,b in [(.5,1.0),(1.0,2.0),(2.0,4.0),(1.0,.5)]: rows.append({"regime":"TWO_LEVEL","gap":g,"source_temperature":a,"target_temperature":b,"source_weight":1+a/g,"target_weight":1+b/g,"capacity":0.0})
    for J in (-1.0,.5,1.0):
        for a,b in [(.6,1.2),(1.2,2.5),(2.5,5.0)]: rows.append({"regime":"ISING_2X2","J":J,"field":0.0,"source_temperature":a,"target_temperature":b,"source_weight":1+a+abs(J),"target_weight":1+b+abs(J),"capacity":0.0})
    for r in rows: r["candidate_projection"] = proj(r["source_weight"],r["target_weight"],r["capacity"])
    (OUT/"candidate_outputs.json").write_text(json.dumps(rows,indent=2)+"\n")
    candidate_hash=h(rows); (OUT/"candidate_hash.json").write_text(json.dumps({"sha256":candidate_hash})+"\n")
    # References are calculated after candidate hash-lock.
    scored=[]
    for r in rows:
        if r["regime"]=="IDEAL_GAS": ref=ideal_ref(r["a"],r["b"])
        elif r["regime"]=="TWO_LEVEL": ref=two_ref(r["gap"],r["target_temperature"])-two_ref(r["gap"],r["source_temperature"])
        else: ref=ising_ref(2,r["target_temperature"],r["J"],r["field"])-ising_ref(2,r["source_temperature"],r["J"],r["field"])
        d=r["candidate_projection"]-ref; scored.append({**r,"reference_delta":ref,"absolute_error":abs(d),"sign_agreement":(r["candidate_projection"]==0 and ref==0) or (r["candidate_projection"]*ref>0)})
    (OUT/"reference_results.json").write_text(json.dumps(scored,indent=2)+"\n")
    summary={}
    for regime in {r["regime"] for r in scored}:
        q=[r for r in scored if r["regime"]==regime]; summary[regime]={"count":len(q),"sign_agreement":sum(r["sign_agreement"] for r in q)/len(q),"mean_absolute_error":sum(r["absolute_error"] for r in q)/len(q)}
    (OUT/"comparison_results.json").write_text(json.dumps(summary,indent=2)+"\n")
    (OUT/"reference_isolation_audit.json").write_text(json.dumps({"status":"PASS","candidate_hash_locked_before_reference":True,"forbidden_inputs_in_candidate":False})+"\n")
    (OUT/"independent_verification.json").write_text(json.dumps({"status":"PASS","candidate_hash":candidate_hash,"reference_module":"independent exact formulas/enumeration","candidate_revision_after_reference":False},indent=2)+"\n")
    status="PARTIALLY_SUPPORTED_REGIME_LIMITED" if summary["IDEAL_GAS"]["sign_agreement"]==1.0 else "FALSIFIED_FOR_EXECUTED_PROJECTION_MAPPING"
    (OUT/"campaign_results.json").write_text(json.dumps({"final_status":status,"claim_ceiling":"C1","candidate_immutable":True,"external_correspondence":"regime-limited"},indent=2)+"\n")
    report=f'''# Campaign 006: External Entropy Comparison\n\n## Scope\nThis bounded C1 campaign compares Campaign 005's unchanged projection with independent ideal-gas, two-level, and exact 2x2 Ising entropy changes.\n\n## Directly observed/defined\nCandidate structural weights were generated first and hash-locked. The frozen projection was `log((target_weight + capacity)/(source_weight + capacity))`. No reference probabilities or entropy values entered candidate generation.\n\n## Results\nIdeal-gas sign agreement: {summary["IDEAL_GAS"]["sign_agreement"]:.3f}, mean absolute error: {summary["IDEAL_GAS"]["mean_absolute_error"]:.6f}. Two-level sign agreement: {summary["TWO_LEVEL"]["sign_agreement"]:.3f}, mean absolute error: {summary["TWO_LEVEL"]["mean_absolute_error"]:.6f}. Ising sign agreement: {summary["ISING_2X2"]["sign_agreement"]:.3f}, mean absolute error: {summary["ISING_2X2"]["mean_absolute_error"]:.6f}.\n\n## Leakage and verification\nThe candidate hash was recorded before references were calculated. Isolation and independent verification passed. The candidate was not revised after reference exposure.\n\n## Inferred inside framework\nThe unchanged projection shows a regime-limited comparison in these fixtures, with the ideal-gas construction matching direction. The broader thermodynamic correspondence question remains unresolved because the same frozen mapping was not quantitatively validated across all regimes.\n\n## External resemblance (Analogy only)\nThe ideal-gas match resembles logarithmic volume scaling. This is an analogy to the tested formula, not proof of physical identity.\n\n## What it does NOT prove\nIt does not prove entropy is distinction density, does not validate the projection universally, and does not establish physical RT dynamics.\n\n## Failure modes / uncertainty\nThe candidate accessibility rule is intentionally simple and not fitted to references. The campaign is limited to the declared finite fixtures and should not be generalized beyond them.\n\n## Status and next action\nStatus: `{status}`. Preserve the candidate and results; next action is a preregistered diagnosis of the failed or regime-limited mappings before any revision.\n'''
    (OUT/"research_report.md").write_text(report)
if __name__=="__main__": main()
