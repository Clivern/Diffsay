from __future__ import annotations

import subprocess
import sys


def is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def commit(message: str) -> None:
    subprocess.check_call(["git", "commit", "-m", message])
