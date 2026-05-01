import typer
from oneproc.lexicon_cli import LexiconOrchestrator
import json

app = typer.Typer()

@app.command()
def test_resolution():
    """Verify deterministic resolution repeatability."""
    orch = LexiconOrchestrator()
    terms = ["epsilon", "residue", "unknown_process"]
    
    report1 = orch.resolve(terms)
    report2 = orch.resolve(terms)
    
    # Remove timestamps and run_ids for stability check
    for r in [report1, report2]:
        r.pop("timestamp")
        r.pop("run_id")
        
    assert report1 == report2
    typer.echo("Success: Deterministic resolution repeatable.")

@app.command()
def test_gap_creation():
    """Verify unknown term creates GAP_OPEN entry."""
    orch = LexiconOrchestrator()
    terms = ["totally_new_term"]
    report = orch.resolve(terms)
    
    found = False
    for res in report["resolved_terms"]:
        if res["raw_term"] == "totally_new_term":
            assert res["validation_status"] == "GAP_OPEN"
            assert res["claim_ceiling"] == "proposed_interpretation"
            found = True
    assert found
    typer.echo("Success: Unknown term correctly routed to GAP_OPEN.")

if __name__ == "__main__":
    app()
