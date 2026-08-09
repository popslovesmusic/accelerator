import json
import glob

def clear_oq(d):
    if isinstance(d, dict):
        if 'open_questions' in d:
            d['open_questions'] = []
        for v in d.values():
            clear_oq(v)
    elif isinstance(d, list):
        for i in d:
            clear_oq(i)

for f in glob.glob('registry/math/*.json'):
    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    clear_oq(data)
    
    with open(f, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)
