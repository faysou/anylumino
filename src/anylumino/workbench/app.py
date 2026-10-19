"""The App base class: the controller that holds a UI's data and handles its events."""

from __future__ import annotations

import warnings
from collections.abc import Callable
from typing import Any


class App:
    """Hold the data of a generated UI and handle its events.

    Subclass ``App`` with one ``handler(self, event)`` method per
    ``@Callback`` handler, and optionally ``setup(self)``. A generated
    ``UI(app)`` is the widget; the app works without one, for example to
    call a handler in a test.

    Parameters
    ----------
    **namespace : Any
        Data the handlers use, stored as attributes: ``SalesApp(sales=sales)``
        gives the handlers ``self.sales``. ``Widget(name)`` in the UI mounts
        the widget passed under ``name``.

    Raises
    ------
    ValueError
        If a name is not an identifier, starts with ``_``, or an ``App``
        attribute or method already uses it.

    Notes
    -----
    Set ``on_error`` to receive handler exceptions as ``on_error(handler,
    error)`` instead of raising them, and ``agent`` to receive
    ``ask_agent(message, context)`` calls.
    """

    # Declared on the class so that namespace names cannot replace them
    ui: Any = None
    agent: Callable[[str, Any], None] | None = None
    on_error: Callable[[str, Exception], None] | None = None

    def __init__(self, **namespace: Any) -> None:
        for name, value in namespace.items():
            if not name.isidentifier() or name.startswith("_") or hasattr(type(self), name):
                raise ValueError(f"{name!r} cannot be an App namespace name; it is not an identifier or the App uses it")
            setattr(self, name, value)

    def set_ui(self, ui: Any) -> None:
        """Keep ``ui`` as ``self.ui`` and run ``setup``; a generated ``UI(app)`` calls it."""
        self.ui = ui
        self.call("setup")

    def setup(self) -> None:
        """Fill the UI after it is built; override it to load data into widgets."""

    def call(self, handler: str, *args: Any) -> None:
        """Run the ``handler`` method with ``args``, passing an exception to ``on_error`` when set."""
        try:
            getattr(self, handler)(*args)
        except Exception as error:
            if self.on_error is None:
                raise
            self.on_error(handler, error)

    def ask_agent(self, message: str, context: Any = None) -> None:
        """Send ``message`` to the workbench agent; warns when no agent is attached."""
        if self.agent is None:
            warnings.warn(f"No workbench is attached, so ask_agent ignored {message!r}.", stacklevel=2)
            return
        self.agent(message, context)
