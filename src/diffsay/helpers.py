from __future__ import annotations

import subprocess
import sys


def is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def commit(message: str) -> None:
    subprocess.check_call(["git", "commit", "-m", message])


def edit_message(default: str, prompt_text: str = "Commit: ") -> str:
    from prompt_toolkit import prompt

    return prompt(prompt_text, default=default)
