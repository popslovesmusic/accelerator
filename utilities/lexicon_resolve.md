# `lexicon_resolve.py`

Heuristic helper to turn a free-text excerpt into a canonical mapping:

```json
{ "epsilon": "...", "residue": "...", "coupling": "..." }
```

It normalizes tokens using `theory/lexicon/lexicon_alias_map.json` and then scores each primitive using keyword hits.

## Examples

Resolve a short excerpt:

```powershell
python utilities/lexicon_resolve.py --text "A continuation is admissible if C(y|x_t,R_t,K_t)=1 and epsilon(y) != 0"
```

Resolve an entire law file:

```powershell
python utilities/lexicon_resolve.py --file "theory/THE LAW OF THE ONE PROCESS.txt" --out "outputs/lexicon_mapping_law.json"
```

## Output fields

- `top_terms`: most common normalized terms detected
- `primitive_scores`: keyword-hit counts for `epsilon`, `residue`, `coupling`
- `mapping`: draft `{epsilon,residue,coupling}` strings suitable for paper section “Theoretical Mapping”

