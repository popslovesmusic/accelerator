"""Bounded substitution and partial-composition semantics tests."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
fx=json.loads((ROOT/'substitution_composition_fixtures.json').read_text(encoding='utf-8'))
def substitute(node,var,repl):
    if not isinstance(node,dict): return node
    out=dict(node)
    if node.get('kind')=='ProcessVar' and node.get('name')==var: return dict(repl)
    for k,v in node.items():
        if isinstance(v,dict): out[k]=substitute(v,var,repl)
    return out
def compose(left,right):
    if left['context']!=right['context']: return {'status':'FAIL_CONTEXT_MISMATCH'}
    if left['right']!=right['left']: return {'status':'FAIL_ENDPOINT_MISMATCH'}
    return {'status':'COMPOSED','left':left['left'],'middle':left['right'],'right':right['right'],'context':left['context']}
def main():
    sub=[]
    for c in fx['substitution']:
        result=substitute(c['expr'],c['variable'],c['replacement'])
        sub.append({'name':c['name'],'status':'PASS' if result['left']['name']==c['expected_left'] else 'FAIL','result':result})
    comp=[]
    for c in fx['composition']:
        result=compose(c['left'],c['right'])
        comp.append({'name':c['name'],'status':'PASS' if result['status']==c['expected'] else 'FAIL','result':result})
    out={'substitution':sub,'composition':comp,'status':'PASS' if all(x['status']=='PASS' for x in sub+comp) else 'FAIL','failure_is_explicit':all(x['result']['status'].startswith('FAIL_') for x in comp if x['name']!='compatible_context_chain')}
    (ROOT/'substitution_composition_report.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8'); print(json.dumps(out))
if __name__=='__main__': main()
