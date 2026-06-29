"""Run a blocking callable on a background thread without freezing the GUI."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QThread, Signal


class Worker(QObject):
    """Runs ``fn(*args, **kwargs)`` in a QThread and reports the result.

    Connect to :attr:`output` for streamed log lines, :attr:`finished` for the
    return value and :attr:`failed` for exceptions. A ``report`` callable is
    injected as a keyword argument if ``fn`` accepts one, so long tasks can emit
    progress lines.
    """

    output = Signal(str)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self) -> None:
        try:
            result = self._fn(*self._args, report=self.output.emit, **self._kwargs)
        except TypeError:
            # fn does not accept a `report` keyword - call it plainly.
            try:
                result = self._fn(*self._args, **self._kwargs)
            except Exception as exc:  # noqa: BLE001
                self.failed.emit(str(exc))
                return
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))
            return
        self.finished.emit(result)


def run_in_thread(parent: QObject, worker: Worker) -> QThread:
    """Move ``worker`` onto a fresh QThread, start it, and wire up cleanup.

    The returned thread is parented to ``parent`` so it stays alive while the
    work runs. The thread quits itself once the worker finishes or fails.
    """
    thread = QThread(parent)
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.failed.connect(thread.quit)
    thread.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    thread.start()
    return thread
