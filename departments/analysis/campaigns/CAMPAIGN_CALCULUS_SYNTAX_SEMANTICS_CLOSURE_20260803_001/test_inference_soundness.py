"""Finite-model soundness checks for minimal noncanonical rules."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
model=json.loads((ROOT/'finite_model.json').read_text(encoding='utf-8'))
fx=json.loads((ROOT/'inference_fixtures.json').read_text(encoding='utf-8'))
def val(n):
    kinds={'ProcessVar':'processes','ResidueVar':'residues','ContextConst':'contexts'}
    if n['name'] not in model[kinds[n['kind']]]: raise ValueError('unknown value')
    return n['name']
def prop(n):
    k=n['kind']
    if k=='Distinct': return val(n['left']) != val(n['right'])
    if k=='Admissible': return [val(n['process']),val(n['context'])] in model['admissible']
    if k=='Closure': return [val(n['process']),val(n['residue']),val(n['context'])] in model['closures']
    if k=='Relation': return [n['name'],val(n['left']),val(n['right']),val(n['context'])] in model['relations']
    if k=='And': return prop(n['left']) and prop(n['right'])
    if k=='Not': return not prop(n['value'])
    raise ValueError('unknown proposition')
def check(c):
    premises=[prop(x) for x in c['premises']]; conclusion=prop(c['conclusion'])
    return {'rule':c['rule'],'premises_true':premises,'conclusion_true':conclusion,'sound_instance':not all(premises) or conclusion}
def main():
    valid=[check(c) for c in fx['valid']]
    bad=check(fx['unsound_candidate'])
    out={'valid_rules':valid,'unsound_candidate':bad,'status':'PASS' if all(x['sound_instance'] for x in valid) and not bad['sound_instance'] else 'FAIL','bounded_only':True}
    (ROOT/'inference_soundness_report.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out))
if __name__=='__main__': main()
