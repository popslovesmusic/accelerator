import typer
app = typer.Typer()
@app.callback(invoke_without_command=True)
def main():
    """Show/audit/promote/downgrade claims."""
    typer.echo("Claim command not yet implemented.")
