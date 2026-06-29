"""Run external tools (flashers like avrdude/openocd/esptool) and stream output."""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Sequence


def run_command(
    cmd: Sequence[str],
    on_output: Callable[[str], None] | None = None,
) -> int:
    """Run ``cmd`` and stream combined stdout/stderr line by line.

    Returns the process exit code. ``on_output`` is called for every line as
    it arrives, which makes it easy to pipe a flasher's progress into a log
    widget. Call this from a background thread to keep the GUI responsive.
    """
    process = subprocess.Popen(
        list(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    for line in process.stdout:
        if on_output is not None:
            on_output(line.rstrip("\n"))
    process.stdout.close()
    return process.wait()
