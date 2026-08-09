"""Capture-avoiding binder substitution tests for the noncanonical extension."""
import json
from pathlib import Path
ROOT=Path(__file__).parent; fx=json.loads((ROOT/'binder_substitution_fixtures.json').read_text(encoding='utf-8'))
def names(n):
    if not isinstance(n,dict): return set()
    out=set()
    if n.get('kind')=='ProcessVar': out.add(n['name'])
    if n.get('kind')=='ForallProcess': out.add(n['binder'])
    for v in n.values():
        if isinstance(v,dict): out |= names(v)
    return out
def rename_bound(n,old,new):
    if n.get('kind')=='ProcessVar' and n.get('name')==old: return {'kind':'ProcessVar','name':new}
    return {k:(rename_bound(v,old,new) if isinstance(v,dict) else v) for k,v in n.items()}
def subst(n,var,repl):
    if n.get('kind')=='ProcessVar': return dict(repl) if n.get('name')==var else dict(n)
    if n.get('kind')=='ForallProcess':
        b=n['binder']
        if b==var: return dict(n)
        body=n['body']
        if repl.get('kind')=='ProcessVar' and repl['name']==b and var in names(body):
            used=names(n)|names(repl); i=0; fresh=f'{b}_{i}'
            while fresh in used: i+=1; fresh=f'{b}_{i}'
            body=rename_bound(body,b,fresh); b=fresh
        return {'kind':'ForallProcess','binder':b,'body':subst(body,var,repl)}
    return {k:(subst(v,var,repl) if isinstance(v,dict) else v) for k,v in n.items()}
def main():
    results=[]
    for c in fx['cases']:
        got=subst(c['expr'],c['variable'],c['replacement']); results.append({'name':c['name'],'pass':got==c['expected'],'result':got})
    out={'status':'PASS' if all(x['pass'] for x in results) else 'FAIL','cases':results,'capture_avoiding':True,'scope':'binder extension only'}
    (ROOT/'binder_substitution_report.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8'); print(json.dumps(out))
if __name__=='__main__': main()
