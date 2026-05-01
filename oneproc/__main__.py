import typer
from oneproc.commands import init, run, worker, validate_paper, claim, publish
from oneproc import lexicon_cli

app = typer.Typer(help="oneproc: Governed Agent Residence CLI Wrapper")

app.add_typer(init.app, name="init")
app.add_typer(run.app, name="run")
app.add_typer(worker.app, name="worker")
app.add_typer(validate_paper.app, name="validate-paper")
app.add_typer(claim.app, name="claim")
app.add_typer(publish.app, name="publish")
app.add_typer(lexicon_cli.app, name="lexicon")

if __name__ == "__main__":
    app()
