from __future__ import annotations

import itertools
import os
import sys
import threading
from collections.abc import Iterator
from contextlib import contextmanager

_FRAMES = "|/-\\"


def _write(text: str) -> None:
    try:
        os.write(sys.stderr.fileno(), text.encode())
    except (AttributeError, OSError, ValueError):
        sys.stderr.write(text)
        sys.stderr.flush()


@contextmanager
def spinner(message: str = "Generating commit message...") -> Iterator[None]:
    if not sys.stderr.isatty():
        yield
        return

    stop = threading.Event()

    def render(frame: str) -> None:
        _write(f"\r{frame} {message}")

    def run() -> None:
        frames = itertools.cycle(_FRAMES)
        next(frames)  # first frame is already on screen
        while not stop.wait(0.08):
            render(next(frames))

    render(_FRAMES[0])
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join()
        _write("\r\033[2K")
