import typer
app = typer.Typer()
@app.callback(invoke_without_command=True)
def main():
    """Zenodo publication package validation/export."""
    typer.echo("Publish command not yet implemented.")
