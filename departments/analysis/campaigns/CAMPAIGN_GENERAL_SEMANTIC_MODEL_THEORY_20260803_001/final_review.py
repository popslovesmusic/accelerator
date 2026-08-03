"""Independent final review of the general semantic campaign."""
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).parent
required=['campaign_specification.json','model_interface_schema.json','validation_plan.json','model_interface_validation_report.json','semantic_result_channel_report.json','alpha_substitution_model_report.json','cross_model_inference_report.json']
scripts=['model_interface_validator.py','test_semantic_result_channel.py','alpha_substitution_model_test.py','cross_model_inference_soundness.py']
def main():
    presence={x:(ROOT/x).exists() for x in required}; runs=[]
    for s in scripts:
        p=subprocess.run([sys.executable,str(ROOT/s)],capture_output=True,text=True); runs.append({'script':s,'pass':p.returncode==0,'returncode':p.returncode})
    spec=json.loads((ROOT/'campaign_specification.json').read_text()); reports=[json.loads((ROOT/x).read_text()) for x in required[3:]]
    out={'status':'PASS_BOUNDED_FINAL_REVIEW' if all(presence.values()) and all(x['pass'] for x in runs) else 'FAIL_REVIEW','artifact_presence':presence,'validator_reruns':runs,'noncanonical_boundary':spec['authority_boundary']=='analysis campaign package only','promotion_status':'NOT_AUTHORIZED','remaining_gaps':['general model-theoretic semantics','soundness for all declared rules and model classes','completeness theorem or explicit formal non-completeness result','consistency proof','infinite or broader model-class behavior','complete treatment of partial operators and undefinedness'],'evidence_scope':'two finite relational models and declared fixtures only'}
    (ROOT/'final_review_report.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out))
if __name__=='__main__': main()
