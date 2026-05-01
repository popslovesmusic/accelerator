import typer
from typing import Optional
from oneproc.workers.base_worker import CodexWorker, GeminiWorker
from oneproc.utils.trace_capture import TraceCapture
import uuid

app = typer.Typer()

@app.command()
def ask(
    agent: str = typer.Option(..., "--agent", help="Agent to call (codex or gemini)"),
    task: str = typer.Option(..., "--task", help="Task description")
):
    """Call Codex/Gemini workers."""
    run_id = str(uuid.uuid4())[:8]
    tracer = TraceCapture(run_id, f"outputs/runs/{run_id}")
    
    if agent.lower() == "codex":
        worker = CodexWorker(tracer=tracer)
    elif agent.lower() == "gemini":
        worker = GeminiWorker(tracer=tracer)
    else:
        typer.echo(f"Unknown agent: {agent}")
        raise typer.Exit(code=1)

    typer.echo(f"Sending task to {agent}...")
    result = worker.ask(task)
    
    typer.echo(f"Worker returned with code: {result.return_code}")
    if result.stdout:
        typer.echo("STDOUT:")
        typer.echo(result.stdout)
    if result.stderr:
        typer.echo("STDERR:")
        typer.echo(result.stderr)
        
    typer.echo(f"Trace captured in: {tracer.file_path}")
