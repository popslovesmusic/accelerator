"""Independent read-only review of the noncanonical calculus closure package."""
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).parent
required=['work_package.json','syntax_semantics_closure_draft.md','validation_matrix.json','frozen_typed_abstract_syntax.json','typed_syntax_fixtures.json','typed_syntax_validation_report.json','finite_model.json','truth_condition_fixtures.json','finite_model_truth_report.json','substitution_composition_report.json','inference_soundness_report.json','operator_algebra_report.json']
def load(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8'))
def main():
    presence={n:(ROOT/n).exists() for n in required}
    syntax=load('typed_syntax_validation_report.json'); truth=load('finite_model_truth_report.json'); sub=load('substitution_composition_report.json'); inf=load('inference_soundness_report.json'); alg=load('operator_algebra_report.json'); wp=load('work_package.json')
    reruns=[]
    for script in ['validate_typed_syntax_fixtures.py','evaluate_finite_model.py','test_substitution_composition.py','test_inference_soundness.py','test_operator_algebra.py']:
        p=subprocess.run([sys.executable,str(ROOT/script)],capture_output=True,text=True)
        reruns.append({'script':script,'returncode':p.returncode,'passed':p.returncode==0})
    gaps={
      'syntax_closure': {'state':'bounded_fixture_pass','evidence':'typed_syntax_validation_report.json','remaining':'not a complete grammar'},
      'semantic_closure': {'state':'finite_model_pass','evidence':'finite_model_truth_report.json','remaining':'one finite model only'},
      'truth_conditions': {'state':'finite_fixture_pass','evidence':'finite_model_truth_report.json','remaining':'no general model-theoretic truth theory'},
      'substitution_binding': {'state':'bounded_fixture_pass','evidence':'substitution_composition_report.json','remaining':'no binder-rich calculus tested'},
      'partial_operator_failure': {'state':'explicit_failure_pass','evidence':'substitution_composition_report.json','remaining':'only declared composition cases'},
      'inference_rules': {'state':'minimal_bounded_soundness','evidence':'inference_soundness_report.json','remaining':'no complete inference calculus'},
      'operator_algebra': {'state':'bounded_fixture_pass','evidence':'operator_algebra_report.json','remaining':'no general associativity/confluence proof'},
      'model_class': {'state':'finite_test_model_only','evidence':'finite_model.json','remaining':'no general satisfiability/consistency result'}
    }
    boundaries={'noncanonical':wp['authority']=='analysis_work_package_only','no_promotion':len(wp['does_not_authorize'])>=3,'reruns_pass':all(x['passed'] for x in reruns)}
    status='PASS_BOUNDED_REVIEW' if all(presence.values()) and all(boundaries.values()) and syntax['status']=='PASS' and truth['status']=='PASS' and sub['status']=='PASS' and inf['status']=='PASS' and alg['status']=='PASS' else 'FAIL_REVIEW'
    out={'status':status,'artifact_presence':presence,'validator_reruns':reruns,'scope_boundary_checks':boundaries,'gap_reconciliation':gaps,'promotion_status':'NOT_AUTHORIZED','independent_of_canonical_registry':True}
    (ROOT/'independent_review_reconciliation.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out))
if __name__=='__main__': main()
