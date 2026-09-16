"""Astryx layout panels that mirror the Lumino layout widgets."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import traitlets as t

from ..layout import ChildInput
from ..layout import TitleInput
from .base import Widget
from .base import _named_props

SPLIT_ORIENTATIONS = ("horizontal", "vertical")
STACK_DIRECTIONS = ("horizontal", "vertical")
SCROLL_AXES = ("block", "inline", "both")


class TabPanel(Widget):
    """Astryx tab list with one child panel shown per tab.

    Children can be passed as a list or as a keyed mapping. Mapping keys become
    stable child keys and default tab titles. Use ``select_key`` or
    ``selected_index`` to choose the active tab. A child panel mounts the first
    time its tab is selected and stays mounted, hidden, afterwards.

    Parameters
    ----------
    children : ChildInput
        Child widgets or owner objects exposing a ``widget`` attribute. Mapping
        keys become stable child keys.
    titles : TitleInput, default None
        Tab titles associated with children. Defaults to the child keys.
    keys : Iterable[str] | None, default None
        Stable child keys for iterable ``children``.
    selected_index : int, default 0
        Initially selected tab index.
    size : str | None, default None
        Tab size, ``"sm"``, ``"md"``, or ``"lg"``.
    layout : str | None, default None
        ``"hug"`` or ``"fill"`` tab layout.
    divider : bool | None, default None
        Whether to show the tab-list divider.
    gap : int | float, default 2
        Astryx spacing step between the tab list and the panel.
    width : int | float | str | None, default None
        Panel width.
    height : int | float | str | None, default None
        Panel height.
    **props : Any
        JSON-safe TabList props forwarded to Astryx.
    """

    _title_prefix = "Tab"

    selected_index = t.Int(0).tag(sync=True)

    def __init__(
        self,
        children: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        selected_index: int = 0,
        size: str | None = None,
        layout: str | None = None,
        divider: bool | None = None,
        gap: int | float = 2,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "TabPanel",
            children,
            titles=titles,
            keys=keys,
            selected_index=selected_index,
            width=width,
            height=height,
            props=_named_props(
                props,
                size=size,
                layout=layout,
                hasDivider=divider,
                gap=gap,
            ),
        )

    def select(self, index: int) -> None:
        """Select the tab at ``index``."""
        self.selected_index = index

    def add_tab(
        self,
        widget: object,
        title: str | None = None,
        *,
        key: str | None = None,
        select: bool = False,
    ) -> None:
        """Append a child as a new tab."""
        self.add_widget(widget, title=title, key=key, select=select)


class StackedPanel(Widget):
    """Astryx panel that shows one selected child at a time.

    A child mounts the first time it is selected and stays mounted, hidden,
    afterwards, so switching back keeps its state.

    Parameters
    ----------
    children : ChildInput
        Child widgets or keyed child mapping.
    titles : TitleInput, default None
        Optional labels associated with children.
    keys : Iterable[str] | None, default None
        Stable child keys for iterable ``children``.
    selected_index : int, default 0
        Initially visible child index.
    width : int | float | str | None, default None
        Panel width.
    height : int | float | str | None, default None
        Panel height.
    **props : Any
        JSON-safe props forwarded to the panel root.
    """

    _title_prefix = "Panel"

    selected_index = t.Int(0).tag(sync=True)

    def __init__(
        self,
        children: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        selected_index: int = 0,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "StackedPanel",
            children,
            titles=titles,
            keys=keys,
            selected_index=selected_index,
            width=width,
            height=height,
            props=_named_props(props),
        )

    def select(self, index: int) -> None:
        """Show the child at ``index``."""
        self.selected_index = index


class AccordionPanel(Widget):
    """Astryx collapsible group with one titled section per child.

    The open sections live in ``value``: a child key when ``multiple`` is
    ``False`` and a list of child keys otherwise.

    Parameters
    ----------
    children : ChildInput
        Child widgets or keyed child mapping.
    titles : TitleInput, default None
        Section titles associated with children. Defaults to the child keys.
    keys : Iterable[str] | None, default None
        Stable child keys for iterable ``children``.
    open : str | int | Iterable[str | int] | None, default None
        Initially open section keys or indexes. Defaults to the first child
        when ``multiple`` is ``False`` and to no section otherwise.
    multiple : bool, default False
        Whether several sections can be open at once.
    dividers : bool, default True
        Whether to draw hairline dividers between sections.
    width : int | float | str | None, default None
        Panel width.
    height : int | float | str | None, default None
        Panel height.
    **props : Any
        JSON-safe CollapsibleGroup props forwarded to Astryx.
    """

    _title_prefix = "Section"

    def __init__(
        self,
        children: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        open: str | int | Iterable[str | int] | None = None,
        multiple: bool = False,
        dividers: bool = True,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "AccordionPanel",
            children,
            titles=titles,
            keys=keys,
            width=width,
            height=height,
            props=_named_props(
                props,
                type="multiple" if multiple else "single",
                hasDividers=dividers,
            ),
        )
        self.value = self._open_value(open, multiple)

    @property
    def open_keys(self) -> list[str]:
        """Keys of the open sections."""
        if isinstance(self.value, str):
            return [self.value] if self.value else []
        return [str(key) for key in self.value or []]

    def open_key(self, key_or_index: str | int) -> None:
        """Open the section for ``key_or_index``."""
        key = self.get_key(self.get_index(key_or_index) if isinstance(key_or_index, str) else key_or_index)
        if self.props.get("type") == "multiple":
            self.value = [*[open for open in self.open_keys if open != key], key]
        else:
            self.value = key

    def close_key(self, key_or_index: str | int) -> None:
        """Close the section for ``key_or_index``."""
        key = self.get_key(self.get_index(key_or_index) if isinstance(key_or_index, str) else key_or_index)
        remaining = [open for open in self.open_keys if open != key]
        self.value = remaining if self.props.get("type") == "multiple" else (remaining[0] if remaining else "")

    def _open_value(self, open: str | int | Iterable[str | int] | None, multiple: bool) -> str | list[str]:
        if open is None:
            if multiple:
                return []
            return self.child_keys[0] if self.child_keys else ""
        requested = [open] if isinstance(open, (str, int)) else list(open)
        keys = [self.get_key(self.get_index(item) if isinstance(item, str) else item) for item in requested]
        if multiple:
            return keys
        if len(keys) != 1:
            msg = "open must name a single section unless multiple=True"
            raise ValueError(msg)
        return keys[0]


class ScrollBox(Widget):
    """Astryx scrollable area holding a vertical stack of children.

    Parameters
    ----------
    children : ChildInput
        Child widgets or keyed child mapping.
    titles : TitleInput, default None
        Optional labels associated with children.
    keys : Iterable[str] | None, default None
        Stable child keys for iterable ``children``.
    axis : str, default 'block'
        Scroll axis, ``"block"``, ``"inline"``, or ``"both"``.
    label : str, default 'Scrollable content'
        Accessible name of the scroll viewport.
    gap : int | float, default 2
        Astryx spacing step between children.
    padding : int | float | None, default None
        Content padding using the Astryx spacing scale.
    width : int | float | str | None, default None
        Viewport width.
    height : int | float | str | None, default 320
        Viewport height.
    max_width : int | float | str | None, default None
        Maximum viewport width.
    min_height : int | float | str | None, default None
        Minimum viewport height.
    **props : Any
        JSON-safe ScrollableArea props forwarded to Astryx.
    """

    _title_prefix = "Widget"

    def __init__(
        self,
        children: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        axis: str = "block",
        label: str = "Scrollable content",
        gap: int | float = 2,
        padding: int | float | None = None,
        width: int | float | str | None = None,
        height: int | float | str | None = 320,
        max_width: int | float | str | None = None,
        min_height: int | float | str | None = None,
        **props: Any,
    ) -> None:
        if axis not in SCROLL_AXES:
            msg = f"axis must be one of {SCROLL_AXES}, got {axis!r}"
            raise ValueError(msg)
        super().__init__(
            "ScrollBox",
            children,
            titles=titles,
            keys=keys,
            label=label,
            width=width,
            height=height,
            props=_named_props(
                props,
                axis=axis,
                gap=gap,
                padding=padding,
                width=width,
                height=height,
                maxWidth=max_width,
                minHeight=min_height,
            ),
        )


class SplitPanel(Widget):
    """Astryx panes separated by draggable resize handles.

    ``sizes`` holds the relative pane sizes as fractions of the panel. Drags
    sync the fractions back to Python, and assigning ``sizes`` resizes the
    panes.

    Parameters
    ----------
    children : ChildInput
        Child widgets or keyed child mapping.
    titles : TitleInput, default None
        Optional labels associated with children.
    keys : Iterable[str] | None, default None
        Stable child keys for iterable ``children``.
    orientation : str, default 'horizontal'
        Split direction. Horizontal places panes side by side; vertical stacks
        them.
    sizes : Iterable[float] | None, default None
        Relative pane sizes. Equal sizes are used when omitted.
    min_size : int, default 80
        Minimum pane size in pixels.
    width : int | float | str | None, default '100%'
        Panel width.
    height : int | float | str | None, default 420
        Panel height.
    **props : Any
        JSON-safe ResizeHandle props forwarded to Astryx.
    """

    _title_prefix = "Pane"

    sizes = t.List(t.Float(), default_value=[]).tag(sync=True)

    def __init__(
        self,
        children: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        orientation: str = "horizontal",
        sizes: Iterable[float] | None = None,
        min_size: int = 80,
        width: int | float | str | None = "100%",
        height: int | float | str | None = 420,
        **props: Any,
    ) -> None:
        if orientation not in SPLIT_ORIENTATIONS:
            msg = f"orientation must be one of {SPLIT_ORIENTATIONS}, got {orientation!r}"
            raise ValueError(msg)
        super().__init__(
            "SplitPanel",
            children,
            titles=titles,
            keys=keys,
            sizes=list(sizes or []),
            width=width,
            height=height,
            props=_named_props(props, orientation=orientation, minSize=min_size),
        )

    def _drop_child_metadata(self, index: int) -> None:
        if index < len(self.sizes):
            self.sizes = [*self.sizes[:index], *self.sizes[index + 1 :]]


class ResponsivePanel(Widget):
    """Astryx stack that switches direction when its width crosses a breakpoint.

    Parameters
    ----------
    children : ChildInput
        Child widgets or keyed child mapping.
    titles : TitleInput, default None
        Optional labels associated with children.
    keys : Iterable[str] | None, default None
        Stable child keys for iterable ``children``.
    breakpoint : int, default 760
        Width in CSS pixels where the layout switches direction.
    wide_direction : str, default 'horizontal'
        Stack direction at or above the breakpoint.
    narrow_direction : str, default 'vertical'
        Stack direction below the breakpoint.
    gap : int | float, default 2
        Astryx spacing step between children.
    width : int | float | str | None, default None
        Panel width.
    height : int | float | str | None, default None
        Panel height.
    **props : Any
        JSON-safe Stack props forwarded to Astryx.
    """

    _title_prefix = "Widget"

    def __init__(
        self,
        children: ChildInput = None,
        *,
        titles: TitleInput = None,
        keys: Iterable[str] | None = None,
        breakpoint: int = 760,
        wide_direction: str = "horizontal",
        narrow_direction: str = "vertical",
        gap: int | float = 2,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        **props: Any,
    ) -> None:
        for name, direction in (("wide_direction", wide_direction), ("narrow_direction", narrow_direction)):
            if direction not in STACK_DIRECTIONS:
                msg = f"{name} must be one of {STACK_DIRECTIONS}, got {direction!r}"
                raise ValueError(msg)
        super().__init__(
            "ResponsivePanel",
            children,
            titles=titles,
            keys=keys,
            width=width,
            height=height,
            props=_named_props(
                props,
                breakpoint=breakpoint,
                wideDirection=wide_direction,
                narrowDirection=narrow_direction,
                gap=gap,
            ),
        )


__all__ = [
    "AccordionPanel",
    "ResponsivePanel",
    "ScrollBox",
    "SplitPanel",
    "StackedPanel",
    "TabPanel",
]
