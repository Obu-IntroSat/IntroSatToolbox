"""Shared core for IntroSat Toolbox applications.

This package holds everything that every app needs:
- the plugin contract (`AppPlugin`) that turns an app into a tab,
- plugin discovery used by the launcher,
- helpers for serial I/O, external processes and background work,
- a tiny runtime helper to run any app as a standalone window.
"""

from .plugin import AppPlugin
from .discovery import discover_plugins
from .runtime import run_standalone

__all__ = ["AppPlugin", "discover_plugins", "run_standalone"]

__version__ = "0.1.0"
