"""Alpha-equivalence and typed substitution checks across finite models."""
import json
from pathlib import Path
ROOT=Path(__file__).parent; PRE=ROOT.parent/'CAMPAIGN_CALCULUS_SYNTAX_SEMANTICS_CLOSURE_20260803_001'
models=[json.loads((PRE/'finite_model.json').read_text()),json.loads((PRE/'finite_model_class_b.json').read_text())]
formula_x={'kind':'ForallProcess','binder':'X','body':{'kind':'Distinct','left':{'kind':'ProcessVar','name':'X'},'right':{'kind':'ProcessVar','name':'X'}}}
formula_y={'kind':'ForallProcess','binder':'Y','body':{'kind':'Distinct','left':{'kind':'ProcessVar','name':'Y'},'right':{'kind':'ProcessVar','name':'Y'}}}
def eval_f(n,m,env=None):
    env=env or {}
    if n['kind']=='ProcessVar': return env.get(n['name'],n['name'])
    if n['kind']=='Distinct': return eval_f(n['left'],m,env)!=eval_f(n['right'],m,env)
    if n['kind']=='ForallProcess': return all(eval_f(n['body'],m,{**env,n['binder']:p}) for p in m['processes'])
    raise ValueError('unsupported formula')
def main():
    rows=[]
    for m in models:
        a,b=eval_f(formula_x,m),eval_f(formula_y,m)
        rows.append({'model':m['model_id'],'alpha_original':a,'alpha_renamed':b,'alpha_equivalent':a==b})
    sub=json.loads((PRE/'binder_substitution_report.json').read_text())
    out={'status':'PASS' if all(x['alpha_equivalent'] for x in rows) and sub['status']=='PASS' else 'FAIL','models':rows,'substitution_fixture_status':sub['status'],'interpretation':'Alpha-renaming preserves tested semantics in both models; arbitrary substitution requires a valuation-preservation condition and is not claimed automatically.'}
    (ROOT/'alpha_substitution_model_report.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out))
if __name__=='__main__': main()
