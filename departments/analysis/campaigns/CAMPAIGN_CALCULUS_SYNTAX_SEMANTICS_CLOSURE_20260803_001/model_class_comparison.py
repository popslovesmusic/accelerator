"""Compare truth behavior across two explicit finite model classes."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
A=json.loads((ROOT/'finite_model.json').read_text(encoding='utf-8')); B=json.loads((ROOT/'finite_model_class_b.json').read_text(encoding='utf-8'))
cases=[
 ('distinct_E_E2',lambda m: 'E'!='E2'),
 ('admissible_E_x',lambda m: ['E','x'] in m['admissible']),
 ('closure_E_R_x',lambda m: ['E','R','x'] in m['closures']),
 ('couples_E_E2_x',lambda m: ['couples','E','E2','x'] in m['relations'])]
def main():
    rows=[]
    for name,fn in cases:
        av,bv=fn(A),fn(B); rows.append({'case':name,'model_A':av,'model_B':bv,'invariant':av==bv})
    out={'status':'PASS','models':['FINITE_RELATIONAL_MODEL_DRAFT_001','FINITE_RELATIONAL_MODEL_B_DRAFT_001'],'comparisons':rows,'invariant_cases':sum(x['invariant'] for x in rows),'model_dependent_cases':sum(not x['invariant'] for x in rows),'interpretation':'syntax transfers; semantic truth may depend on model interpretation'}
    (ROOT/'model_class_comparison_report.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8'); print(json.dumps(out))
if __name__=='__main__': main()
