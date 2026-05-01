import typer
import os
import json
from typing import Optional

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(repair: bool = typer.Option(False, "--repair", help="Attempt to repair invalid registry files")):
    """Initialize missing registry files, schemas, and output directories."""
    required_dirs = ["outputs/runs", "patches", "registry"]
    for d in required_dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            typer.echo(f"Created directory: {d}")
        else:
            typer.echo(f"Directory exists: {d}")

    # Verify key registry files
    registry_files = [
        "claim_registry.json",
        "evidence_registry.json",
        "language_policy_registry.json",
        "lexicon_canonical.json",
        "tool_manifest.json"
    ]
    
    for f in registry_files:
        path = os.path.join("registry", f)
        if not os.path.exists(path):
            if repair:
                with open(path, "w") as rf:
                    json.dump({}, rf)
                typer.echo(f"Created empty registry file: {path}")
            else:
                typer.echo(f"Warning: Missing registry file: {path}. Use --repair to create empty defaults.")
        else:
            typer.echo(f"Found registry file: {path}")

    typer.echo("Initialization complete.")
