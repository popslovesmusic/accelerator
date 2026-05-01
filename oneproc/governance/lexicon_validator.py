import json
import os
from typing import List, Dict, Any, Optional
from oneproc.utils.trace_capture import TraceCapture

class LexiconValidator:
    def __init__(self, registry_dir: str = "registry", tracer: Optional[TraceCapture] = None):
        self.registry_dir = registry_dir
        self.tracer = tracer
        self.canonical_path = os.path.join(registry_dir, "lexicon_canonical.json")
        self.alias_map_path = os.path.join(registry_dir, "lexicon_alias_map.json")
        self.gap_queue_path = os.path.join(registry_dir, "lexicon_gap_queue.json")
        
        self.lexicon = self._load_json(self.canonical_path)
        self.aliases = self._load_json(self.alias_map_path)

    def _load_json(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def lexicon_in_check(self, terms: List[str]) -> Dict[str, Any]:
        """Check if terms are in the lexicon or gap queue."""
        results = {"valid": [], "missing": [], "aliases": {}}
        for term in terms:
            if term in self.lexicon:
                results["valid"].append(term)
            elif term in self.aliases:
                results["aliases"][term] = self.aliases[term]
                results["valid"].append(self.aliases[term])
            else:
                results["missing"].append(term)
        
        if self.tracer:
            self.tracer.capture("lexicon_validator", "lexicon_in_check", "complete", {
                "input_terms": terms,
                "results": results
            })
        return results

    def lexicon_out_check(self, terms: List[str]) -> Dict[str, Any]:
        """Perform out-check and identify gaps."""
        results = self.lexicon_in_check(terms)
        gaps = results["missing"]
        
        if gaps and self.tracer:
            self.tracer.capture("lexicon_validator", "lexicon_out_check", "gaps_found", {
                "gaps": gaps
            })
            # In a real impl, we might automatically add to gap queue here or flag it.
            
        return results
