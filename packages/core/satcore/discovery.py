"""Find installed app plugins via Python entry points."""

from __future__ import annotations

from importlib.metadata import entry_points

from .plugin import AppPlugin

ENTRY_POINT_GROUP = "introsat.apps"


def discover_plugins(group: str = ENTRY_POINT_GROUP) -> list[AppPlugin]:
    """Load every registered plugin, sorted by ``order``.

    A failure to load one plugin is reported but does not stop the others.
    """
    plugins: list[AppPlugin] = []
    for ep in entry_points(group=group):
        try:
            plugin = ep.load()()
        except Exception as exc:  # noqa: BLE001 - one bad app must not kill the rest
            print(f"[discovery] failed to load plugin '{ep.name}': {exc}")
            continue
        plugins.append(plugin)
    plugins.sort(key=lambda p: getattr(p, "order", 100))
    return plugins
