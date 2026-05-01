import typer
import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from oneproc.utils.trace_capture import TraceCapture

app = typer.Typer(help="oneproc Lexicon Housekeeping and Resolution")

class LexiconOrchestrator:
    def __init__(self, registry_dir: str = "registry", tracer: Optional[TraceCapture] = None):
        self.registry_dir = registry_dir
        self.tracer = tracer
        self.canonical_path = os.path.join(registry_dir, "lexicon_canonical.json")
        self.alias_map_path = os.path.join(registry_dir, "lexicon_alias_map.json")
        self.gap_queue_path = os.path.join(registry_dir, "lexicon_gap_queue.json")
        self.registry_path = os.path.join(registry_dir, "lexicon_validation_registry.json")
        self.sidecar_path = os.path.join(registry_dir, "lexicon_rules_sidecar.json")
        self.history_path = os.path.join(registry_dir, "lexicon_run_history.jsonl")
        self.snapshot_path = os.path.join(registry_dir, "lexicon_latest_snapshot.json")

    def _load_json(self, path: str) -> Any:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def resolve(self, terms: List[str], strict: bool = False) -> Dict[str, Any]:
        lexicon_file = self._load_json(self.canonical_path)
        lexicon_list = lexicon_file.get("terms", [])
        # Extract actual term strings from the list of dicts
        lexicon_keys = [t.get("term") for t in lexicon_list if t.get("term")]
        
        aliases = self._load_json(self.alias_map_path)
        gap_queue = self._load_json(self.gap_queue_path)
        sidecar = self._load_json(self.sidecar_path)
        registry = self._load_json(self.registry_path)

        resolved = []
        new_gaps = []
        
        ceilings = sidecar.get("claim_ceiling_rules", {
            "GAP_OPEN": "proposed_interpretation",
            "L0": "provisional",
            "L1": "partially_supported",
            "L2": "partially_supported_with_limits",
            "L3": "supported"
        })

        for term in terms:
            entry = {
                "raw_term": term,
                "resolution_type": "gap_open",
                "canonical_term": None,
                "validation_status": "GAP_OPEN",
                "claim_ceiling": ceilings["GAP_OPEN"]
            }

            t_match = term.lower()
            
            canonical_match = next((k for k in lexicon_keys if k.lower() == t_match), None)
            alias_match = next((k for k in aliases if k.lower() == t_match), None)

            if canonical_match:
                entry["resolution_type"] = "canonical"
                entry["canonical_term"] = canonical_match
                status = registry.get(canonical_match, {}).get("status", "L0")
                entry["validation_status"] = status
                entry["claim_ceiling"] = ceilings.get(status, "provisional")
            elif alias_match:
                target = aliases[alias_match]
                entry["resolution_type"] = "alias"
                entry["canonical_term"] = target
                status = registry.get(target, {}).get("status", "L0")
                entry["validation_status"] = status
                entry["claim_ceiling"] = ceilings.get(status, "provisional")
            elif term in gap_queue:
                entry["resolution_type"] = "gap_open"
                entry["canonical_term"] = term
                entry["validation_status"] = "GAP_OPEN"
                entry["claim_ceiling"] = ceilings["GAP_OPEN"]
            else:
                if strict:
                    entry["resolution_type"] = "ambiguous_gap"
                new_gaps.append(term)
            
            resolved.append(entry)

        report = {
            "run_id": str(uuid.uuid4())[:8],
            "timestamp": datetime.utcnow().isoformat(),
            "input_terms": terms,
            "resolved_terms": resolved,
            "new_gaps": new_gaps
        }
        
        if self.tracer:
            self.tracer.capture("lexicon_orchestrator", "resolve", "complete", report)
        
        return report

@app.command()
def resolve(
    terms: Optional[List[str]] = typer.Argument(None, help="Terms to resolve"),
    input_file: Optional[str] = typer.Option(None, "--input", help="File containing terms"),
    out: Optional[str] = typer.Option(None, "--out", help="Output report path"),
    strict: bool = typer.Option(False, "--strict", help="Strict resolution mode")
):
    """Resolve raw terms into canonical terms, aliases, or gaps."""
    if input_file:
        with open(input_file, "r", encoding="utf-8") as f:
            terms = f.read().split()
    
    if not terms:
        typer.echo("No terms provided.")
        return

    orch = LexiconOrchestrator()
    report = orch.resolve(terms, strict=strict)
    
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        typer.echo(f"Resolution report written to {out}")
    else:
        typer.echo(json.dumps(report, indent=2))

@app.command()
def gaps(
    out: Optional[str] = typer.Option(None, "--out", help="Output path"),
    blocking_only: bool = typer.Option(False, "--blocking-only", help="Only show terms blocking claim promotion")
):
    """List unresolved terms and gaps."""
    orch = LexiconOrchestrator()
    gap_queue = orch._load_json(orch.gap_queue_path)
    
    typer.echo("Lexicon Gaps (GAP_OPEN):")
    if isinstance(gap_queue, dict):
        for term, data in gap_queue.items():
            typer.echo(f" - {term}: {data.get('proposed_definition', 'No definition')}")
    else:
        typer.echo("Gap queue is in an unexpected format.")

@app.command()
def audit(strict: bool = typer.Option(False, "--strict")):
    """Detect duplicate terms, orphan aliases, and registry drift."""
    orch = LexiconOrchestrator()
    lexicon_file = orch._load_json(orch.canonical_path)
    lexicon_list = lexicon_file.get("terms", [])
    lexicon_keys = [t.get("term") for t in lexicon_list if t.get("term")]
    aliases = orch._load_json(orch.alias_map_path)
    
    warnings = []
    for alias, target in aliases.items():
        if target not in lexicon_keys:
            warnings.append(f"Orphan Alias: '{alias}' -> '{target}' (target not in canonical lexicon)")
            
    if warnings:
        typer.echo("Audit Warnings:")
        for w in warnings:
            typer.echo(f" [!] {w}")
    else:
        typer.echo("Lexicon audit passed. No orphans or duplicates detected.")

@app.command()
def snapshot(run_id: str = typer.Option(..., "--run-id"), out: Optional[str] = typer.Option(None, "--out")):
    """Write lexicon snapshot and append to history."""
    orch = LexiconOrchestrator()
    lexicon_file = orch._load_json(orch.canonical_path)
    gap_queue = orch._load_json(orch.gap_queue_path)
    
    snapshot_data = {
        "run_id": run_id,
        "timestamp": datetime.utcnow().isoformat(),
        "snapshot": {
            "lexicon": lexicon_file,
            "gap_queue": gap_queue
        }
    }
    
    with open(orch.snapshot_path, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, indent=2)
    
    with open(orch.history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"run_id": run_id, "timestamp": snapshot_data["timestamp"], "action": "snapshot"}) + "\n")
        
    typer.echo(f"Snapshot written to {orch.snapshot_path} and logged to history.")

if __name__ == "__main__":
    app()
