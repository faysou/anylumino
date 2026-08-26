from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from datetime import date
from datetime import datetime
from datetime import time
from pathlib import Path
from typing import Any


PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"


class ActivationCallbacks:
    """Shared activation callback registration for anylumino widgets.

    Every anylumino widget family registers Python callbacks the same way:
    ``on_click(callback)`` runs for each frontend activation, and
    ``on_action(callback)`` runs only for activations that carry a value, such
    as a chosen menu item or a changed control value. Both accept
    ``remove=True`` to unregister the same callable.

    Use ``traitlets.link`` or ``observe`` to keep sibling widgets in sync;
    callbacks are for reacting to activations, not for mirroring state.
    """

    def _init_callbacks(self) -> None:
        self._click_callbacks: list[Callable[..., None]] = []
        self._action_callbacks: list[Callable[..., None]] = []

    def _register_callbacks(
        self,
        callbacks: Iterable[Callable[..., None]] | None = None,
        action_callbacks: Iterable[Callable[..., None]] | None = None,
    ) -> None:
        for callback in callbacks or ():
            self.on_click(callback)
        for callback in action_callbacks or ():
            self.on_action(callback)

    def on_click(self, callback: Callable[..., None], remove: bool = False) -> None:
        """Register or unregister a callback for activations."""
        if remove:
            self._click_callbacks = [item for item in self._click_callbacks if item is not callback]
            return
        self._click_callbacks.append(callback)

    def on_action(self, callback: Callable[..., None], remove: bool = False) -> None:
        """Register or unregister a callback for activations that carry a value."""
        if remove:
            self._action_callbacks = [item for item in self._action_callbacks if item is not callback]
            return
        self._action_callbacks.append(callback)

    def _notify_action(self, value: Any) -> None:
        for callback in list(self._action_callbacks):
            callback(self, value)

    def _notify_click(self) -> None:
        for callback in list(self._click_callbacks):
            callback(self)


class LazyStaticAsset:
    def __init__(self, path: Path) -> None:
        self._path = path

    def __str__(self) -> str:
        try:
            return self._path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            msg = f"anylumino static asset is missing: {self._path}. Run `npm run build`."
            raise FileNotFoundError(msg) from exc


def static_asset(filename: str) -> Path | LazyStaticAsset:
    path = STATIC_DIR / filename
    if path.is_file():
        return path
    return LazyStaticAsset(path)


def json_value(value: Any) -> Any:
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, tuple):
        return [json_value(item) for item in value]
    if isinstance(value, list):
        return [json_value(item) for item in value]
    return value


def options_tuple(options: Iterable[Any] | None) -> tuple[Any, ...]:
    if options is None:
        return ()
    if isinstance(options, Mapping):
        return tuple((str(label), json_value(value)) for label, value in options.items())

    normalized = []
    for option in options:
        if isinstance(option, (list, tuple)) and len(option) == 2:
            label, value = option
            normalized.append((str(label), json_value(value)))
        else:
            normalized.append(json_value(option))
    return tuple(normalized)


def option_value(option: Any) -> Any:
    if isinstance(option, (list, tuple)) and len(option) == 2:
        return option[1]
    return option
