from __future__ import annotations

import click

from diffsay.diff import Diff
from diffsay.spinner import spinner


@click.command()
@click.option(
    "-m",
    "--model",
    default=Diff.DEFAULT_MODEL,
    show_default=True,
    help=(
        "Hugging Face model id or local path. Bare names are resolved under "
        f"{Diff.DEFAULT_MODEL_ORG}/."
    ),
)
def main(model: str) -> None:
    """Generate a conventional commit message from the staged git diff."""
    diff = Diff(model)
    diff_text = diff.staged()
    if not diff_text:
        raise click.ClickException(
            "No staged changes found. Please stage files using 'git add' first."
        )

    prepared = diff.prepare(diff_text)
    if diff.truncated:
        click.echo("Some file diffs were truncated to fit the model context.", err=True)

    with spinner():
        message = diff.say(prepared)
    click.echo(message)
