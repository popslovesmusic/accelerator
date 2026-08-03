"""Finite-model truth-condition evaluator for the noncanonical closure draft."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
model=json.loads((ROOT/'finite_model.json').read_text(encoding='utf-8'))
cases=json.loads((ROOT/'truth_condition_fixtures.json').read_text(encoding='utf-8'))
def value(node):
    k=node['kind']; name=node.get('name')
    if k=='ProcessVar':
        if name not in model['processes']: raise ValueError('unknown process')
        return ('Process',name)
    if k=='ResidueVar':
        if name not in model['residues']: raise ValueError('unknown residue')
        return ('Residue',name)
    if k=='ContextConst':
        if name not in model['contexts']: raise ValueError('unknown context')
        return ('Context',name)
    raise ValueError('not a value node')
def prop(node):
    k=node['kind']
    if k=='Distinct': return value(node['left'])[1] != value(node['right'])[1]
    if k=='Admissible': return [value(node['process'])[1],value(node['context'])[1]] in model['admissible']
    if k=='Closure': return [value(node['process'])[1],value(node['residue'])[1],value(node['context'])[1]] in model['closures']
    if k=='Relation': return [node['name'],value(node['left'])[1],value(node['right'])[1],value(node['context'])[1]] in model['relations']
    if k=='And': return prop(node['left']) and prop(node['right'])
    if k=='Not': return not prop(node['value'])
    raise ValueError('unknown proposition')
def run(group, expected):
    results=[]
    for c in cases[group]:
        try: observed=prop(c['expr']); results.append({'name':c['name'],'status':'PASS' if observed==expected else 'FAIL','observed':observed})
        except ValueError as e: results.append({'name':c['name'],'status':'FAIL' if expected else 'PASS','error':str(e)})
    return results
def main():
    out={'true_cases':run('true_cases',True),'false_cases':run('false_cases',False),'invalid_cases':run('invalid_cases',False)}
    passed=all(x['status']=='PASS' for group in out.values() for x in group)
    out['status']='PASS' if passed else 'FAIL'; out['repeatable']=out==json.loads(json.dumps(out))
    (ROOT/'finite_model_truth_report.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out))
if __name__=='__main__': main()
