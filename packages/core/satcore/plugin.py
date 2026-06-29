"""The contract every app must implement to become a tab in the launcher."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget


class AppPlugin:
    """Base class for an application that can live inside the launcher.

    An app becomes a tab by subclassing this and implementing
    :meth:`create_widget`. The launcher discovers plugins through the
    ``introsat.apps`` entry point group, so adding a new app never requires
    touching the launcher itself.
    """

    #: Stable machine id, e.g. "comms" or "firmware".
    id: str = "plugin"

    #: Human-readable tab title.
    title: str = "Plugin"

    #: Lower numbers appear first among the tabs.
    order: int = 100

    def create_widget(self, parent: QWidget | None = None) -> QWidget:
        """Build and return the root widget of the application."""
        raise NotImplementedError
