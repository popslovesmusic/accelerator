"""Deterministic fixture validator for the noncanonical typed syntax draft."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
schema=json.loads((ROOT/'frozen_typed_abstract_syntax.json').read_text(encoding='utf-8'))
fixtures=json.loads((ROOT/'typed_syntax_fixtures.json').read_text(encoding='utf-8'))
def infer(node):
    if not isinstance(node,dict) or 'kind' not in node: raise TypeError('node must have kind')
    spec=schema['nodes'].get(node['kind'])
    if spec is None: raise TypeError('unknown node kind')
    for field, expected in spec['fields'].items():
        if field not in node: raise TypeError('missing field '+field)
        value=node[field]
        if expected=='string':
            if not isinstance(value,str) or not value: raise TypeError('invalid string field')
        else:
            actual=infer(value)
            if actual != expected: raise TypeError(f'{field}: expected {expected}, got {actual}')
    extra=set(node)-{'kind'}-set(spec['fields'])
    if extra: raise TypeError('unexpected fields')
    return spec['type']
def check(nodes, expected):
    results=[]
    for node in nodes:
        try: infer(node); ok=True
        except TypeError: ok=False
        results.append(ok)
    assert all(results) if expected else not any(results)
    return results
def main():
    valid=check(fixtures['valid'],True); invalid=check(fixtures['invalid'],False)
    report={'status':'PASS','valid_fixture_results':valid,'invalid_fixture_results':invalid,'deterministic':check(fixtures['valid'],True)==valid,'schema_id':schema['schema_id']}
    (ROOT/'typed_syntax_validation_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
if __name__=='__main__': main()
