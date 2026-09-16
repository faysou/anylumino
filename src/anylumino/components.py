from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from typing import Any

import anywidget
import traitlets as t

from .layout import ChildInput
from .layout import TitleInput
from .layout import KeyedChildren
from .layout import _normalize_children
from .layout import _size_to_css
from .layout import _widget_list_from_json
from .layout import _widget_list_to_json


ActionCallback = Callable[["ComponentWidget", Any], None]


class ComponentWidget(KeyedChildren, anywidget.AnyWidget):
    """Base class for composable component-library anywidgets.

    Component families inherit this class to share child composition, keyed
    access, open/close state, size traits, and activation callbacks.

    ``on_click`` runs for every activation and ``on_action`` runs only for
    activations that carry a value, so a menu item choice runs both. To mirror
    state between sibling widgets use ``traitlets.link`` or ``observe`` rather
    than callbacks.
    """

    component_family = t.Unicode("").tag(sync=True)
    component_kind = t.Unicode("element").tag(sync=True)
    tag = t.Unicode("").tag(sync=True)
    widgets = t.List(anywidget.WidgetTrait(), default_value=[]).tag(
        sync=True,
        to_json=_widget_list_to_json,
        from_json=_widget_list_from_json,
    )
    child_keys = t.List(t.Unicode(), default_value=[]).tag(sync=True)
    titles = t.List(t.Unicode(), default_value=[]).tag(sync=True)
    text = t.Unicode("").tag(sync=True)
    label = t.Unicode("").tag(sync=True)
    value = t.Any(None, allow_none=True).tag(sync=True)
    is_open = t.Bool(False).tag(sync=True)
    disabled = t.Bool(False).tag(sync=True)
    selected = t.Bool(False).tag(sync=True)
    indeterminate = t.Bool(False).tag(sync=True)
    variant = t.Unicode("").tag(sync=True)
    placement = t.Unicode("bottom").tag(sync=True)
    orientation = t.Unicode("horizontal").tag(sync=True)
    width = t.Unicode("").tag(sync=True)
    height = t.Unicode("").tag(sync=True)
    icon = t.Unicode("").tag(sync=True)
    icon_src = t.Unicode("").tag(sync=True)
    icon_size = t.Unicode("s").tag(sync=True)
    attributes = t.Dict(default_value={}).tag(sync=True)
    last_action = t.Any(None, allow_none=True).tag(sync=True)

    def __init__(
        self,
        children: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        action_callbacks: Iterable[ActionCallback] | None = None,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        **kwargs: Any,
    ) -> None:
        widget_list, owner_list, key_list, title_list = _normalize_children(
            children, titles, keys
        )
        self._owners_by_key = dict(zip(key_list, owner_list, strict=True))
        self._init_callbacks()
        self._syncing_children = True
        try:
            super().__init__(
                widgets=widget_list,
                child_keys=key_list,
                titles=title_list,
                width=_size_to_css(width, ""),
                height=_size_to_css(height, ""),
                **kwargs,
            )
        finally:
            self._syncing_children = False
        self.observe(self._observe_widgets, names="widgets")
        self.on_msg(self._handle_frontend_message)
        self._register_callbacks(callbacks, action_callbacks)

    def show(self) -> None:
        """Open overlay-like components."""
        self.is_open = True

    def hide(self) -> None:
        """Close overlay-like components."""
        self.is_open = False

    def toggle(self) -> None:
        """Toggle overlay-like components."""
        self.is_open = not self.is_open

    def _handle_frontend_message(
        self, _widget: object, content: dict[str, Any], _buffers: object
    ) -> None:
        msg_type = content.get("type")
        if msg_type == "open":
            self.is_open = bool(content.get("is_open", True))
            return
        if msg_type == "close":
            self.is_open = False
            return
        if msg_type != "click":
            return
        if "value" in content or "action" in content:
            self.last_action = content.get("value", content.get("action"))
            self._notify_action(self.last_action)
        self._notify_click()


__all__ = ["ComponentWidget"]
