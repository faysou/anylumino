from __future__ import annotations

from pathlib import Path
from typing import Iterable

import anywidget
import traitlets as t


PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"

TAB_PLACEMENTS = ("top", "bottom", "left", "right")


def _widget_ref(value: object) -> object:
    model_id = getattr(value, "model_id", None)
    if isinstance(model_id, str):
        return f"anywidget:{model_id}"
    return value


def _widget_list_to_json(value: list[object], _obj: object) -> list[object]:
    return [_widget_ref(item) for item in value]


def _widget_list_from_json(value: list[object], _obj: object) -> list[object]:
    return value


def _size_to_css(value: int | float | str | None, fallback: str) -> str:
    if value is None:
        return fallback
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        if 0 < value <= 1:
            return f"{value * 100}%"
        return f"{int(value)}px" if float(value).is_integer() else f"{value}px"
    return fallback


class TabPanel(anywidget.AnyWidget):
    _esm = STATIC_DIR / "tab_panel.js"
    _css = STATIC_DIR / "tab_panel.css"

    widgets = t.List(anywidget.WidgetTrait(), default_value=[]).tag(
        sync=True,
        to_json=_widget_list_to_json,
        from_json=_widget_list_from_json,
    )
    titles = t.List(t.Unicode(), default_value=[]).tag(sync=True)
    selected_index = t.Int(0).tag(sync=True)
    tab_placement = t.Enum(TAB_PLACEMENTS, default_value="top").tag(sync=True)
    tabs_movable = t.Bool(False).tag(sync=True)
    width = t.Unicode("100%").tag(sync=True)
    height = t.Unicode("420px").tag(sync=True)

    def __init__(
        self,
        widgets: Iterable[anywidget.Widget] | None = None,
        *,
        titles: Iterable[str] | None = None,
        selected_index: int = 0,
        tab_placement: str = "top",
        tabs_movable: bool = False,
        width: int | float | str | None = "100%",
        height: int | float | str | None = 420,
    ) -> None:
        widget_list = list(widgets or [])
        title_list = list(titles or [])
        if title_list and len(title_list) != len(widget_list):
            msg = "titles must be empty or have the same length as widgets"
            raise ValueError(msg)

        super().__init__(
            widgets=widget_list,
            titles=title_list,
            selected_index=selected_index,
            tab_placement=tab_placement,
            tabs_movable=tabs_movable,
            width=_size_to_css(width, "100%"),
            height=_size_to_css(height, "420px"),
        )

    def select(self, index: int) -> None:
        self.selected_index = index

    def add_tab(self, widget: anywidget.Widget, title: str | None = None, *, select: bool = False) -> None:
        next_index = len(self.widgets)
        with self.hold_sync():
            self.widgets = [*self.widgets, widget]
            self.titles = [*self.titles, title or f"Tab {next_index + 1}"]
            if select:
                self.selected_index = next_index


class TextWidget(anywidget.AnyWidget):
    _esm = STATIC_DIR / "text_widget.js"
    _css = STATIC_DIR / "text_widget.css"

    text = t.Unicode("").tag(sync=True)

    def __init__(self, text: str = "") -> None:
        super().__init__(text=text)
