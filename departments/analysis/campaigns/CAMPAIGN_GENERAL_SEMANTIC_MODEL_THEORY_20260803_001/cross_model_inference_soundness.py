"""Cross-model soundness test for the minimal inference rules."""
import json
from pathlib import Path
ROOT=Path(__file__).parent; PRE=ROOT.parent/'CAMPAIGN_CALCULUS_SYNTAX_SEMANTICS_CLOSURE_20260803_001'
models=[json.loads((PRE/'finite_model.json').read_text()),json.loads((PRE/'finite_model_class_b.json').read_text())]
d={'kind':'Distinct','left':{'kind':'ProcessVar','name':'E'},'right':{'kind':'ProcessVar','name':'E2'}}; conjunction={'kind':'And','left':d,'right':d}
def val(n,m):
    domain={'ProcessVar':'processes','ResidueVar':'residues','ContextConst':'contexts'}[n['kind']]
    if n['name'] not in m[domain]: raise ValueError('unknown')
    return n['name']
def p(n,m):
    if n['kind']=='Distinct': return val(n['left'],m)!=val(n['right'],m)
    if n['kind']=='And': return p(n['left'],m) and p(n['right'],m)
    if n['kind']=='Admissible': return [val(n['process'],m),val(n['context'],m)] in m['admissible']
    if n['kind']=='Closure': return [val(n['process'],m),val(n['residue'],m),val(n['context'],m)] in m['closures']
    raise ValueError('unsupported')
def main():
    rows=[]
    for m in models:
        intro=p(d,m) and p(d,m) <= p(conjunction,m); left=p(conjunction,m) <= p(d,m); right=p(conjunction,m) <= p(d,m)
        badprem=p({'kind':'Admissible','process':{'kind':'ProcessVar','name':'E3'},'context':{'kind':'ContextConst','name':'y'}},m); badcon=p({'kind':'Closure','process':{'kind':'ProcessVar','name':'E3'},'residue':{'kind':'ResidueVar','name':'R'},'context':{'kind':'ContextConst','name':'y'}},m)
        rows.append({'model':m['model_id'],'AND_INTRO':intro,'AND_ELIM_LEFT':left,'AND_ELIM_RIGHT':right,'negative_rule_premise':badprem,'negative_rule_conclusion':badcon,'negative_rule_falsified':badprem and not badcon})
    out={'status':'PASS' if all(r['AND_INTRO'] and r['AND_ELIM_LEFT'] and r['AND_ELIM_RIGHT'] and r['negative_rule_falsified'] for r in rows) else 'FAIL','models':rows,'scope':'two declared finite models only','general_soundness_claim':False}
    (ROOT/'cross_model_inference_report.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out))
if __name__=='__main__': main()
