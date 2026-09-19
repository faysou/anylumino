from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, Iterable

import anywidget
import traitlets as t

# anywidget keeps the model id lookup private until
# https://github.com/manzt/anywidget/pull/1024 lands.
from anywidget._descriptor import _try_get_model_id as get_model_id

from .common import ActivationCallbacks
from .common import static_asset


TAB_PLACEMENTS = ("top", "bottom", "left", "right")
BOX_DIRECTIONS = ("left-to-right", "right-to-left", "top-to-bottom", "bottom-to-top")
ORIENTATIONS = ("horizontal", "vertical")
DOCK_MODES = ("tab-after", "split-right", "split-left", "split-top", "split-bottom")
ACTION_KINDS = ("toolbar", "menubar", "command_palette")
ActionCallback = Callable[[str], None]
ChildInput = Iterable[object] | Mapping[str, object] | None
TitleInput = Iterable[str] | Mapping[str, str] | None


def _is_widget(value: object) -> bool:
    return get_model_id(value) is not None


def _widget_ref(value: object) -> object:
    model_id = get_model_id(value)
    if model_id is not None:
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
            return f"{value * 100:g}%"
        return f"{int(value)}px" if float(value).is_integer() else f"{value}px"
    return fallback


def _as_list(values: Iterable[Any] | None) -> list[Any]:
    return list(values or [])


def _validate_titles(widget_list: list[object], title_list: list[str]) -> None:
    if title_list and len(title_list) != len(widget_list):
        msg = "titles must be empty or have the same length as widgets"
        raise ValueError(msg)


def _key_to_string(key: object) -> str:
    text = str(key).strip()
    if not text:
        msg = "widget keys must not be empty"
        raise ValueError(msg)
    return text


def _validate_keys(key_list: list[str]) -> None:
    if len(set(key_list)) != len(key_list):
        msg = "widget keys must be unique"
        raise ValueError(msg)


def _view_for_child(child: object) -> object:
    if _is_widget(child):
        return child
    view = getattr(child, "widget", None)
    if _is_widget(view):
        return view
    return child


def _is_child(value: object) -> bool:
    if _is_widget(value):
        return True
    return _is_widget(getattr(value, "widget", None))


def _as_child_list(children: ChildInput) -> list[Any]:
    if children is None:
        return []
    if _is_child(children):
        return [children]
    return list(children)


def _normalize_keys(keys: Iterable[str] | None, length: int) -> list[str]:
    if keys is None:
        key_list = [f"widget-{index + 1}" for index in range(length)]
    else:
        key_list = [_key_to_string(key) for key in keys]
        if len(key_list) != length:
            msg = "keys must have the same length as widgets"
            raise ValueError(msg)
    _validate_keys(key_list)
    return key_list


def _normalize_titles(
    titles: TitleInput,
    key_list: list[str],
    *,
    default_to_keys: bool,
) -> list[str]:
    if titles is None:
        return list(key_list) if default_to_keys else []
    if isinstance(titles, Mapping):
        return [str(titles.get(key, key if default_to_keys else "")) for key in key_list]
    title_list = [str(title) for title in titles]
    if len(title_list) != len(key_list):
        msg = "titles must be empty or have the same length as widgets"
        raise ValueError(msg)
    return title_list


def _normalize_children(
    children: ChildInput,
    titles: TitleInput,
    keys: Iterable[str] | None,
) -> tuple[list[object], list[object], list[str], list[str]]:
    if isinstance(children, Mapping):
        if keys is not None:
            msg = "keys cannot be passed when widgets is a mapping"
            raise ValueError(msg)
        key_list = [_key_to_string(key) for key in children]
        _validate_keys(key_list)
        owner_list = list(children.values())
        title_list = _normalize_titles(titles, key_list, default_to_keys=True)
    else:
        owner_list = _as_child_list(children)
        key_list = _normalize_keys(keys, len(owner_list))
        title_list = _normalize_titles(titles, key_list, default_to_keys=False)

    widget_list = [_view_for_child(child) for child in owner_list]
    _validate_titles(widget_list, title_list)
    return widget_list, owner_list, key_list, title_list


class KeyedChildren(ActivationCallbacks):
    """Keyed access to the children of a composed anylumino widget.

    Lumino layout widgets and Astryx widgets share this base. Children are
    stored as a synced ``widgets`` list of rendered views plus a parallel
    ``child_keys`` list. ``get_widget`` returns the view that renders in the
    browser and ``get_owner`` returns the object that was passed in, so
    wrapper objects exposing a ``widget`` attribute keep their own API.
    Subscripting returns the owner. Widgets with a ``selected_index`` trait
    also gain ``selected_key`` and ``select_key``.
    """

    _title_prefix = "Widget"

    widgets: list[Any]
    child_keys: list[str]
    titles: list[str]
    _owners_by_key: dict[str, Any]
    _syncing_children: bool

    def __contains__(self, key: object) -> bool:
        if isinstance(key, bool):
            return False
        if isinstance(key, int):
            return -len(self.child_keys) <= key < len(self.child_keys)
        return str(key).strip() in self.child_keys

    def __getitem__(self, key_or_index: str | int) -> object:
        return self.get_owner(key_or_index)

    def __iter__(self) -> Any:
        msg = (
            f"{type(self).__name__} is not iterable. Pass children as a list or mapping, "
            "and read one child with get_widget or get_owner."
        )
        raise TypeError(msg)

    def get_index(self, key: str) -> int:
        return self._resolve_index(key)

    def get_key(self, index: int) -> str:
        return self.child_keys[self._resolve_index(index)]

    def get_widget(self, key_or_index: str | int) -> object:
        return self.widgets[self._resolve_index(key_or_index)]

    def get_owner(self, key_or_index: str | int) -> object:
        index = self._resolve_index(key_or_index)
        return self._owners_by_key.get(self.child_keys[index], self.widgets[index])

    def _resolve_index(self, key_or_index: str | int) -> int:
        count = len(self.child_keys)
        if isinstance(key_or_index, int) and not isinstance(key_or_index, bool):
            if -count <= key_or_index < count:
                return key_or_index if key_or_index >= 0 else count + key_or_index
            msg = f"widget index out of range: {key_or_index}"
            raise IndexError(msg)
        key = str(key_or_index).strip()
        try:
            return self.child_keys.index(key)
        except ValueError:
            available = ", ".join(self.child_keys) or "none"
            msg = f"unknown widget key {key!r}; available keys: {available}"
            raise KeyError(msg) from None

    def _adopt_children(self, views: Iterable[object]) -> None:
        """Apply parent-owned state to newly attached children."""

    def _drop_child_metadata(self, index: int) -> None:
        """Drop per-child metadata for a child that was removed."""

    def _rekey_children(self, previous: list[object], current: list[object]) -> None:
        selected_key = getattr(self, "selected_key", None)
        previous_keys = {id(view): key for view, key in zip(previous, self.child_keys)}
        titles_by_key = dict(zip(self.child_keys, self._complete_titles()))
        key_list: list[str] = []
        adopted: list[object] = []
        for view in current:
            key = previous_keys.pop(id(view), None)
            if key is None:
                key = self._unused_key(key_list)
                adopted.append(view)
            key_list.append(key)
        owners = {key: self._owners_by_key.get(key, view) for key, view in zip(key_list, current)}
        self._syncing_children = True
        try:
            with self.hold_sync():
                self.child_keys = key_list
                self.titles = [titles_by_key.get(key, "") for key in key_list]
                self._owners_by_key = owners
                self._restore_selection(selected_key)
        finally:
            self._syncing_children = False
        self._adopt_children(adopted)

    def _observe_widgets(self, change: dict[str, Any]) -> None:
        if self._syncing_children:
            return
        self._rekey_children(list(change["old"]), list(change["new"]))

    def _unused_key(self, taken: Iterable[str]) -> str:
        used = set(self.child_keys) | set(taken)
        index = len(used) + 1
        while f"widget-{index}" in used:
            index += 1
        return f"widget-{index}"

    def _restore_selection(self, selected_key: str | None) -> None:
        if not hasattr(self, "selected_index"):
            return
        if selected_key in self.child_keys:
            self.selected_index = self.child_keys.index(selected_key)
        else:
            self.selected_index = max(0, min(self.selected_index, len(self.child_keys) - 1))

    @property
    def selected_key(self) -> str | None:
        selected_index = getattr(self, "selected_index", None)
        if selected_index is None or not self.child_keys:
            return None
        if selected_index < 0 or selected_index >= len(self.child_keys):
            return None
        return self.child_keys[selected_index]

    @property
    def selected_widget(self) -> object | None:
        selected_key = self.selected_key
        return self.get_widget(selected_key) if selected_key is not None else None

    @property
    def selected_owner(self) -> object | None:
        selected_key = self.selected_key
        return self.get_owner(selected_key) if selected_key is not None else None

    def select_key(self, key: str) -> None:
        if not hasattr(self, "selected_index"):
            msg = f"{type(self).__name__} does not support selection"
            raise AttributeError(msg)
        self.selected_index = self.get_index(key)

    def apply_widget(self, key_or_index: str | int, callback: Callable[[object], Any]) -> Any:
        return callback(self.get_widget(key_or_index))

    def apply_owner(self, key_or_index: str | int, callback: Callable[[object], Any]) -> Any:
        return callback(self.get_owner(key_or_index))

    def call_widget(self, key_or_index: str | int, method_name: str, *args: Any, **kwargs: Any) -> Any:
        return getattr(self.get_widget(key_or_index), method_name)(*args, **kwargs)

    def call_owner(self, key_or_index: str | int, method_name: str, *args: Any, **kwargs: Any) -> Any:
        return getattr(self.get_owner(key_or_index), method_name)(*args, **kwargs)

    def add(
        self,
        key: str,
        widget: object,
        *,
        title: str | None = None,
        select: bool = False,
    ) -> None:
        self.add_widget(widget, title=title, key=key, select=select)

    def add_widget(
        self,
        widget: object,
        title: str | None = None,
        *,
        key: str | None = None,
        select: bool = False,
    ) -> None:
        next_index = len(self.widgets)
        has_explicit_key = key is not None
        child_key = self._next_key(key)
        child_title = title or (child_key if has_explicit_key else f"{self._title_prefix} {next_index + 1}")
        view = _view_for_child(widget)
        titles = self._complete_titles()
        self._syncing_children = True
        try:
            with self.hold_sync():
                self.widgets = [*self.widgets, view]
                self.child_keys = [*self.child_keys, child_key]
                self.titles = [*titles, child_title]
                self._owners_by_key[child_key] = widget
                if select and hasattr(self, "selected_index"):
                    self.selected_index = next_index
        finally:
            self._syncing_children = False
        self._adopt_children([view])

    def remove_widget(self, key_or_index: str | int, *, close: bool = False) -> object:
        """Remove a child and return the owner that was passed in.

        Pass ``close=True`` to also close the removed widget models. Closing
        releases them from the ipywidgets registry and makes them unusable, so
        the default keeps the returned owner alive for the caller to reuse.
        """
        index = self._resolve_index(key_or_index)
        key = self.child_keys[index]
        owner = self.get_owner(index)
        view = self.widgets[index]
        selected_key = self.selected_key
        titles = self._complete_titles()
        self._syncing_children = True
        try:
            with self.hold_sync():
                self.widgets = [*self.widgets[:index], *self.widgets[index + 1 :]]
                self.child_keys = [*self.child_keys[:index], *self.child_keys[index + 1 :]]
                self.titles = [*titles[:index], *titles[index + 1 :]]
                self._owners_by_key.pop(key, None)
                self._drop_child_metadata(index)
                self._restore_selection(selected_key)
        finally:
            self._syncing_children = False
        if close:
            for target in {id(view): view, id(owner): owner}.values():
                closer = getattr(target, "close", None)
                if callable(closer):
                    closer()
        return owner

    def move_widget(self, key_or_index: str | int, index: int) -> None:
        """Move a child to a new position, keeping keys and titles aligned."""
        current = self._resolve_index(key_or_index)
        target = max(0, min(len(self.child_keys) - 1, index))
        if current == target:
            return
        selected_key = self.selected_key
        titles = self._complete_titles()
        order = [position for position in range(len(self.child_keys)) if position != current]
        order.insert(target, current)
        self._syncing_children = True
        try:
            with self.hold_sync():
                self.widgets = [self.widgets[position] for position in order]
                self.child_keys = [self.child_keys[position] for position in order]
                self.titles = [titles[position] for position in order]
                self._restore_selection(selected_key)
        finally:
            self._syncing_children = False

    def rename_widget(self, key_or_index: str | int, title: str) -> None:
        index = self._resolve_index(key_or_index)
        titles = self._complete_titles()
        titles[index] = title
        self.titles = titles

    def _next_key(self, key: str | None = None) -> str:
        if key is not None:
            child_key = _key_to_string(key)
            if child_key in self.child_keys:
                msg = f"widget key already exists: {child_key}"
                raise ValueError(msg)
            return child_key
        return self._unused_key(())

    def _complete_titles(self) -> list[str]:
        titles = list(self.titles)
        complete = []
        for index, key in enumerate(self.child_keys):
            if index < len(titles) and titles[index]:
                complete.append(titles[index])
            elif key.startswith("widget-"):
                complete.append(f"{self._title_prefix} {index + 1}")
            else:
                complete.append(key)
        return complete

class LayoutWidget(KeyedChildren, anywidget.AnyWidget):
    """Base class for keyed anywidget composition layouts.

    ``LayoutWidget`` stores child widgets in a keyed map while syncing the
    frontend-ready widget views to the browser. Subclasses choose the Lumino
    layout that displays those children.
    """

    widgets = t.List(anywidget.WidgetTrait(), default_value=[]).tag(
        sync=True,
        to_json=_widget_list_to_json,
        from_json=_widget_list_from_json,
    )
    child_keys = t.List(t.Unicode(), default_value=[]).tag(sync=True)
    titles = t.List(t.Unicode(), default_value=[]).tag(sync=True)
    width = t.Unicode("100%").tag(sync=True)
    height = t.Unicode("420px").tag(sync=True)
    resizable = t.Bool(True).tag(sync=True)
    scroll_x = t.Bool(False).tag(sync=True)
    scroll_y = t.Bool(False).tag(sync=True)
    child_min_width = t.Unicode("0px").tag(sync=True)
    child_min_height = t.Unicode("0px").tag(sync=True)
    fit_content = t.Bool(False).tag(sync=True)

    def _init_composed(
        self,
        widgets: ChildInput,
        titles: TitleInput,
        keys: Iterable[str] | None,
        width: int | float | str | None,
        height: int | float | str | None,
        resizable: bool,
        scroll_x: bool = False,
        scroll_y: bool = False,
        child_min_width: int | float | str | None = None,
        child_min_height: int | float | str | None = None,
        fit_content: bool = False,
        **kwargs: Any,
    ) -> None:
        widget_list, owner_list, key_list, title_list = _normalize_children(widgets, titles, keys)
        self._owners_by_key = dict(zip(key_list, owner_list, strict=True))
        self._init_callbacks()
        self._syncing_children = True
        try:
            super().__init__(
                widgets=widget_list,
                child_keys=key_list,
                titles=title_list,
                width=_size_to_css(width, "100%"),
                height=_size_to_css(height, "420px"),
                resizable=resizable,
                scroll_x=scroll_x,
                scroll_y=scroll_y,
                child_min_width=_size_to_css(child_min_width, "0px"),
                child_min_height=_size_to_css(child_min_height, "0px"),
                fit_content=fit_content,
                **kwargs,
            )
        finally:
            self._syncing_children = False
        self.observe(self._observe_widgets, names="widgets")
        self.on_msg(self._handle_frontend_message)

    def _handle_frontend_message(self, _widget: object, content: dict[str, Any], _buffers: object) -> None:
        if content.get("type") != "move":
            return
        from_index = content.get("from")
        to_index = content.get("to")
        if not isinstance(from_index, int) or not isinstance(to_index, int):
            return
        if not 0 <= from_index < len(self.child_keys):
            return
        self.move_widget(from_index, to_index)


_ComposedWidget = LayoutWidget


class TabPanel(LayoutWidget):
    """Lumino tab container for composing child widgets.

    Children can be passed as a list or as a keyed mapping. Mapping keys become
    stable child identifiers and default tab titles. Use ``select_key`` or
    ``selected_index`` to choose the active tab.

    Parameters
    ----------
    widgets : iterable or mapping, optional
        Child anywidget-compatible widgets or owner objects exposing a
        ``widget`` attribute. When a mapping is passed, its keys become stable
        child keys.
    titles : iterable or mapping, optional
        Tab titles. A mapping is resolved by child key. When ``widgets`` is a
        mapping and titles are omitted, keys are used as titles.
    keys : iterable of str, optional
        Stable child keys for iterable ``widgets``. Do not pass this when
        ``widgets`` is a mapping.
    selected_index : int, default 0
        Initially selected tab index.
    tab_placement : {"top", "bottom", "left", "right"}, default "top"
        Where Lumino should place the tab bar.
    tabs_movable : bool, default False
        Whether tabs can be reordered in the frontend. A drag reorders
        ``widgets``, ``child_keys``, and ``titles`` in Python too, so
        ``selected_key`` keeps naming the visible child.
    width : int, float, str, or None
        Widget width. Numbers above 1 are pixels, numbers between 0 and 1 are
        percentages, and strings are passed through as CSS sizes.
    height : int, float, str, or None
        Widget height. Numbers above 1 are pixels, numbers between 0 and 1 are
        percentages, and strings are passed through as CSS sizes.
    resizable : bool, default True
        Whether the panel receives a notebook-friendly resize handle.
    """

    _esm = static_asset("layout/tab_panel.bundle.js")
    _css = static_asset("layout/tab_panel.css")
    _title_prefix = "Tab"

    selected_index = t.Int(0).tag(sync=True)
    tab_placement = t.Enum(TAB_PLACEMENTS, default_value="top").tag(sync=True)
    tabs_movable = t.Bool(False).tag(sync=True)

    def __init__(
        self,
        widgets: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        selected_index: int = 0,
        tab_placement: str = "top",
        tabs_movable: bool = False,
        width: int | float | str | None = "100%",
        height: int | float | str | None = 420,
        resizable: bool = True,
        fit_content: bool = False,
    ) -> None:
        self._init_composed(
            widgets,
            titles,
            keys,
            width,
            height,
            resizable,
            fit_content=fit_content,
            selected_index=selected_index,
            tab_placement=tab_placement,
            tabs_movable=tabs_movable,
        )

    def select(self, index: int) -> None:
        self.selected_index = index

    def add_tab(
        self,
        widget: object,
        title: str | None = None,
        *,
        key: str | None = None,
        select: bool = False,
    ) -> None:
        self.add_widget(widget, title=title, key=key, select=select)


class BoxPanel(LayoutWidget):
    """Lumino box layout with configurable direction, spacing, and stretch.

    ``HBox`` and ``VBox`` are direction-specific convenience subclasses. Set
    ``scroll=True`` to enable scrolling along the natural box direction, or use
    ``scroll_x`` and ``scroll_y`` for explicit overflow behavior.

    Parameters
    ----------
    widgets : iterable or mapping, optional
        Child anywidget-compatible widgets or owner objects exposing a
        ``widget`` attribute. Mapping keys become stable child keys and default
        titles.
    titles : iterable or mapping, optional
        Optional labels associated with children. Mapping values are looked up
        by child key.
    keys : iterable of str, optional
        Stable child keys for iterable ``widgets``.
    direction : {"left-to-right", "right-to-left", "top-to-bottom", "bottom-to-top"}
        Lumino box direction.
    spacing : int, default 8
        Pixel spacing between children.
    stretches : iterable of int, optional
        Lumino stretch factors, one per child when provided.
    width : int, float, str, or None
        Widget width. Numeric values use the shared anylumino size rules.
    height : int, float, str, or None
        Widget height. Numeric values use the shared anylumino size rules.
    resizable : bool, default True
        Whether the panel receives a notebook-friendly resize handle.
    scroll : bool, default False
        Enables scrolling along the natural layout direction.
    scroll_x, scroll_y : bool, optional
        Explicit horizontal or vertical overflow controls.
    child_min_width, child_min_height : int, float, str, or None
        Minimum child sizes used when scrolling is enabled.

    Notes
    -----
    A scrolling panel establishes an overflow boundary. Hosts that cap output
    height, such as VS Code notebooks, then show a scrollbar inside a scrollbar,
    and children that position popups within their own subtree are clipped at
    that boundary. Set ``fit_content=True`` instead when the panel should grow
    to its content rather than scroll.
    """

    _esm = static_asset("layout/layout_panel.bundle.js")
    _css = static_asset("layout/layout_panel.css")

    layout_kind = t.Unicode("box").tag(sync=True)
    direction = t.Enum(BOX_DIRECTIONS, default_value="left-to-right").tag(sync=True)
    spacing = t.Int(8).tag(sync=True)
    stretches = t.List(t.Int(), default_value=[]).tag(sync=True)

    def __init__(
        self,
        widgets: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        direction: str = "left-to-right",
        spacing: int = 8,
        stretches: Iterable[int] | None = None,
        width: int | float | str | None = "100%",
        height: int | float | str | None = 420,
        resizable: bool = True,
        scroll: bool = False,
        scroll_x: bool | None = None,
        scroll_y: bool | None = None,
        child_min_width: int | float | str | None = None,
        child_min_height: int | float | str | None = None,
        fit_content: bool = False,
    ) -> None:
        horizontal = direction in ("left-to-right", "right-to-left")
        resolved_scroll_x = bool(scroll_x if scroll_x is not None else scroll and horizontal)
        resolved_scroll_y = bool(scroll_y if scroll_y is not None else scroll and not horizontal)
        default_child_min_width = "220px" if resolved_scroll_x else None
        default_child_min_height = "44px" if resolved_scroll_y else None
        self._init_composed(
            widgets,
            titles,
            keys,
            width,
            height,
            resizable,
            resolved_scroll_x,
            resolved_scroll_y,
            child_min_width if child_min_width is not None else default_child_min_width,
            child_min_height if child_min_height is not None else default_child_min_height,
            fit_content=fit_content,
            direction=direction,
            spacing=spacing,
            stretches=_as_list(stretches),
        )

    def _drop_child_metadata(self, index: int) -> None:
        if index < len(self.stretches):
            self.stretches = [*self.stretches[:index], *self.stretches[index + 1 :]]


class HBox(BoxPanel):
    """Horizontal ``BoxPanel`` convenience wrapper.

    Parameters
    ----------
    widgets : iterable or mapping, optional
        Child widgets or keyed child mapping.
    titles : iterable or mapping, optional
        Optional labels associated with children.
    keys : iterable of str, optional
        Stable child keys for iterable ``widgets``.
    spacing : int, default 8
        Pixel spacing between children.
    stretches : iterable of int, optional
        Lumino stretch factors, one per child when provided.
    width : int, float, str, or None
        Widget width. Numeric values use the shared anylumino size rules.
    height : int, float, str, or None
        Widget height. Numeric values use the shared anylumino size rules.
    resizable : bool, default True
        Whether the panel receives a notebook-friendly resize handle.
    scroll : bool, default False
        Enables horizontal scrolling by default.
    scroll_x, scroll_y : bool, optional
        Explicit horizontal or vertical overflow controls.
    child_min_width, child_min_height : int, float, str, or None
        Minimum child sizes used when scrolling is enabled.
    """

    def __init__(
        self,
        widgets: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        spacing: int = 8,
        stretches: Iterable[int] | None = None,
        width: int | float | str | None = "100%",
        height: int | float | str | None = 420,
        resizable: bool = True,
        scroll: bool = False,
        scroll_x: bool | None = None,
        scroll_y: bool | None = None,
        child_min_width: int | float | str | None = None,
        child_min_height: int | float | str | None = None,
        fit_content: bool = False,
    ) -> None:
        super().__init__(
            widgets,
            titles=titles,
            keys=keys,
            direction="left-to-right",
            spacing=spacing,
            stretches=stretches,
            width=width,
            height=height,
            resizable=resizable,
            scroll=scroll,
            scroll_x=scroll_x,
            scroll_y=scroll_y,
            child_min_width=child_min_width,
            child_min_height=child_min_height,
            fit_content=fit_content,
        )


class VBox(BoxPanel):
    """Vertical ``BoxPanel`` convenience wrapper.

    Parameters
    ----------
    widgets : iterable or mapping, optional
        Child widgets or keyed child mapping.
    titles : iterable or mapping, optional
        Optional labels associated with children.
    keys : iterable of str, optional
        Stable child keys for iterable ``widgets``.
    spacing : int, default 8
        Pixel spacing between children.
    stretches : iterable of int, optional
        Lumino stretch factors, one per child when provided.
    width : int, float, str, or None
        Widget width. Numeric values use the shared anylumino size rules.
    height : int, float, str, or None
        Widget height. Numeric values use the shared anylumino size rules.
    resizable : bool, default True
        Whether the panel receives a notebook-friendly resize handle.
    scroll : bool, default False
        Enables vertical scrolling by default.
    scroll_x, scroll_y : bool, optional
        Explicit horizontal or vertical overflow controls.
    child_min_width, child_min_height : int, float, str, or None
        Minimum child sizes used when scrolling is enabled.
    """

    def __init__(
        self,
        widgets: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        spacing: int = 8,
        stretches: Iterable[int] | None = None,
        width: int | float | str | None = "100%",
        height: int | float | str | None = 420,
        resizable: bool = True,
        scroll: bool = False,
        scroll_x: bool | None = None,
        scroll_y: bool | None = None,
        child_min_width: int | float | str | None = None,
        child_min_height: int | float | str | None = None,
        fit_content: bool = False,
    ) -> None:
        super().__init__(
            widgets,
            titles=titles,
            keys=keys,
            direction="top-to-bottom",
            spacing=spacing,
            stretches=stretches,
            width=width,
            height=height,
            resizable=resizable,
            scroll=scroll,
            scroll_x=scroll_x,
            scroll_y=scroll_y,
            child_min_width=child_min_width,
            child_min_height=child_min_height,
            fit_content=fit_content,
        )


class ScrollBox(VBox):
    """Scrollable vertical box for notebook-sized control panels.

    Parameters
    ----------
    widgets : iterable or mapping, optional
        Child widgets or keyed child mapping.
    titles : iterable or mapping, optional
        Optional labels associated with children.
    keys : iterable of str, optional
        Stable child keys for iterable ``widgets``.
    spacing : int, default 8
        Pixel spacing between children.
    stretches : iterable of int, optional
        Lumino stretch factors, one per child when provided.
    width : int, float, str, or None
        Widget width. Numeric values use the shared anylumino size rules.
    height : int, float, str, or None
        Widget height. Numeric values use the shared anylumino size rules.
    resizable : bool, default True
        Whether the panel receives a notebook-friendly resize handle.
    scroll : bool, default True
        Enables vertical scrolling by default.
    scroll_x, scroll_y : bool, optional
        Explicit horizontal or vertical overflow controls.
    child_min_width, child_min_height : int, float, str, or None
        Minimum child sizes used when scrolling is enabled.
    """

    def __init__(
        self,
        widgets: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        spacing: int = 8,
        stretches: Iterable[int] | None = None,
        width: int | float | str | None = "100%",
        height: int | float | str | None = 420,
        resizable: bool = True,
        scroll: bool = True,
        scroll_x: bool | None = None,
        scroll_y: bool | None = None,
        child_min_width: int | float | str | None = None,
        child_min_height: int | float | str | None = None,
        fit_content: bool = False,
    ) -> None:
        super().__init__(
            widgets,
            titles=titles,
            keys=keys,
            spacing=spacing,
            stretches=stretches,
            width=width,
            height=height,
            resizable=resizable,
            scroll=scroll,
            scroll_x=scroll_x,
            scroll_y=scroll_y,
            child_min_width=child_min_width,
            child_min_height=child_min_height,
            fit_content=fit_content,
        )


class SplitPanel(LayoutWidget):
    """Lumino split panel with draggable dividers between children.

    Parameters
    ----------
    widgets : iterable or mapping, optional
        Child widgets or keyed child mapping. Mapping keys become stable child
        keys and default titles.
    titles : iterable or mapping, optional
        Optional labels associated with children.
    keys : iterable of str, optional
        Stable child keys for iterable ``widgets``.
    orientation : {"horizontal", "vertical"}, default "horizontal"
        Split direction. Horizontal places panes side by side; vertical stacks
        panes top to bottom.
    spacing : int, default 6
        Pixel spacing around Lumino split handles.
    sizes : iterable of float, optional
        Initial relative pane sizes. Values are passed to Lumino as ratios.
    width : int, float, str, or None
        Widget width.
    height : int, float, str, or None
        Widget height.
    resizable : bool, default True
        Whether the whole panel gets a notebook resize handle. Lumino pane
        dividers remain draggable independently.
    """

    _esm = static_asset("layout/layout_panel.bundle.js")
    _css = static_asset("layout/layout_panel.css")

    layout_kind = t.Unicode("split").tag(sync=True)
    orientation = t.Enum(ORIENTATIONS, default_value="horizontal").tag(sync=True)
    spacing = t.Int(6).tag(sync=True)
    sizes = t.List(t.Float(), default_value=[]).tag(sync=True)

    def __init__(
        self,
        widgets: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        orientation: str = "horizontal",
        spacing: int = 6,
        sizes: Iterable[float] | None = None,
        width: int | float | str | None = "100%",
        height: int | float | str | None = 420,
        resizable: bool = True,
        fit_content: bool = False,
    ) -> None:
        self._init_composed(
            widgets,
            titles,
            keys,
            width,
            height,
            resizable,
            fit_content=fit_content,
            orientation=orientation,
            spacing=spacing,
            sizes=_as_list(sizes),
        )

    def _drop_child_metadata(self, index: int) -> None:
        if index < len(self.sizes):
            self.sizes = [*self.sizes[:index], *self.sizes[index + 1 :]]


class DockPanel(LayoutWidget):
    """Lumino dock panel for tabbed or split workspace-style layouts.

    Parameters
    ----------
    widgets : iterable or mapping, optional
        Child widgets or keyed child mapping. Mapping keys become stable child
        keys and default tab titles.
    titles : iterable or mapping, optional
        Tab titles associated with children.
    keys : iterable of str, optional
        Stable child keys for iterable ``widgets``.
    mode : {"tab-after", "split-right", "split-left", "split-top", "split-bottom"}
        Placement mode used as children are added to the dock layout.
    width : int, float, str, or None
        Widget width.
    height : int, float, str, or None
        Widget height.
    resizable : bool, default True
        Whether the dock panel gets a notebook resize handle.
    """

    _esm = static_asset("layout/layout_panel.bundle.js")
    _css = static_asset("layout/layout_panel.css")

    layout_kind = t.Unicode("dock").tag(sync=True)
    mode = t.Enum(DOCK_MODES, default_value="split-right").tag(sync=True)

    def __init__(
        self,
        widgets: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        mode: str = "split-right",
        width: int | float | str | None = "100%",
        height: int | float | str | None = 520,
        resizable: bool = True,
        fit_content: bool = False,
    ) -> None:
        self._init_composed(widgets, titles, keys, width, height, resizable, fit_content=fit_content, mode=mode)


class AccordionPanel(LayoutWidget):
    """Lumino accordion panel with titled collapsible sections.

    Parameters
    ----------
    widgets : iterable or mapping, optional
        Child widgets or keyed child mapping. Mapping keys become stable child
        keys and default section titles.
    titles : iterable or mapping, optional
        Section titles associated with children.
    keys : iterable of str, optional
        Stable child keys for iterable ``widgets``.
    width : int, float, str, or None
        Widget width.
    height : int, float, str, or None
        Widget height.
    resizable : bool, default True
        Whether the accordion gets a notebook resize handle.
    """

    _esm = static_asset("layout/layout_panel.bundle.js")
    _css = static_asset("layout/layout_panel.css")

    layout_kind = t.Unicode("accordion").tag(sync=True)

    def __init__(
        self,
        widgets: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        width: int | float | str | None = "100%",
        height: int | float | str | None = 420,
        resizable: bool = True,
        fit_content: bool = False,
    ) -> None:
        self._init_composed(widgets, titles, keys, width, height, resizable, fit_content=fit_content)


class StackedPanel(LayoutWidget):
    """Lumino stacked panel that shows one selected child at a time.

    Parameters
    ----------
    widgets : iterable or mapping, optional
        Child widgets or keyed child mapping.
    titles : iterable or mapping, optional
        Optional labels associated with children.
    keys : iterable of str, optional
        Stable child keys for iterable ``widgets``.
    selected_index : int, default 0
        Initially visible child index.
    width : int, float, str, or None
        Widget width.
    height : int, float, str, or None
        Widget height.
    resizable : bool, default True
        Whether the panel gets a notebook resize handle.
    """

    _esm = static_asset("layout/layout_panel.bundle.js")
    _css = static_asset("layout/layout_panel.css")

    layout_kind = t.Unicode("stacked").tag(sync=True)
    selected_index = t.Int(0).tag(sync=True)

    def __init__(
        self,
        widgets: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        selected_index: int = 0,
        width: int | float | str | None = "100%",
        height: int | float | str | None = 420,
        resizable: bool = True,
        fit_content: bool = False,
    ) -> None:
        self._init_composed(
            widgets,
            titles,
            keys,
            width,
            height,
            resizable,
            fit_content=fit_content,
            selected_index=selected_index,
        )

    def select(self, index: int) -> None:
        self.selected_index = index


class GridPanel(LayoutWidget):
    """CSS grid-backed Lumino panel for placing children in grid cells.

    Parameters
    ----------
    widgets : iterable or mapping, optional
        Child widgets or keyed child mapping.
    titles : iterable or mapping, optional
        Optional labels associated with children.
    keys : iterable of str, optional
        Stable child keys for iterable ``widgets``.
    columns : str, default "1fr 1fr"
        CSS ``grid-template-columns`` value.
    rows : str, default "auto"
        CSS ``grid-template-rows`` value.
    gap : int, float, str, or None, default 8
        CSS grid gap. Numeric values use shared anylumino size rules.
    areas : iterable of dict, optional
        Per-child placement metadata. Each item can describe CSS grid
        placement such as row, column, or area values understood by the
        frontend.
    width : int, float, str, or None
        Widget width.
    height : int, float, str, or None
        Widget height.
    resizable : bool, default True
        Whether the grid gets a notebook resize handle.
    """

    _esm = static_asset("layout/layout_panel.bundle.js")
    _css = static_asset("layout/layout_panel.css")

    layout_kind = t.Unicode("grid").tag(sync=True)
    columns = t.Unicode("1fr 1fr").tag(sync=True)
    rows = t.Unicode("auto").tag(sync=True)
    gap = t.Unicode("8px").tag(sync=True)
    areas = t.List(t.Dict(), default_value=[]).tag(sync=True)

    def __init__(
        self,
        widgets: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        columns: str = "1fr 1fr",
        rows: str = "auto",
        gap: int | float | str | None = 8,
        areas: Iterable[dict[str, Any]] | None = None,
        width: int | float | str | None = "100%",
        height: int | float | str | None = 420,
        resizable: bool = True,
        fit_content: bool = False,
    ) -> None:
        self._init_composed(
            widgets,
            titles,
            keys,
            width,
            height,
            resizable,
            fit_content=fit_content,
            columns=columns,
            rows=rows,
            gap=_size_to_css(gap, "8px"),
            areas=_as_list(areas),
        )

    def _drop_child_metadata(self, index: int) -> None:
        if index < len(self.areas):
            self.areas = [*self.areas[:index], *self.areas[index + 1 :]]


class ResponsivePanel(LayoutWidget):
    """Box layout that switches direction when its width crosses a breakpoint.

    Parameters
    ----------
    widgets : iterable or mapping, optional
        Child widgets or keyed child mapping.
    titles : iterable or mapping, optional
        Optional labels associated with children.
    keys : iterable of str, optional
        Stable child keys for iterable ``widgets``.
    breakpoint : int, default 760
        Width in CSS pixels where the layout switches direction.
    wide_direction : str, default "left-to-right"
        Box direction used when the container is wider than ``breakpoint``.
    narrow_direction : str, default "top-to-bottom"
        Box direction used when the container is narrower than ``breakpoint``.
    spacing : int, default 8
        Pixel spacing between children.
    width : int, float, str, or None
        Widget width.
    height : int, float, str, or None
        Widget height.
    resizable : bool, default True
        Whether the panel gets a notebook resize handle.
    """

    _esm = static_asset("layout/layout_panel.bundle.js")
    _css = static_asset("layout/layout_panel.css")

    layout_kind = t.Unicode("responsive").tag(sync=True)
    breakpoint = t.Int(760).tag(sync=True)
    wide_direction = t.Enum(BOX_DIRECTIONS, default_value="left-to-right").tag(sync=True)
    narrow_direction = t.Enum(BOX_DIRECTIONS, default_value="top-to-bottom").tag(sync=True)
    spacing = t.Int(8).tag(sync=True)

    def __init__(
        self,
        widgets: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        breakpoint: int = 760,
        wide_direction: str = "left-to-right",
        narrow_direction: str = "top-to-bottom",
        spacing: int = 8,
        width: int | float | str | None = "100%",
        height: int | float | str | None = 420,
        resizable: bool = True,
        fit_content: bool = False,
    ) -> None:
        self._init_composed(
            widgets,
            titles,
            keys,
            width,
            height,
            resizable,
            fit_content=fit_content,
            breakpoint=breakpoint,
            wide_direction=wide_direction,
            narrow_direction=narrow_direction,
            spacing=spacing,
        )


class _ActionWidget(ActivationCallbacks, anywidget.AnyWidget):
    _esm = static_asset("layout/action_panel.bundle.js")
    _css = static_asset("layout/action_panel.css")

    action_kind = t.Enum(ACTION_KINDS).tag(sync=True)
    actions = t.List(t.Dict(), default_value=[]).tag(sync=True)
    width = t.Unicode("100%").tag(sync=True)
    height = t.Unicode("auto").tag(sync=True)

    def __init__(
        self,
        actions: Iterable[dict[str, Any]] | None = None,
        *,
        callbacks: dict[str, ActionCallback] | None = None,
        width: int | float | str | None = "100%",
        height: int | float | str | None = "auto",
        **kwargs: Any,
    ) -> None:
        self._init_callbacks()
        self.callbacks = dict(callbacks or {})
        super().__init__(
            actions=_as_list(actions),
            width=_size_to_css(width, "100%"),
            height=_size_to_css(height, "auto"),
            **kwargs,
        )
        self.on_msg(self._handle_frontend_event)

    def _handle_frontend_event(self, _widget: object, content: dict[str, Any], _buffers: object) -> None:
        if content.get("type") != "activate":
            return
        action_id = content.get("id")
        if not isinstance(action_id, str):
            return
        callback = self.callbacks.get(action_id)
        if callback is not None:
            callback(action_id)
        self._notify_action(action_id)
        self._notify_click()


class Toolbar(_ActionWidget):
    """Toolbar of clickable actions that can invoke Python callbacks.

    Parameters
    ----------
    actions : iterable of dict, optional
        Action definitions. Each action should include an ``id`` and ``label``;
        optional keys such as ``icon``, ``icon_src``, ``icon_size``,
        ``tooltip``, ``disabled``, or ``separator`` are forwarded to the
        frontend. ``icon`` uses bundled workflow icon names.
    callbacks : dict[str, callable], optional
        Callback map keyed by action id. A callback receives the activated
        action id. The map stays available as the ``callbacks`` attribute, and
        ``on_click`` or ``on_action`` register callbacks for every activation.
    width : int, float, str, or None
        Widget width.
    height : int, float, str, or None
        Widget height.
    """

    def __init__(
        self,
        actions: Iterable[dict[str, Any]] | None = None,
        *,
        callbacks: dict[str, ActionCallback] | None = None,
        width: int | float | str | None = "100%",
        height: int | float | str | None = "auto",
    ) -> None:
        super().__init__(actions, callbacks=callbacks, width=width, height=height, action_kind="toolbar")


class MenuBar(_ActionWidget):
    """Lumino-style menu bar with nested menu items and Python callbacks.

    Parameters
    ----------
    menus : iterable of dict, optional
        Menu definitions. A menu normally has a ``label`` and an ``items``
        sequence. Item dictionaries should include an ``id`` and ``label`` and
        may include frontend options such as ``icon``, ``icon_src``,
        ``icon_size``, ``disabled``, or ``separator``. ``icon`` uses bundled
        workflow icon names.
    callbacks : dict[str, callable], optional
        Callback map keyed by menu item id. A callback receives the activated
        item id. The map stays available as the ``callbacks`` attribute, and
        ``on_click`` or ``on_action`` register callbacks for every activation.
    width : int, float, str, or None
        Widget width.
    height : int, float, str, or None
        Widget height.
    """

    def __init__(
        self,
        menus: Iterable[dict[str, Any]] | None = None,
        *,
        callbacks: dict[str, ActionCallback] | None = None,
        width: int | float | str | None = "100%",
        height: int | float | str | None = "auto",
    ) -> None:
        super().__init__(menus, callbacks=callbacks, width=width, height=height, action_kind="menubar")


class CommandPalette(_ActionWidget):
    """Command palette for searchable actions grouped by category.

    Parameters
    ----------
    commands : iterable of dict, optional
        Command definitions. Each command should include an ``id`` and
        ``label``; optional keys such as ``category``, ``caption``, ``icon``,
        ``icon_src``, ``icon_size``, or ``disabled`` are forwarded to the
        frontend. ``icon`` uses bundled workflow icon names.
    callbacks : dict[str, callable], optional
        Callback map keyed by command id. A callback receives the activated
        command id. The map stays available as the ``callbacks`` attribute, and
        ``on_click`` or ``on_action`` register callbacks for every activation.
    width : int, float, str, or None
        Widget width.
    height : int, float, str, or None
        Widget height.
    """

    def __init__(
        self,
        commands: Iterable[dict[str, Any]] | None = None,
        *,
        callbacks: dict[str, ActionCallback] | None = None,
        width: int | float | str | None = "100%",
        height: int | float | str | None = 320,
    ) -> None:
        super().__init__(
            commands,
            callbacks=callbacks,
            width=width,
            height=height,
            action_kind="command_palette",
        )


class TextWidget(anywidget.AnyWidget):
    """Small synced value display widget used in examples and tests.

    Parameters
    ----------
    value : str, default ""
        Initial value displayed by the widget.
    """

    _esm = static_asset("layout/text_widget.js")
    _css = static_asset("layout/text_widget.css")

    value = t.Unicode("").tag(sync=True)

    def __init__(self, value: str = "") -> None:
        super().__init__(value=value)
