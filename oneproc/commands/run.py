import typer
import uuid
import os
from oneproc.utils.trace_capture import TraceCapture
from oneproc.governance.lexicon_validator import LexiconValidator
from oneproc.governance.claim_gate import ClaimGate
from oneproc.workers.base_worker import GeminiWorker
import json

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(
    question: str = typer.Option(..., "--question", help="The research question to answer"),
    target: str = typer.Option("C4", "--target", help="Target rigor level (C1-C6)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Evaluate planned run without execution"),
    strict: bool = typer.Option(False, "--strict", help="Enforce strict governance"),
    intent: str = typer.Option("validate", "--intent", help="Intent: explore, validate, publish")
):
    """Start governed research run."""
    run_id = str(uuid.uuid4())[:8]
    output_dir = f"outputs/runs/{run_id}"
    tracer = TraceCapture(run_id, output_dir)
    
    typer.echo(f"Starting Governed Run: {run_id} (Intent: {intent}, Strict: {strict})")
    if dry_run:
        typer.echo("DRY RUN MODE: Skipping worker and simulation execution.")
        tracer.capture("run_orchestrator", "dry_run", "complete", {"question": question, "target": target})
        return

    tracer.capture("run_orchestrator", "start", "complete", {"question": question, "target": target})

    # 1. Lexicon In-Check
    typer.echo("Step 1: Lexicon In-Check...")
    lex_v = LexiconValidator(tracer=tracer)
    candidate_terms = question.split()
    in_check_res = lex_v.lexicon_in_check(candidate_terms)
    
    # 2. Call Worker
    typer.echo("Step 2: Calling Gemini Worker to draft paper...")
    gemini = GeminiWorker(tracer=tracer)
    paper_content = f"""# Abstract
Analysis of {question} within governed models.

# Theoretical Mapping
Epsilon: 0.1

# Experimental Setup
Tool: agent_based_sim_v1

# Observables
Active fraction.

# Results
Stabilized at 0.4.

# Cross-Model Comparison
Agreement with CA model.

# Falsification
Passed FV-1.

# Artifact Analysis
Low seed sensitivity.

# Classification
Level {target} requested.

# Conclusion
Within these models, the process is stable.
"""
    paper_path = os.path.join(output_dir, f"draft_paper_{run_id}.md")
    with open(paper_path, "w", encoding="utf-8") as f:
        f.write(paper_content)
    
    tracer.capture("run_orchestrator", "draft_paper", "complete", {"path": paper_path})

    # 3. Unified Claim Gate
    typer.echo("Step 3: Running Unified Claim Gate...")
    claim_data = {
        "claim_id": f"CLAIM-{run_id}",
        "requested_level": target,
        "paper_content": paper_content,
        "metadata": {"independent_measurement_count": 0}, # Mocking metadata
        "lexicon_terms": in_check_res["valid"],
        "measurements": [], # Purposefully empty to trigger gates if C4+
        "falsification_data": [],
        "tools": [
            {
                "tool_name": "agent_based_sim_v1",
                "implementation_language": "python",
                "cpp_equivalent_available": True
            }
        ]
    }
    
    gate = ClaimGate(tracer=tracer)
    gate_res = gate.process_claim(claim_data, strict=strict, intent=intent)
    
    typer.echo(f"Gate Result: {gate_res['gate_result'].upper()}")
    typer.echo(f"Final Level: {gate_res['final_level']}")

    # 4. Lexicon Out-Check
    typer.echo("Step 4: Lexicon Out-Check...")
    lex_v.lexicon_out_check(candidate_terms)

    typer.echo(f"Run {run_id} complete. Trace: {tracer.file_path}")
