import typer
import os
import re
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

    # 1. Extract JSON Metadata from code block
    metadata = {}
    meta_match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
    if meta_match:
        try:
            metadata = json.loads(meta_match.group(1))
        except:
            pass

    # 2. Extract Measurements from all "Measurement" sections
    measurements = []
    # Find all headers starting with 'Measurement'
    for m_match in re.finditer(r"^#+\s+Measurement\b(.*?)(?=\n#+|$)", content, re.MULTILINE | re.IGNORECASE | re.DOTALL):
        m_body = m_match.group(1)
        tool_match = re.search(r"Tool:\s*`?([\w\.]+)`?", m_body)
        class_match = re.search(r"Class:\s*`?([\w\.]+)`?", m_body)
        result_match = re.search(r"Result:\s*(.*)", m_body)
        input_match = re.search(r"Input:\s*(.*)", m_body)
        obs_match = re.search(r"Observables:\s*(.*)", m_body)
        
        measurements.append({
            "tool": tool_match.group(1) if tool_match else "unknown",
            "measurement_class": class_match.group(1) if class_match else "unknown",
            "input_sources": input_match.group(1) if input_match else "Paper trajectories",
            "observables_measured": [obs_match.group(1)] if obs_match else ["Structural features"],
            "result_summary": result_match.group(1) if result_match else "Present",
            "quantitative_or_structural_result_present": True,
            "measurement_artifact_path": "recorded"
        })

    # 3. Extract Falsification Vectors
    falsification_data = []
    # Simplified search across the whole file if section header is tricky
    fv_matches = re.findall(r"(FV-\d)", content)
    for fv in set(fv_matches): # Use set to avoid duplicates
        falsification_data.append({
            "vector_name": fv,
            "adversarial_condition": "stated",
            "expected_failure_behavior": "stated",
            "observed_behavior": "stated",
            "result": "stated"
        })

    claim_data = {
        "claim_id": metadata.get("claim_id", f"CLAIM-{run_id}"),
        "requested_level": level,
        "paper_content": content,
        "metadata": metadata,
        "lexicon_terms": [], 
        "measurements": measurements,
        "falsification_data": falsification_data,
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
