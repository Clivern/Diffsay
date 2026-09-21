from __future__ import annotations

import click

from diffsay.diff import Diff
from diffsay.helpers import commit, edit_message, is_interactive
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
@click.option(
    "-p",
    "--print-only",
    is_flag=True,
    help="Print the message and exit instead of committing.",
)
def main(model: str, print_only: bool) -> None:
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

    if print_only or not is_interactive():
        click.echo(message)
        return

    message = edit_message(message)
    if not message.strip():
        raise click.ClickException("Empty commit message.")
    commit(message)
