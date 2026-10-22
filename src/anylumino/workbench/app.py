"""The App, View, and Event classes behind a generated UI: the controller, the view, and an event."""

from __future__ import annotations

import sys
import warnings
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Event:
    """A widget event passed to a handler.

    Attributes
    ----------
    source : str
        The statement name of the component that fired.
    value : Any
        The new value for a value change, or `None` for a click.
    context : Any
        The second ``@Callback`` argument, or `None`.
    """

    source: str
    value: Any = None
    context: Any = None


class App:
    """Hold the data of a generated UI and handle its events.

    Subclass ``App`` with one ``handler(self, event)`` method per
    ``@Callback`` handler, and optionally ``setup(self)``. A generated
    ``UI(app)`` builds the widgets for the app and is what a notebook cell
    shows. The handlers read and change those widgets through ``self.ui``.
    A ``UI`` builds without being displayed, so a test can create one, call a
    handler, and check the widgets.

    One app drives one UI: ``UI(app)`` calls `set_ui`, which runs ``setup``,
    and a second ``UI`` for the same app raises. Create a new app for each UI.

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
        """Keep ``ui`` as ``self.ui`` and run ``setup``; a generated ``UI(app)`` calls it.

        Raises
        ------
        RuntimeError
            If the app already drives another UI, whose handlers would then
            change the new one.
        """
        if self.ui is not None and self.ui is not ui:
            raise RuntimeError(f"This {type(self).__name__} already drives a UI; create a new app for each UI.")

        self.ui = ui
        self.call("setup")
        # A Plotly FigureWidget sends its changes as messages that only a rendered figure keeps,
        # and copies the whole figure into its synced state only when it is displayed. A figure
        # inside a container is not displayed itself, so marimo, which renders it later, would
        # show the figure without what setup added.
        figure_widget = getattr(sys.modules.get("plotly.basewidget"), "BaseFigureWidget", None)
        if figure_widget is not None and isinstance(ui, View):
            for widget in vars(ui).values():
                if isinstance(widget, figure_widget):
                    widget._repr_mimebundle_()

    def setup(self) -> None:
        """Fill the UI while it is built; override it to load data into widgets."""

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


class View:
    """The base of a generated ``UI``: its widgets by statement name, and its root ``widget``.

    A view is not a widget itself. anylumino containers accept it as a child,
    since they mount its ``widget``, and a notebook cell shows that widget.
    Keeping the widgets on a plain object leaves statement names free, apart
    from ``app`` and ``widget``.

    Attributes
    ----------
    app : App
        The app that handles the view's events.
    widget : Any
        The root widget, set when the view is built.
    """

    app: App
    widget: Any = None

    def _repr_mimebundle_(self, **kwargs: Any) -> Any:
        return self.widget._repr_mimebundle_(**kwargs)
