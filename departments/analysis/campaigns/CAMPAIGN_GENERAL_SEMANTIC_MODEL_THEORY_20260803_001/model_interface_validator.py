"""Validate the general model interface and produce rule countermodels."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
PRE=ROOT.parent/'CAMPAIGN_CALCULUS_SYNTAX_SEMANTICS_CLOSURE_20260803_001'
schema=json.loads((ROOT/'model_interface_schema.json').read_text(encoding='utf-8'))
models=[json.loads((PRE/'finite_model.json').read_text(encoding='utf-8')),json.loads((PRE/'finite_model_class_b.json').read_text(encoding='utf-8'))]
def validate(m):
    required=['processes','residues','contexts','admissible','closures','relations']
    present=all(k in m for k in required)
    typed=present and all(isinstance(m[k],list) for k in required)
    return present and typed
def countermodel(m):
    for process,context in m['admissible']:
        residue=m['residues'][0]
        if [process,residue,context] not in m['closures']:
            return {'model_id':m['model_id'],'premise':{'Admissible':[process,context],'truth':True},'conclusion':{'Closure':[process,residue,context],'truth':False},'rule':'Admissible -> Closure','counterexample':True}
    return {'model_id':m['model_id'],'counterexample':False}
def main():
    checks=[{'model_id':m['model_id'],'interface_valid':validate(m),'countermodel':countermodel(m)} for m in models]
    out={'status':'PASS' if all(x['interface_valid'] and x['countermodel']['counterexample'] for x in checks) else 'FAIL','schema_id':schema['schema_id'],'models':checks,'semantic_result_channel':schema['semantic_result'],'interpretation':'The rejected rule fails in both declared finite models; this is countermodel coverage, not a general completeness proof.'}
    (ROOT/'model_interface_validation_report.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out))
if __name__=='__main__': main()
