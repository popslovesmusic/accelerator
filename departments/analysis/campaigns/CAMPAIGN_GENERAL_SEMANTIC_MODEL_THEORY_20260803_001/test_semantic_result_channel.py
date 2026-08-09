"""Determinism and typed partiality tests for the general semantic draft."""
import json
from pathlib import Path
ROOT=Path(__file__).parent; model=json.loads((ROOT.parent/'CAMPAIGN_CALCULUS_SYNTAX_SEMANTICS_CLOSURE_20260803_001'/'finite_model.json').read_text(encoding='utf-8')); fx=json.loads((ROOT/'semantic_result_fixtures.json').read_text(encoding='utf-8'))
def eval_case(c):
    if c['kind']=='Relation':
        if c.get('left_type')=='Residue' or c.get('left') not in model['processes'] or c.get('right') not in model['processes']: return 'INVALID_ILL_TYPED'
    elif c.get('process') not in model['processes']:
        return 'INVALID_ILL_TYPED'
    if c['kind']=='Admissible': return 'TRUE' if [c['process'],c['context']] in model['admissible'] else 'FALSE'
    if c['kind']=='Closure': return 'TRUE' if [c['process'],c['residue'],c['context']] in model['closures'] else 'FALSE'
    if c['kind']=='Relation':
        if c['relation'] not in ['couples']: return 'UNDEFINED_TYPED'
        return 'TRUE' if ['couples',c['left'],c['right'],c['context']] in model['relations'] else 'FALSE'
    return 'INVALID_ILL_TYPED'
def main():
    rows=[]
    for c in fx['cases']:
        first=eval_case(c); second=eval_case(c); rows.append({'name':c['name'],'expected':c['expected'],'first':first,'second':second,'deterministic':first==second,'pass':first==c['expected'] and first==second})
    out={'status':'PASS' if all(x['pass'] for x in rows) else 'FAIL','cases':rows,'channel':['TRUE','FALSE','UNDEFINED_TYPED','INVALID_ILL_TYPED']}
    (ROOT/'semantic_result_channel_report.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8'); print(json.dumps(out))
if __name__=='__main__': main()
