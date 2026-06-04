from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from typing import Any

import anywidget
import traitlets as t

from ._layout import ChildInput
from ._layout import TitleInput
from ._layout import _normalize_children
from ._layout import _size_to_css
from ._layout import _widget_list_from_json
from ._layout import _widget_list_to_json


class ComponentWidget(anywidget.AnyWidget):
    """Base class for composable component-library anywidgets.

    Component families such as ``SpectrumWidget`` inherit this class to share
    child composition, keyed access, open/close state, size traits, and
    activation callbacks.
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

    def __init__(
        self,
        children: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        **kwargs: Any,
    ) -> None:
        widget_list, owner_list, key_list, title_list = _normalize_children(children, titles, keys)
        self._owners_by_key = dict(zip(key_list, owner_list, strict=True))
        self._click_callbacks: list[Callable[[ComponentWidget], None]] = []
        super().__init__(
            widgets=widget_list,
            child_keys=key_list,
            titles=title_list,
            width=_size_to_css(width, ""),
            height=_size_to_css(height, ""),
            **kwargs,
        )
        self.on_msg(self._handle_frontend_message)
        if callbacks is not None:
            for callback in callbacks:
                self.on_click(callback)

    def __contains__(self, key: object) -> bool:
        return str(key) in self.child_keys

    def __getitem__(self, key: str) -> object:
        return self.get_owner(key)

    def get_owner(self, key_or_index: str | int) -> object:
        index = self._resolve_index(key_or_index)
        key = self.child_keys[index]
        return self._owners_by_key.get(key, self.widgets[index])

    def show(self) -> None:
        """Open overlay-like components."""
        self.is_open = True

    def hide(self) -> None:
        """Close overlay-like components."""
        self.is_open = False

    def toggle(self) -> None:
        """Toggle overlay-like components."""
        self.is_open = not self.is_open

    def on_click(
        self,
        callback: Callable[[ComponentWidget], None],
        remove: bool = False,
    ) -> None:
        """Register or unregister a callback for activations."""
        if remove:
            self._click_callbacks = [item for item in self._click_callbacks if item is not callback]
            return
        self._click_callbacks.append(callback)

    def _resolve_index(self, key_or_index: str | int) -> int:
        if isinstance(key_or_index, int):
            return key_or_index
        return self.child_keys.index(str(key_or_index))

    def _handle_frontend_message(self, _widget: object, content: dict[str, Any], _buffers: object) -> None:
        msg_type = content.get("type")
        if msg_type == "open":
            self.is_open = True
            return
        if msg_type == "close":
            self.is_open = False
            return
        if msg_type != "click":
            return
        for callback in list(self._click_callbacks):
            callback(self)


__all__ = ["ComponentWidget"]
