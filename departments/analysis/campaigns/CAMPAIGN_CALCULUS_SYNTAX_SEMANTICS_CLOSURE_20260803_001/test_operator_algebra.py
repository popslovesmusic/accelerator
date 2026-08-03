"""Bounded composition-property checks over finite typed relation paths."""
import json
from pathlib import Path
ROOT=Path(__file__).parent; f=json.loads((ROOT/'operator_algebra_fixtures.json').read_text(encoding='utf-8'))
def comp(a,b):
    if a['context']!=b['context']: return {'status':'FAIL_CONTEXT'}
    if a['right']!=b['left']: return {'status':'FAIL_ENDPOINT'}
    return {'status':'OK','left':a['left'],'right':b['right'],'context':a['context']}
def as_edge(x): return {'left':x['left'],'right':x['right'],'context':x['context']}
def main():
    r1,r2,r3,e,f2=f['r1'],f['r2'],f['r3'],f['identity_E'],f['identity_E2']
    left=comp(comp(r1,r2)|{'left':r1['left'],'right':r2['right'],'context':'x'},r3)
    right=comp(r1,{'left':r2['left'],'right':r3['right'],'context':'x'})
    identity_left=comp(e,r1); identity_right=comp(r1,f2)
    noncomm=comp(r1,r2)['status']=='OK' and comp(r2,r1)['status']!='OK'
    out={'closure':comp(r1,r2),'associativity_fixture':{'left':left,'right':right,'equal':left==right},'identity_fixture':{'left':identity_left,'right':identity_right},'noncommutativity_fixture':noncomm,'context_failure':comp(r1,{'left':'E2','right':'E3','context':'y'}),'status':'PASS' if comp(r1,r2)['status']=='OK' and left==right and identity_left['status']=='OK' and identity_right['status']=='OK' and noncomm else 'FAIL','scope':'finite compatible relation paths only'}
    (ROOT/'operator_algebra_report.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8'); print(json.dumps(out))
if __name__=='__main__': main()
