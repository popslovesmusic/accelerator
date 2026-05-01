import typer
import os
from typing import Optional
from oneproc.governance.claim_gate import ClaimGate
from oneproc.utils.trace_capture import TraceCapture
import uuid
import json

app = typer.Typer()

def _validate(paper_path: str, level: str, intent: str, strict: bool):
    if not os.path.exists(paper_path):
        typer.echo(f"Error: Paper not found at {paper_path}")
        raise typer.Exit(code=1)

    run_id = str(uuid.uuid4())[:8]
    tracer = TraceCapture(run_id, f"outputs/runs/{run_id}")
    
    with open(paper_path, "r", encoding="utf-8") as f:
        content = f.read().replace("\r\n", "\n")

    # Simple metadata extraction for testing
    metadata = {}
    if "independent_measurement_count=1" in content:
        metadata["independent_measurement_count"] = 1
    
    claim_data = {
        "claim_id": f"CLAIM-{run_id}",
        "requested_level": level,
        "paper_content": content,
        "metadata": metadata,
        "lexicon_terms": [],
        "measurements": [],
        "falsification_data": [],
        "tools": []
    }

    gate = ClaimGate(tracer=tracer)
    return gate.process_claim(claim_data, strict=strict, intent=intent), tracer

@app.command()
def check(
    paper_path: str = typer.Argument(..., help="Path to the technical paper (Markdown)"),
    level: str = typer.Option("C4", "--level", help="Target claim level"),
    intent: str = typer.Option("validate", "--intent", help="Intent: explore, validate, publish"),
    strict: bool = typer.Option(False, "--strict", help="Enforce strict mode")
):
    """Return pass/fail and validation summary."""
    result, tracer = _validate(paper_path, level, intent, strict)
    typer.echo(f"Validation Result: {result['gate_result'].upper()}")
    typer.echo(f"Final Level: {result['final_level']}")
    typer.echo(f"Trace captured in: {tracer.file_path}")
    if result["gate_result"] == "block":
        raise typer.Exit(code=1)

@app.command()
def explain(
    paper_path: str = typer.Argument(..., help="Path to the technical paper (Markdown)"),
    level: str = typer.Option("C4", "--level", help="Target claim level"),
    intent: str = typer.Option("validate", "--intent", help="Intent: explore, validate, publish"),
    strict: bool = typer.Option(False, "--strict", help="Enforce strict mode")
):
    """Return human-readable failure explanation and exact fixes."""
    result, tracer = _validate(paper_path, level, intent, strict)
    typer.echo(f"=== Validation Report for {paper_path} ===")
    typer.echo(f"Result: {result['gate_result'].upper()}")
    typer.echo(f"Final Level: {result['final_level']}")
    
    if result["blocked_reasons"]:
        typer.echo("\nBLOCKING ERRORS:")
        for r in result["blocked_reasons"]:
            typer.echo(f" - {r}")
            
    if result["downgrades_applied"]:
        typer.echo("\nDOWNGRADES APPLIED:")
        for d in result["downgrades_applied"]:
            typer.echo(f" - {d}")
    
    typer.echo(f"\nTrace: {tracer.file_path}")

@app.command()
def json_report(
    paper_path: str = typer.Argument(..., help="Path to the technical paper (Markdown)"),
    level: str = typer.Option("C4", "--level", help="Target claim level"),
    intent: str = typer.Option("validate", "--intent", help="Intent: explore, validate, publish"),
    strict: bool = typer.Option(False, "--strict", help="Enforce strict mode")
):
    """Emit machine-readable validation report only."""
    result, _ = _validate(paper_path, level, intent, strict)
    typer.echo(json.dumps(result, indent=2))
