"""Astryx layout, surface, and composite widgets."""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any

from ..components import ComponentWidget
from ..layout import ChildInput
from .base import Widget
from .base import _clean_value
from .base import _named_props
from .base import _option_records
from .base import _search_records


class Stack(Widget):
    """Arrange child widgets in an Astryx stack.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    direction : str, default 'vertical'
        Layout direction.
    gap : int | float, default 2
        Astryx spacing step between children.
    align : str | None, default None
        Cross-axis alignment.
    justify : str | None, default None
        Main-axis alignment.
    width : int | float | str | None, default None
        Container width.
    height : int | float | str | None, default None
        Container height.
    padding : int | float | None, default None
        Inner padding using the Astryx spacing scale.
    wrap : str | None, default None
        Stack wrapping behavior.
    scrollable : bool | None, default None
        Whether overflow should scroll.
    **props : Any
        JSON-safe Stack props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Stack props forwarded to Astryx.

    Supported Astryx props include:

    - ``direction`` ('horizontal' or 'vertical'; default 'vertical'): Direction of the stack layout.
    - ``hAlign`` (StackAlignment): Horizontal alignment. With horizontal direction it controls the
      main axis; with vertical direction it controls the cross axis.
    - ``vAlign`` (StackAlignment): Vertical alignment. With horizontal direction it controls the
      cross axis; with vertical direction it controls the main axis.
    - ``justify`` (StackMainAlignment): Main-axis alignment alias resolved from direction, mirroring
      CSS justify-content.
    - ``align`` (StackCrossAlignment): Cross-axis alignment alias resolved from direction, mirroring
      CSS align-items.
    - ``width`` (number or string): Container width. Numbers are pixels; strings are used as CSS
      values.
    - ``height`` (number or string): Container height. Numbers are pixels; strings are used as CSS
      values.
    - ``gap`` (spacing step): Spacing between items. Accepts Astryx spacing steps such as 0, 0.5, 1,
      2, 3, 4, 6, 8, and 10.
    - ``padding`` (spacing step): Inner padding on all sides using the spacing scale.
    - ``paddingInline`` (spacing step): Horizontal padding override; takes precedence over padding
      on the inline axis.
    - ``paddingBlock`` (spacing step): Vertical padding override; takes precedence over padding on
      the block axis.
    - ``isScrollable`` (boolean; default false): Enables scrollable overflow on the stack container.
    - ``wrap`` ('nowrap' or 'wrap' or 'wrap-reverse'; default 'nowrap'): Controls whether items wrap
      onto additional lines.
    - ``as`` (ElementType; default div): Element type to render for the root element.
    - ``xstyle`` (StyleXStyles): StyleX styles created with stylex.create().
    - ``className`` (string): CSS class names appended to the root element.
    - ``style`` (CSSProperties): Inline styles applied after StyleX styles.
    - ``children`` (ReactNode): Content rendered inside the stack.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Stack>.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        direction: str = "vertical",
        gap: int | float = 2,
        align: str | None = None,
        justify: str | None = None,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        padding: int | float | None = None,
        wrap: str | None = None,
        scrollable: bool | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Stack",
            children,
            width=width,
            height=height,
            props=_named_props(
                props,
                direction=direction,
                gap=gap,
                align=align,
                justify=justify,
                width=width,
                height=height,
                padding=padding,
                wrap=wrap,
                isScrollable=scrollable,
            ),
        )


class Grid(Widget):
    """Arrange child widgets in an Astryx grid.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    columns : int | Mapping[str, Any], default 2
        Grid or table column definition.
    gap : int | float, default 3
        Astryx spacing step between children.
    row_gap : int | float | None, default None
        Row spacing override.
    column_gap : int | float | None, default None
        Column spacing override.
    align : str | None, default None
        Vertical item alignment.
    justify : str | None, default None
        Horizontal item alignment.
    width : int | float | str | None, default None
        Grid width.
    height : int | float | str | None, default None
        Grid height.
    **props : Any
        JSON-safe Grid props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Grid props forwarded to Astryx.

    Supported Astryx props include:

    - ``columns`` (number or {minWidth: number, max?: number, repeat?: 'fill' or 'fit'}): Column
      configuration. Use a number for fixed columns (e.g. 'columns={3}'). Use an object for
      responsive columns: 'minWidth' sets the minimum column width in px, 'repeat' controls
      track behavior ('"fill"' preserves empty tracks for consistent widths, '"fit"' collapses
      empty tracks so items stretch; defaults to '"fill"'), and 'max' caps the maximum number of
      columns.
    - ``minChildWidth`` (number): Deprecated: use 'columns={{minWidth: 280}}' instead. Minimum item
      width in px; enables responsive auto-fit.
    - ``width`` (number or string): Container width.
    - ``height`` (number or string): Container height.
    - ``gap`` (SpacingStep): Spacing between all items.
    - ``rowGap`` (SpacingStep): Row spacing; overrides 'gap' for the row axis.
    - ``columnGap`` (SpacingStep): Column spacing; overrides 'gap' for the column axis.
    - ``align`` (GridAlignment): Vertical alignment of items.
    - ``justify`` (GridAlignment): Horizontal alignment of items.
    - ``children`` (ReactNode): Grid content.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Grid>.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        columns: int | Mapping[str, Any] = 2,
        gap: int | float = 3,
        row_gap: int | float | None = None,
        column_gap: int | float | None = None,
        align: str | None = None,
        justify: str | None = None,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Grid",
            children,
            width=width,
            height=height,
            props=_named_props(
                props,
                columns=_clean_value(columns),
                gap=gap,
                rowGap=row_gap,
                columnGap=column_gap,
                align=align,
                justify=justify,
                width=width,
                height=height,
            ),
        )


class Center(Widget):
    """Center child content in an Astryx container.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    axis : str, default 'both'
        Axis used for centering child content.
    width : int | float | str | None, default None
        Container width.
    height : int | float | str | None, default None
        Container height.
    inline : bool | None, default None
        Whether to use inline-flex layout.
    **props : Any
        JSON-safe Center props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Center props forwarded to Astryx.

    Supported Astryx props include:

    - ``axis`` ('both' or 'horizontal' or 'vertical'): Which direction(s) to center.
    - ``width`` (number or string): Container width (px or CSS value).
    - ``height`` (number or string): Container height (px or CSS value).
    - ``isInline`` (boolean): Use inline-flex (useful for text/icons).
    - ``children`` (ReactNode): Content to center.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Center>.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        axis: str = "both",
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        inline: bool | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Center",
            children,
            width=width,
            height=height,
            props=_named_props(
                props, axis=axis, width=width, height=height, isInline=inline
            ),
        )


class AspectRatio(Widget):
    """Constrain child content to a fixed aspect ratio.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    ratio : int | float, default '16 / 9'
        Aspect ratio as a numeric width divided by height value.
    **props : Any
        JSON-safe AspectRatio props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe AspectRatio props forwarded to Astryx.

    Supported Astryx props include:

    - ``ratio`` (number; required): Aspect ratio as width/height (e.g. 16/9, 1).
    - ``children`` (ReactNode; required): Content positioned absolutely to fill the container.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/AspectRatio>.
    """

    def __init__(
        self, children: ChildInput = None, *, ratio: int | float = 16 / 9, **props: Any
    ) -> None:
        super().__init__("AspectRatio", children, props={"ratio": ratio, **props})


class Card(Widget):
    """Render an Astryx card container.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    variant : str, default 'default'
        Astryx visual variant.
    padding : int | float | None, default None
        Inner padding using the Astryx spacing scale.
    width : int | float | str | None, default None
        Card width.
    height : int | float | str | None, default None
        Card height.
    max_width : int | float | str | None, default None
        Maximum card width.
    min_height : int | float | str | None, default None
        Minimum card height.
    **props : Any
        JSON-safe Card props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Card props forwarded to Astryx.

    Supported Astryx props include:

    - ``width`` (SizeValue): Width of the card (number = pixels, string = used as-is).
    - ``height`` (SizeValue): Height of the card (number = pixels, string = used as-is).
    - ``maxWidth`` (SizeValue): Maximum width of the card.
    - ``minHeight`` (SizeValue): Minimum height of the card.
    - ``children`` (ReactNode): Content to render inside the card.
    - ``padding`` (0 or 0.5 or 1 or 1.5 or 2 or 3 or 4 or 5 or 6 or 8 or 10): Internal padding using
      the spacing scale.
    - ``variant`` ('default' or 'muted' or 'blue' or 'cyan' or 'gray' or 'green' or 'orange' or
      'pink' or 'purple' or 'red' or 'teal' or 'yellow'): Background color variant. 'default'
      uses the standard card background. 'muted' uses the muted background for de-emphasised
      cards. The non-semantic variants use the corresponding '--color-<name>-background' token.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Card>.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        variant: str = "default",
        padding: int | float | None = None,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        max_width: int | float | str | None = None,
        min_height: int | float | str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Card",
            children,
            variant=variant,
            width=width,
            height=height,
            props=_named_props(
                props,
                variant=variant,
                padding=padding,
                width=width,
                height=height,
                maxWidth=max_width,
                minHeight=min_height,
            ),
        )


class ClickableCard(Widget):
    """Render an Astryx card that behaves like an action target.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    label : str
        Visible or accessible label for the component.
    variant : str, default 'default'
        Astryx visual variant.
    disabled : bool, default False
        Whether the card is disabled.
    href : str | None, default None
        Optional navigation target.
    target : str | None, default None
        Link target when ``href`` is supplied.
    padding : int | float | None, default None
        Inner padding using the Astryx spacing scale.
    width : int | float | str | None, default None
        Card width.
    height : int | float | str | None, default None
        Card height.
    max_width : int | float | str | None, default None
        Maximum card width.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked for frontend activations.
    **props : Any
        JSON-safe ClickableCard props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe ClickableCard props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessibility label.
    - ``onClick`` ((event: MouseEvent) => void): Click handler: fires on card surface only.
    - ``href`` (string): Navigation URL.
    - ``target`` (string): Link target.
    - ``isDisabled`` (boolean): Disables the card.
    - ``children`` (ReactNode): Card content.
    - ``padding`` (SpacingStep): Inner padding.
    - ``variant`` ('default' or 'transparent' or 'muted' or 'blue' or 'cyan' or 'gray' or 'green' or
      'orange' or 'pink' or 'purple' or 'red' or 'teal' or 'yellow'): Background color variant.
    - ``width`` (SizeValue): Card width.
    - ``height`` (SizeValue): Card height.
    - ``maxWidth`` (SizeValue): Maximum card width.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/ClickableCard>.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        label: str,
        variant: str = "default",
        disabled: bool = False,
        href: str | None = None,
        target: str | None = None,
        padding: int | float | None = None,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        max_width: int | float | str | None = None,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "ClickableCard",
            children,
            label=label,
            variant=variant,
            disabled=disabled,
            callbacks=callbacks,
            width=width,
            height=height,
            props=_named_props(
                props,
                variant=variant,
                href=href,
                target=target,
                padding=padding,
                width=width,
                height=height,
                maxWidth=max_width,
            ),
        )


class SelectableCard(Widget):
    """Render an Astryx card with a selected state.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    value : bool, default False
        Synchronized component value.
    label : str
        Visible or accessible label for the component.
    variant : str, default 'default'
        Astryx visual variant.
    disabled : bool, default False
        Whether the card is disabled.
    padding : int | float | None, default None
        Inner padding using the Astryx spacing scale.
    width : int | float | str | None, default None
        Card width.
    height : int | float | str | None, default None
        Card height.
    max_width : int | float | str | None, default None
        Maximum card width.
    **props : Any
        JSON-safe SelectableCard props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe SelectableCard props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessibility label.
    - ``isSelected`` (boolean; required): Controlled selection state.
    - ``onChange`` ((isSelected: boolean) => void; required): Called when toggled.
    - ``isDisabled`` (boolean): Disables the card.
    - ``children`` (ReactNode): Card content.
    - ``padding`` (SpacingStep): Inner padding.
    - ``variant`` ('default' or 'transparent' or 'muted' or 'blue' or 'cyan' or 'gray' or 'green' or
      'orange' or 'pink' or 'purple' or 'red' or 'teal' or 'yellow'): Background color variant.
    - ``width`` (SizeValue): Card width.
    - ``height`` (SizeValue): Card height.
    - ``maxWidth`` (SizeValue): Maximum card width.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/SelectableCard>.
    """

    def __init__(
        self,
        children: ChildInput = None,
        value: bool = False,
        *,
        label: str,
        variant: str = "default",
        disabled: bool = False,
        padding: int | float | None = None,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        max_width: int | float | str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "SelectableCard",
            children,
            label=label,
            value=value,
            variant=variant,
            disabled=disabled,
            width=width,
            height=height,
            props=_named_props(
                props,
                variant=variant,
                padding=padding,
                width=width,
                height=height,
                maxWidth=max_width,
            ),
        )


class Section(Widget):
    """Render an Astryx section container.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    variant : str, default 'section'
        Astryx visual variant.
    padding : int | float | None, default None
        Inner padding using the Astryx spacing scale.
    padding_block : int | float | None, default None
        Block-axis padding override.
    dividers : Iterable[str] | None, default None
        Section sides that display divider borders.
    width : int | float | str | None, default None
        Section width.
    height : int | float | str | None, default None
        Section height.
    max_width : int | float | str | None, default None
        Maximum section width.
    **props : Any
        JSON-safe Section props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Section props forwarded to Astryx.

    Supported Astryx props include:

    - ``variant`` ('section' or 'transparent' or 'muted'): Background variant applied to the section
      container.
    - ``width`` (SizeValue): Width of the section; a number is interpreted as pixels, a string is
      used as-is.
    - ``height`` (SizeValue): Height of the section; a number is interpreted as pixels, a string is
      used as-is.
    - ``maxWidth`` (SizeValue): Maximum width of the section.
    - ``minHeight`` (SizeValue): Minimum height of the section.
    - ``children`` (ReactNode): Content rendered inside the section.
    - ``dividers`` (Array<'top' or 'bottom' or 'start' or 'end'>): Which sides of the section have
      divider borders.
    - ``padding`` (SpacingStep): Internal padding using the spacing scale (0, 0.5, 1, 1.5, 2, 3, 4,
      5, 6, 8, 10). Use padding={0} for edge-to-edge content.
    - ``paddingBlock`` (SpacingStep): Block (vertical) padding override. Overrides only the
      block-axis padding while preserving inline padding from 'padding' or the container theme
      default. Accepts the spacing scale (0, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10).
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Section>.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        variant: str = "section",
        padding: int | float | None = None,
        padding_block: int | float | None = None,
        dividers: Iterable[str] | None = None,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        max_width: int | float | str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Section",
            children,
            variant=variant,
            width=width,
            height=height,
            props=_named_props(
                props,
                variant=variant,
                padding=padding,
                paddingBlock=padding_block,
                dividers=list(dividers) if dividers is not None else None,
                width=width,
                height=height,
                maxWidth=max_width,
            ),
        )


class Divider(Widget):
    """Render an Astryx divider.

    Parameters
    ----------
    orientation : str, default 'horizontal'
        Astryx component option.
    variant : str, default 'subtle'
        Astryx visual variant.
    label : str | None, default None
        Optional text centered on the divider.
    full_bleed : bool | None, default None
        Whether the divider extends to the container edges.
    **props : Any
        JSON-safe Divider props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Divider props forwarded to Astryx.

    Supported Astryx props include:

    - ``orientation`` ('horizontal' or 'vertical'): Orientation of the divider.
    - ``label`` (ReactNode): Optional label centered on the divider.
    - ``variant`` ('subtle' or 'strong'): Visual weight of the divider line.
    - ``isFullBleed`` (boolean): Extend the divider to container edges with negative margins.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Divider>.
    """

    def __init__(
        self,
        *,
        orientation: str = "horizontal",
        variant: str = "subtle",
        label: str | None = None,
        full_bleed: bool | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Divider",
            variant=variant,
            props=_named_props(
                props,
                orientation=orientation,
                variant=variant,
                label=label,
                isFullBleed=full_bleed,
            ),
        )


class List(Widget):
    """Render an Astryx list from item records.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    header : str, default ''
        Optional header text or content.
    density : str | None, default None
        Item spacing density.
    dividers : bool | None, default None
        Whether to show dividers between items.
    list_style : str | None, default None
        List marker style.
    start : int | None, default None
        Starting number for ordered lists.
    **props : Any
        JSON-safe List props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe List props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode): List items (ListItem components).
    - ``density`` ('compact' or 'balanced' or 'spacious'): Spacing density for items.
    - ``hasDividers`` (boolean): Show dividers between items.
    - ``header`` (ReactNode): Header content, associated with the list via aria-labelledby.
    - ``listStyle`` ('none' or 'disc' or 'decimal' or 'circle'): List marker style. 'decimal'
      renders an <ol> element instead of <ul>.
    - ``start`` (number): Starting number for ordered lists (listStyle='decimal'). Sets the CSS
      counter to begin at this value.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/List>.
    """

    def __init__(
        self,
        items: Iterable[Any],
        *,
        header: str = "",
        density: str | None = None,
        dividers: bool | None = None,
        list_style: str | None = None,
        start: int | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "List",
            props=_named_props(
                props,
                items=_option_records(items),
                header=header or None,
                density=density,
                hasDividers=dividers,
                listStyle=list_style,
                start=start,
            ),
        )


class MetadataList(Widget):
    """Render label-value metadata rows.

    Parameters
    ----------
    items : Iterable[Mapping[str, Any]]
        Item records used by generated child components or static search sources.
    columns : str | int | None, default None
        Single, multi, or fixed-count column layout.
    label : Mapping[str, Any] | None, default None
        Label position and width configuration.
    max_items : int | None, default None
        Maximum visible items before the expansion control.
    orientation : str | None, default None
        Vertical or horizontal layout.
    title : str | None, default None
        Optional title above the metadata.
    **props : Any
        JSON-safe MetadataList props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe MetadataList props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): Metadata items (MetadataListItem components).
    - ``columns`` ('multi' or 'single' or number): Column layout mode.
    - ``label`` ({ position?: 'start' or 'top', width?: number or string }): Label display
      configuration. position controls label placement, width sets a custom label column width.
      Defaults to { position: 'top' } for multi-column layouts.
    - ``maxNumOfItems`` (number): Maximum items to show before collapsing with a show more/less
      toggle.
    - ``orientation`` ('vertical' or 'horizontal'): Layout orientation. Horizontal mode flows items
      in a row with flex-wrap.
    - ``title`` (ReactNode): Optional title or heading above the list.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization. Must be a stylex.create()
      value.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/MetadataList>.
    """

    def __init__(
        self,
        items: Iterable[Mapping[str, Any]],
        *,
        columns: str | int | None = None,
        label: Mapping[str, Any] | None = None,
        max_items: int | None = None,
        orientation: str | None = None,
        title: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "MetadataList",
            props=_named_props(
                props,
                items=_clean_value(list(items)),
                columns=columns,
                label=label,
                maxNumOfItems=max_items,
                orientation=orientation,
                title=title,
            ),
        )


class Breadcrumbs(Widget):
    """Render Astryx breadcrumbs from item records.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    separator : str | None, default None
        Separator text between breadcrumb items.
    variant : str | None, default None
        Default or supporting visual treatment.
    label : str | None, default None
        Accessible navigation label.
    **props : Any
        JSON-safe Breadcrumbs props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Breadcrumbs props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): BreadcrumbItem elements to render inside the breadcrumb
      trail.
    - ``separator`` (ReactNode): Separator rendered between breadcrumb items.
    - ``variant`` ('default' or 'supporting'): Visual variant: supporting is smaller with secondary
      text styling.
    - ``label`` (string): Accessible label for the nav landmark (aria-label).
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Breadcrumbs>.
    """

    def __init__(
        self,
        items: Iterable[Any],
        *,
        separator: str | None = None,
        variant: str | None = None,
        label: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Breadcrumbs",
            props=_named_props(
                props,
                items=_option_records(items),
                separator=separator,
                variant=variant,
                label=label,
            ),
        )


class TabList(Widget):
    """Render an Astryx tab list.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    value : str
        Synchronized component value.
    size : str | None, default None
        Tab size.
    layout : str | None, default None
        Hug or fill tab layout.
    divider : bool | None, default None
        Whether to show the tab-list divider.
    orientation : str | None, default None
        Horizontal or vertical tab orientation.
    **props : Any
        JSON-safe TabList props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe TabList props forwarded to Astryx.

    Supported Astryx props include:

    - ``value`` (string; required): The currently selected tab value.
    - ``onChange`` ((value: string) => void; required): Callback fired when a tab is selected.
    - ``size`` ('sm' or 'md' or 'lg'): Size variant applied to all child tabs.
    - ``layout`` ('hug' or 'fill'): Layout mode for tab sizing. 'hug': each tab hugs its content
      width. 'fill': tabs stretch equally to fill the container width.
    - ``hasDivider`` (boolean): Whether to show a bottom border divider under the tab list.
    - ``orientation`` ('horizontal' or 'vertical'): Orientation of the tab strip, controlling which
      arrow keys move focus between tabs and the reported aria-orientation. 'horizontal':
      ArrowLeft/ArrowRight. 'vertical': ArrowUp/ArrowDown. Both axes' arrows are accepted
      regardless.
    - ``children`` (ReactNode; required): Tab and TabMenu items to render inside the nav.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/TabList>.
    """

    def __init__(
        self,
        items: Iterable[Any],
        value: str,
        *,
        size: str | None = None,
        layout: str | None = None,
        divider: bool | None = None,
        orientation: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "TabList",
            value=value,
            props=_named_props(
                props,
                items=_option_records(items),
                size=size,
                layout=layout,
                hasDivider=divider,
                orientation=orientation,
            ),
        )


class SegmentedControl(Widget):
    """Render a compact Astryx segmented control.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    value : str
        Synchronized component value.
    label : str
        Visible or accessible label for the component.
    size : str | None, default None
        Control size.
    layout : str | None, default None
        Hug or fill segment layout.
    disabled : bool, default False
        Whether the entire control is disabled.
    **props : Any
        JSON-safe SegmentedControl props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe SegmentedControl props forwarded to Astryx.

    Supported Astryx props include:

    - ``value`` (string; required): The currently selected value (controlled).
    - ``onChange`` ((value: string) => void; required): Callback fired when a segment is selected.
    - ``label`` (string; required): Accessible label for the radio group (used as aria-label, never
      rendered visually).
    - ``size`` ('sm' or 'md' or 'lg'): Size variant for the control.
    - ``layout`` ('hug' or 'fill'): Layout mode. hug (default) sizes segments to content; fill
      stretches them equally to fill the container.
    - ``isDisabled`` (boolean): Whether the entire control is disabled.
    - ``children`` (ReactNode; required): SegmentedControlItem children.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/SegmentedControl>.
    """

    def __init__(
        self,
        items: Iterable[Any],
        value: str,
        *,
        label: str,
        size: str | None = None,
        layout: str | None = None,
        disabled: bool = False,
        **props: Any,
    ) -> None:
        super().__init__(
            "SegmentedControl",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props, items=_option_records(items), size=size, layout=layout
            ),
        )


class RadioList(Widget):
    """Render a single-choice Astryx radio list.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    value : str
        Synchronized component value.
    label : str
        Visible or accessible label for the component.
    orientation : str | None, default None
        Vertical or horizontal item layout.
    disabled : bool, default False
        Whether all radio items are disabled.
    size : str | None, default None
        Radio control size.
    label_hidden : bool | None, default None
        Whether to visually hide the accessible label.
    description : str | None, default None
        Helper text displayed with the group.
    status : Mapping[str, Any] | None, default None
        Validation status record.
    **props : Any
        JSON-safe RadioList props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe RadioList props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for the radio group (always rendered for
      accessibility).
    - ``value`` (string; required): The currently selected value.
    - ``onChange`` ((value: string) => void; required): Callback fired when the selected value
      changes.
    - ``children`` (ReactNode; required): RadioListItem elements.
    - ``isLabelHidden`` (boolean): Whether to visually hide the label.
    - ``description`` (string): Description text displayed below the label.
    - ``orientation`` ('vertical' or 'horizontal'): Layout direction of the radio items.
    - ``isDisabled`` (boolean): Whether all radio items are disabled.
    - ``isRequired`` (boolean): Whether the radio group is required.
    - ``isOptional`` (boolean): Whether the field is optional (mutually exclusive with isRequired).
    - ``status`` (InputStatus): Status indicator ({ type, message }).
    - ``size`` ('sm' or 'md'): Size of the radio controls.
    - ``labelTooltip`` (string): Tooltip text for an info icon next to the label.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/RadioList>.
    """

    def __init__(
        self,
        items: Iterable[Any],
        value: str,
        *,
        label: str,
        orientation: str | None = None,
        disabled: bool = False,
        size: str | None = None,
        label_hidden: bool | None = None,
        description: str | None = None,
        status: Mapping[str, Any] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "RadioList",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props,
                items=_option_records(items),
                orientation=orientation,
                size=size,
                isLabelHidden=label_hidden,
                description=description,
                status=status,
            ),
        )


class CheckboxList(Widget):
    """Render a multi-choice Astryx checkbox list.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    value : Iterable[str], default ()
        Synchronized component value.
    label : str
        Visible or accessible label for the component.
    density : str | None, default None
        Item spacing density.
    dividers : bool | None, default None
        Whether to show item dividers.
    disabled : bool, default False
        Whether all checkbox items are disabled.
    label_hidden : bool | None, default None
        Whether to visually hide the accessible label.
    description : str | None, default None
        Helper text displayed with the group.
    status : Mapping[str, Any] | None, default None
        Validation status record.
    **props : Any
        JSON-safe CheckboxList props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe CheckboxList props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for the checkbox group (always rendered for
      accessibility).
    - ``children`` (ReactNode; required): CheckboxListItem elements.
    - ``value`` (string[]): The currently selected values (collection mode).
    - ``onChange`` ((values: string[]) => void): Callback fired when the selected values change.
    - ``changeAction`` ((values: string[]) => void or Promise<void>): Async action on change with
      optimistic updates. While the promise is pending, the toggled item shows a spinner inside
      its checkbox and is marked aria-busy.
    - ``isLabelHidden`` (boolean): Whether to visually hide the label.
    - ``description`` (string): Description text displayed below the label.
    - ``density`` ('compact' or 'balanced' or 'spacious'): Spacing density for list items.
    - ``hasDividers`` (boolean): Whether to show dividers between items.
    - ``isDisabled`` (boolean): Whether all checkbox items are disabled.
    - ``status`` (InputStatus): Status indicator ({ type, message }).
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization. Must be a stylex.create()
      value.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/CheckboxList>.
    """

    def __init__(
        self,
        items: Iterable[Any],
        value: Iterable[str] = (),
        *,
        label: str,
        density: str | None = None,
        dividers: bool | None = None,
        disabled: bool = False,
        label_hidden: bool | None = None,
        description: str | None = None,
        status: Mapping[str, Any] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "CheckboxList",
            label=label,
            value=list(value),
            disabled=disabled,
            props=_named_props(
                props,
                items=_option_records(items),
                density=density,
                hasDividers=dividers,
                isLabelHidden=label_hidden,
                description=description,
                status=status,
            ),
        )


class ButtonGroup(Widget):
    """Render an Astryx button group from item records.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    label : str
        Visible or accessible label for the component.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked for frontend activations.
    action_callbacks : Iterable[Callable[[ComponentWidget, Any], None]] | None
        Python callbacks receiving the selected item value.
    orientation : str | None, default None
        Horizontal or vertical group orientation.
    size : str | None, default None
        Default child button size.
    disabled : bool, default False
        Whether all buttons are disabled.
    **props : Any
        JSON-safe ButtonGroup props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe ButtonGroup props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): Button or IconButton children.
    - ``label`` (string; required): Accessible group label used as aria-label.
    - ``orientation`` ('horizontal' or 'vertical'; default 'horizontal'): Button group orientation
      and keyboard navigation axis.
    - ``size`` ('sm' or 'md' or 'lg'; default 'md'): Default size for buttons in the group;
      individual buttons can override it.
    - ``isDisabled`` (boolean; default false): Disables all buttons in the group.
    - ``data-testid`` (string): Test selector for automated testing.
    - ``xstyle`` (StyleXStyles): StyleX styles for the group root.
    - ``className`` (string): CSS class names for the group root.
    - ``style`` (CSSProperties): Inline styles for the group root.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/ButtonGroup>.
    """

    def __init__(
        self,
        items: Iterable[Any],
        *,
        label: str,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        action_callbacks: Iterable[Callable[[ComponentWidget, Any], None]]
        | None = None,
        orientation: str | None = None,
        size: str | None = None,
        disabled: bool = False,
        **props: Any,
    ) -> None:
        super().__init__(
            "ButtonGroup",
            label=label,
            callbacks=callbacks,
            action_callbacks=action_callbacks,
            disabled=disabled,
            props=_named_props(
                props,
                items=_option_records(items),
                label=label,
                orientation=orientation,
                size=size,
            ),
        )


class AvatarGroup(Widget):
    """Render a compact group of Astryx avatars.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    overflow_count : int, default 0
        Number shown in the avatar-group overflow indicator.
    size : str | None, default None
        Avatar size used by the group.
    **props : Any
        JSON-safe AvatarGroup props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe AvatarGroup props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): Avatar children, optionally followed by one
      AvatarGroupOverflow. Consumers handle slicing to the desired visible count.
    - ``size`` (AvatarSize): Size applied to all avatars via context.
    - ``ref`` (React.Ref<HTMLDivElement>): Ref forwarded to the root element.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization.
    - ``data-testid`` (string): Test selector for automated testing frameworks.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/AvatarGroup>.
    """

    def __init__(
        self,
        items: Iterable[Any],
        *,
        overflow_count: int = 0,
        size: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "AvatarGroup",
            props=_named_props(
                props,
                items=_option_records(items),
                overflowCount=overflow_count,
                size=size,
            ),
        )


class Code(Widget):
    """Render inline code with Astryx styling.

    Parameters
    ----------
    code : str
        Astryx component option.
    **props : Any
        JSON-safe Code props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Code props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): Code content.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization. Must be a stylex.create()
      value.
    - ``className`` (string): CSS class name for the root element. Prefer xstyle for styling.
    - ``style`` (CSSProperties): Inline styles. Prefer xstyle for StyleX-optimized styling.
    - ``data-testid`` (string): Test selector for automated testing frameworks.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Code>.
    """

    def __init__(self, code: str, **props: Any) -> None:
        super().__init__("Code", text=code, props=props)


class Citation(Widget):
    """Render a compact inline citation reference.

    Parameters
    ----------
    source : Mapping[str, Any]
        Citation source metadata.
    number : int, default 1
        Citation number.
    variant : str, default 'number'
        Astryx visual variant.
    **props : Any
        JSON-safe Citation props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Citation props forwarded to Astryx.

    Supported Astryx props include:

    - ``source`` (CitationSource; required): The citation source object containing title, url, and
      optional icon.
    - ``number`` (number; required): The display index for this citation.
    - ``variant`` ('label' or 'number'): Display style: a label chip showing the source title or a
      compact numbered badge.

    See Astryx component docs: <https://astryx.atmeta.com/components/Citation>.
    """

    def __init__(
        self,
        source: Mapping[str, Any],
        *,
        number: int = 1,
        variant: str = "number",
        **props: Any,
    ) -> None:
        super().__init__(
            "Citation",
            value=number,
            variant=variant,
            props={
                "source": _clean_value(source),
                "number": number,
                "variant": variant,
                **props,
            },
        )


class Field(Widget):
    """Wrap a custom control with an Astryx field label.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    label : str
        Visible or accessible label for the component.
    input_id : str, default ''
        ID associated with the wrapped input element.
    description : str, default ''
        Supporting description text.
    status : Mapping[str, Any] | None
        Validation or status record displayed by Astryx.
    disabled : bool, default False
        Whether the component should render disabled.
    label_hidden : bool | None, default None
        Whether to visually hide the accessible label.
    optional : bool | None, default None
        Whether to mark the field optional.
    required : bool | None, default None
        Whether to mark the field required.
    status_variant : str | None, default None
        Attached or detached status presentation.
    width : int | float | str | None, default None
        Width of the complete field.
    **props : Any
        JSON-safe Field props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Field props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for the field (always rendered for accessibility).
    - ``inputID`` (string; required): ID for the input element (used for the label htmlFor
      attribute).
    - ``children`` (ReactNode; required): The input or control to render.
    - ``isLabelHidden`` (boolean): Visually hide the label (still accessible to screen readers).
    - ``isDisabled`` (boolean): Whether the associated input is disabled. Propagates disabled
      styling to the label.
    - ``description`` (string): Description text displayed between the label and input.
    - ``descriptionID`` (string): ID for the description element (use for aria-describedby on the
      input).
    - ``isOptional`` (boolean): Whether the field is optional (mutually exclusive with isRequired).
    - ``isRequired`` (boolean): Whether the field is required (mutually exclusive with isOptional).
    - ``labelIcon`` (IconType): Icon to display before the label text. See 'npx astryx docs icons'
      for valid semantic names.
    - ``labelTooltip`` (string): Tooltip text to display in an info icon at the end of the label.
    - ``status`` (FieldStatus): Status indicator with type and optional message. When message is
      set, displays a colored status box.
    - ``statusVariant`` ('attached' or 'detached'): How the status message renders relative to the
      input. Attached overlaps the input border; detached floats below.
    - ``width`` (SizeValue): Width of the field (number = pixels, string used as-is, e.g. "100%").
      Sizes the whole field (label, control, and status) so they stay aligned. Prefer this over
      setting width via xstyle/className/style, which only size the inner control box.
    - ``ref`` (React.Ref<HTMLDivElement>): Ref forwarded to the root element.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.
    - ``className`` (string): CSS class name(s) appended to the root element. Prefer xstyle for
      StyleX deduplication.
    - ``style`` (React.CSSProperties): Inline styles applied to the root element. Takes priority
      over StyleX inline styles.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Field>.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        label: str,
        input_id: str = "",
        description: str = "",
        status: Mapping[str, Any] | None = None,
        disabled: bool = False,
        label_hidden: bool | None = None,
        optional: bool | None = None,
        required: bool | None = None,
        status_variant: str | None = None,
        width: int | float | str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Field",
            children,
            label=label,
            disabled=disabled,
            width=width,
            props=_named_props(
                props,
                label=label,
                inputID=input_id,
                description=description or None,
                status=_clean_value(status) if status else None,
                isLabelHidden=label_hidden,
                isOptional=optional,
                isRequired=required,
                statusVariant=status_variant,
                width=width,
            ),
        )


class FieldStatus(Widget):
    """Render an Astryx field status message.

    Parameters
    ----------
    message : str
        Astryx component option.
    type : str, default 'success'
        Astryx component option.
    variant : str, default 'detached'
        Astryx visual variant.
    **props : Any
        JSON-safe FieldStatus props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe FieldStatus props forwarded to Astryx.

    Supported Astryx props include:

    - ``type`` ('error' or 'warning' or 'success'; required): Status type.
    - ``message`` (string; required): Status message text.
    - ``id`` (string): ID for aria-describedby association.
    - ``variant`` ('attached' or 'detached'): Visual variant: attached overlaps the input, detached
      floats below.

    See Astryx component docs: <https://astryx.atmeta.com/components/FieldStatus>.
    """

    def __init__(
        self,
        message: str,
        *,
        type: str = "success",
        variant: str = "detached",
        **props: Any,
    ) -> None:
        super().__init__(
            "FieldStatus",
            label=message,
            variant=type,
            props={"type": type, "message": message, "variant": variant, **props},
        )


class FormLayout(Widget):
    """Arrange Astryx form controls with consistent spacing.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    direction : str, default 'vertical'
        Layout direction.
    **props : Any
        JSON-safe FormLayout props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe FormLayout props forwarded to Astryx.

    Supported Astryx props include:

    - ``direction`` ('vertical' or 'horizontal' or 'horizontal-labels'): Controls field arrangement.
      Vertical stacks top-to-bottom, horizontal arranges left-to-right with equal flex-grow, and
      horizontal-labels uses CSS Grid with labels to the left of inputs (collapses to vertical
      on narrow viewports <=480px).
    - ``children`` (ReactNode): Form fields to arrange. Accepts Astryx inputs (TextInput, Selector,
      etc.) and Field-wrapped custom controls.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/FormLayout>.
    """

    def __init__(
        self, children: ChildInput = None, *, direction: str = "vertical", **props: Any
    ) -> None:
        super().__init__(
            "FormLayout", children, props={"direction": direction, **props}
        )


class InputGroup(Widget):
    """Group an input with prefix and suffix adornments.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    label : str
        Visible or accessible label for the component.
    prefix : str, default ''
        Text rendered before grouped input children.
    suffix : str, default ''
        Text rendered after grouped input children.
    disabled : bool, default False
        Whether the component should render disabled.
    label_hidden : bool | None, default None
        Whether to visually hide the accessible label.
    description : str | None, default None
        Helper text displayed with the group.
    optional : bool | None, default None
        Whether to mark the group optional.
    required : bool | None, default None
        Whether to mark the group required.
    size : str | None, default None
        Default child input size.
    status : Mapping[str, Any] | None, default None
        Validation status record.
    **props : Any
        JSON-safe InputGroup props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe InputGroup props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): Input and InputGroupText children.
    - ``label`` (string; required): Accessible label for the group.
    - ``isLabelHidden`` (boolean): Visually hide the label.
    - ``description`` (string): Helper text between label and input group.
    - ``isDisabled`` (boolean): Disable the entire group.
    - ``isOptional`` (boolean): Show "(optional)" indicator.
    - ``isRequired`` (boolean): Mark the field as required.
    - ``size`` ('sm' or 'md' or 'lg'): Default size for inputs in the group.
    - ``status`` (InputStatus): Status indicator applied to the group border.
    - ``labelTooltip`` (string): Tooltip text at the end of the label.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization.
    - ``data-testid`` (string): Test selector.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/InputGroup>.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        label: str,
        prefix: str = "",
        suffix: str = "",
        disabled: bool = False,
        label_hidden: bool | None = None,
        description: str | None = None,
        optional: bool | None = None,
        required: bool | None = None,
        size: str | None = None,
        status: Mapping[str, Any] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "InputGroup",
            children,
            label=label,
            disabled=disabled,
            props=_named_props(
                props,
                label=label,
                prefix=prefix or None,
                suffix=suffix or None,
                isLabelHidden=label_hidden,
                description=description,
                isOptional=optional,
                isRequired=required,
                size=size,
                status=status,
            ),
        )


class Collapsible(Widget):
    """Render expandable notebook content.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    trigger : str
        Trigger content used by disclosure or overlay components.
    open : bool, default True
        Controlled open state synchronized with Python.
    default_open : bool | None, default None
        Backward-compatible alias for ``open``.
    value : str, default ''
        Synchronized component value.
    **props : Any
        JSON-safe Collapsible props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Collapsible props forwarded to Astryx.

    Supported Astryx props include:

    - ``trigger`` (ReactNode; required): Content shown in the trigger area (always visible).
    - ``children`` (ReactNode): Content that collapses and expands.
    - ``defaultIsOpen`` (boolean): Default open state (uncontrolled).
    - ``isOpen`` (boolean): Controlled open state.
    - ``onOpenChange`` ((isOpen: boolean) => void): Callback invoked when the open state changes.
    - ``value`` (string): Identifier used for group coordination. Required when placed inside an
      CollapsibleGroup.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Collapsible>.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        trigger: str,
        open: bool = True,
        default_open: bool | None = None,
        value: str = "",
        **props: Any,
    ) -> None:
        effective_open = open if default_open is None else default_open
        super().__init__(
            "Collapsible",
            children,
            label=trigger,
            open=effective_open,
            props=_named_props(props, trigger=trigger, value=value or None),
        )


class Outline(Widget):
    """Render a table-of-contents outline.

    Parameters
    ----------
    items : Iterable[Mapping[str, Any]]
        Item records used by generated child components or static search sources.
    active_id : str, default ''
        Currently active outline item id.
    label : str, default 'Table of contents'
        Visible or accessible label for the component.
    density : str, default 'compact'
        Astryx density or spacing mode.
    **props : Any
        JSON-safe Outline props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Outline props forwarded to Astryx.

    Supported Astryx props include:

    - ``items`` (OutlineItem[]; required): Ordered heading items to render as table-of-contents
      links.
    - ``activeId`` (string): Currently active item id. When provided, disables built-in scroll spy
      state ownership.
    - ``onActiveIdChange`` ((id: string) => void): Called when the active item changes from scroll
      spy or click.
    - ``label`` (string; default 'Table of contents'): Accessible label for the nav landmark.
    - ``density`` ('default' or 'compact'; default 'default'): Controls item padding density.
    - ``data-testid`` (string): Test selector for automated testing.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization.
    - ``className`` (string): CSS class names for the nav element.
    - ``style`` (CSSProperties): Inline styles for the nav element.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Outline>.
    """

    def __init__(
        self,
        items: Iterable[Mapping[str, Any]],
        *,
        active_id: str = "",
        label: str = "Table of contents",
        density: str = "compact",
        **props: Any,
    ) -> None:
        super().__init__(
            "Outline",
            label=label,
            value=active_id,
            props={
                "items": _clean_value(list(items)),
                "label": label,
                "density": density,
                **props,
            },
        )


class TreeList(Widget):
    """Render hierarchical notebook data as an expandable tree.

    Parameters
    ----------
    items : Iterable[Mapping[str, Any]]
        Item records used by generated child components or static search sources.
    header : str, default ''
        Optional header text or content.
    density : str, default 'balanced'
        Astryx density or spacing mode.
    **props : Any
        JSON-safe TreeList props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe TreeList props forwarded to Astryx.

    Supported Astryx props include:

    - ``items`` (TreeListItemData[]; required): Recursive tree item data; nested children arrays
      create hierarchy.
    - ``density`` ('compact' or 'balanced' or 'spacious'; default 'balanced'): Spacing density for
      tree list items.
    - ``header`` (ReactNode): Header content rendered above the tree and associated with
      aria-labelledby.
    - ``data-testid`` (string): Test selector for automated testing.
    - ``xstyle`` (StyleXStyles): StyleX styles for the root element.
    - ``className`` (string): CSS class names for the root element.
    - ``style`` (CSSProperties): Inline styles for the root element.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/TreeList>.
    """

    def __init__(
        self,
        items: Iterable[Mapping[str, Any]],
        *,
        header: str = "",
        density: str = "balanced",
        **props: Any,
    ) -> None:
        super().__init__(
            "TreeList",
            props={
                "items": _clean_value(list(items)),
                "header": header or None,
                "density": density,
                **props,
            },
        )


class Toolbar(Widget):
    """Render an Astryx toolbar with optional slots.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    label : str
        Visible or accessible label for the component.
    size : str, default 'sm'
        Astryx component option.
    gap : int | float, default 1
        Astryx spacing step between children.
    orientation : str | None, default None
        Horizontal or vertical keyboard navigation.
    variant : str | None, default None
        Toolbar section visual variant.
    dividers : Iterable[str] | None, default None
        Toolbar sides that display divider borders.
    **props : Any
        JSON-safe Toolbar props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Toolbar props forwarded to Astryx.

    Supported Astryx props include:

    - ``startContent`` (ReactNode): Content aligned to the start side.
    - ``centerContent`` (ReactNode): Content centered between start and end; switches layout to a
      three-column grid.
    - ``endContent`` (ReactNode): Content aligned to the end side.
    - ``label`` (string; required): Accessible label applied to the toolbar element.
    - ``size`` ('sm' or 'md' or 'lg'; default 'md'): Toolbar size cascaded to common child controls
      through SizeContext.
    - ``gap`` (spacing step; default 1): Gap between items within each slot.
    - ``orientation`` ('horizontal' or 'vertical'; default 'horizontal'): Keyboard navigation
      orientation.
    - ``variant`` (SectionVariant; default transparent): Visual variant passed through to the
      underlying Section.
    - ``dividers`` (array of 'top', 'bottom', 'start', or 'end'): Divider borders passed through to
      the underlying Section.
    - ``xstyle`` (StyleXStyles): StyleX styles for the Section root.
    - ``className`` (string): CSS class names for the Section root.
    - ``style`` (CSSProperties): Inline styles for the Section root.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Toolbar>.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        label: str,
        size: str = "sm",
        gap: int | float = 1,
        orientation: str | None = None,
        variant: str | None = None,
        dividers: Iterable[str] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Toolbar",
            children,
            label=label,
            props=_named_props(
                props,
                label=label,
                size=size,
                gap=gap,
                orientation=orientation,
                variant=variant,
                dividers=list(dividers) if dividers is not None else None,
            ),
        )


class Tooltip(Widget):
    """Attach a tooltip to notebook content.

    Parameters
    ----------
    content : str | ChildInput
        Overlay or tooltip content.
    trigger : ChildInput
        Trigger content used by disclosure or overlay components.
    label : str, default ''
        Visible or accessible label for the component.
    placement : str | None, default None
        Placement relative to the trigger.
    alignment : str | None, default None
        Alignment along the placement axis.
    delay : int | None, default None
        Show delay in milliseconds.
    hide_delay : int | None, default None
        Hide delay in milliseconds.
    enabled : bool | None, default None
        Whether hover and focus triggers are enabled.
    open : bool | None, default None
        Optional controlled open state.
    default_open : bool | None, default None
        Initial uncontrolled open state.
    **props : Any
        JSON-safe Tooltip props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Tooltip props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode): Trigger content. When anchorRef is provided, children may be
      omitted.
    - ``anchorRef`` (React.RefObject<HTMLElement>): External tooltip anchor used for sibling-mode
      rendering.
    - ``content`` (ReactNode; required): Tooltip content, typically short non-interactive text.
    - ``placement`` (LayerPlacement; default 'above'): Placement relative to the anchor.
    - ``alignment`` (LayerAlignment; default 'center'): Alignment along the placement axis.
    - ``delay`` (number; default 200): Delay in milliseconds before showing on hover.
    - ``hideDelay`` (number; default 0): Delay in milliseconds before hiding after mouse or focus
      leave.
    - ``focusTrigger`` ('auto' or 'always' or 'never'; default 'auto'): Controls whether focus opens
      the tooltip.
    - ``isEnabled`` (boolean; default true): Enables or disables hover and focus triggers.
    - ``onOpenChange`` ((isOpen: boolean) => void): Called when tooltip visibility changes.
    - ``hasHoverIndication`` ('auto' or boolean; default 'auto'): Controls dashed underline hover
      indication on the trigger.
    - ``isOpen`` (boolean): Controlled open state.
    - ``isDefaultOpen`` (boolean): Initial uncontrolled open state.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Tooltip>.
    """

    def __init__(
        self,
        content: str | ChildInput,
        trigger: ChildInput = None,
        *,
        label: str = "",
        placement: str | None = None,
        alignment: str | None = None,
        delay: int | None = None,
        hide_delay: int | None = None,
        enabled: bool | None = None,
        open: bool | None = None,
        default_open: bool | None = None,
        **props: Any,
    ) -> None:
        children = {"trigger": trigger} if trigger is not None else None
        if not isinstance(content, str):
            children = (
                {"trigger": trigger, "content": content}
                if trigger is not None
                else {"content": content}
            )
            content_prop = None
        else:
            content_prop = content
        super().__init__(
            "Tooltip",
            children,
            label=label or content_prop or "",
            open=open,
            props=_named_props(
                props,
                content=content_prop,
                placement=placement,
                alignment=alignment,
                delay=delay,
                hideDelay=hide_delay,
                isEnabled=enabled,
                isOpen=open,
                isDefaultOpen=default_open,
            ),
        )


class HoverCard(Widget):
    """Attach a hover card with richer preview content.

    Parameters
    ----------
    content : str | ChildInput
        Overlay or tooltip content.
    trigger : ChildInput
        Trigger content used by disclosure or overlay components.
    label : str, default ''
        Visible or accessible label for the component.
    placement : str | None, default None
        Placement relative to the trigger.
    alignment : str | None, default None
        Alignment along the placement axis.
    delay : int | None, default None
        Show delay in milliseconds.
    hide_delay : int | None, default None
        Hide delay in milliseconds.
    enabled : bool | None, default None
        Whether hover and focus triggers are enabled.
    open : bool | None, default None
        Optional controlled open state.
    default_open : bool | None, default None
        Initial uncontrolled open state.
    **props : Any
        JSON-safe HoverCard props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe HoverCard props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): Trigger content.
    - ``content`` (ReactNode; required): Interactive hover card content.
    - ``placement`` (LayerPlacement; default 'above'): Placement relative to the anchor.
    - ``alignment`` (LayerAlignment; default 'center'): Alignment along the placement axis.
    - ``delay`` (number; default 300): Delay in milliseconds before showing on hover.
    - ``hideDelay`` (number; default 200): Delay in milliseconds before hiding after mouse or focus
      leave.
    - ``focusTrigger`` ('auto' or 'always' or 'never'; default 'auto'): Controls whether focus opens
      the hover card.
    - ``isEnabled`` (boolean; default true): Enables or disables hover and focus triggers.
    - ``onOpenChange`` ((isOpen: boolean) => void): Called when hover card visibility changes.
    - ``hasHoverIndication`` ('auto' or boolean; default 'auto'): Controls dashed underline hover
      indication on the trigger.
    - ``isOpen`` (boolean): Controlled open state.
    - ``isDefaultOpen`` (boolean): Initial uncontrolled open state.
    - ``xstyle`` (StyleXStyles): StyleX styles for the hover card content.
    - ``className`` (string): CSS class names for the hover card content.
    - ``style`` (CSSProperties): Inline styles for the hover card content.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/HoverCard>.
    """

    def __init__(
        self,
        content: str | ChildInput,
        trigger: ChildInput,
        *,
        label: str = "",
        placement: str | None = None,
        alignment: str | None = None,
        delay: int | None = None,
        hide_delay: int | None = None,
        enabled: bool | None = None,
        open: bool | None = None,
        default_open: bool | None = None,
        **props: Any,
    ) -> None:
        children = {"trigger": trigger}
        content_prop: str | None = content if isinstance(content, str) else None
        if not isinstance(content, str):
            children["content"] = content
        super().__init__(
            "HoverCard",
            children,
            label=label or content_prop or "",
            open=open,
            props=_named_props(
                props,
                content=content_prop,
                placement=placement,
                alignment=alignment,
                delay=delay,
                hideDelay=hide_delay,
                isEnabled=enabled,
                isOpen=open,
                isDefaultOpen=default_open,
            ),
        )


class Popover(Widget):
    """Render click-triggered popover content.

    Parameters
    ----------
    content : str | ChildInput
        Overlay or tooltip content.
    trigger : ChildInput
        Trigger content used by disclosure or overlay components.
    label : str
        Visible or accessible label for the component.
    placement : str | None, default None
        Placement relative to the trigger.
    alignment : str | None, default None
        Alignment along the placement axis.
    open : bool | None, default None
        Optional controlled open state.
    enabled : bool | None, default None
        Whether trigger interaction is enabled.
    width : int | float | str | None, default None
        Popover width.
    close_button : bool | None, default None
        Whether to include the accessible close button.
    auto_focus : bool | None, default None
        Whether content receives focus when opened.
    **props : Any
        JSON-safe Popover props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Popover props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode or render function): Trigger content. Automatic mode requires a button
      or role=button descendant; render-function mode receives trigger props.
    - ``anchorRef`` (React.RefObject<HTMLElement>): External button or role=button anchor used for
      sibling-mode rendering.
    - ``content`` (ReactNode; required): Popover dialog content.
    - ``placement`` (LayerPlacement; default 'below'): Placement relative to the trigger.
    - ``alignment`` (LayerAlignment; default 'start'): Alignment along the placement axis.
    - ``isOpen`` (boolean): Controlled open state.
    - ``onOpenChange`` ((isOpen: boolean) => void): Called when popover visibility changes.
    - ``isEnabled`` (boolean; default true): Disables trigger interactions when false.
    - ``width`` (number or string; default 'auto'): Popover container width. Numbers are pixels;
      strings are CSS values.
    - ``label`` (string): Accessible label for the popover dialog.
    - ``hasCloseButton`` (boolean): Includes a hidden close button for keyboard users.
    - ``closeButtonLabel`` (string; default 'Close popover'): Accessible label for the hidden close
      button.
    - ``hasAutoFocus`` (boolean; default true): Auto-focuses the first focusable element when
      opened.
    - ``data-testid`` (string): Test selector for the popover container.
    - ``xstyle`` (StyleXStyles): StyleX styles for the popover content.
    - ``className`` (string): CSS class names for the popover content.
    - ``style`` (CSSProperties): Inline styles for the popover content.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Popover>.
    """

    def __init__(
        self,
        content: str | ChildInput,
        trigger: ChildInput,
        *,
        label: str,
        placement: str | None = None,
        alignment: str | None = None,
        open: bool | None = None,
        enabled: bool | None = None,
        width: int | float | str | None = None,
        close_button: bool | None = None,
        auto_focus: bool | None = None,
        **props: Any,
    ) -> None:
        children = {"trigger": trigger}
        content_prop: str | None = content if isinstance(content, str) else None
        if not isinstance(content, str):
            children["content"] = content
        super().__init__(
            "Popover",
            children,
            label=label,
            open=open,
            width=width,
            props=_named_props(
                props,
                content=content_prop,
                label=label,
                placement=placement,
                alignment=alignment,
                isOpen=open,
                isEnabled=enabled,
                width=width,
                hasCloseButton=close_button,
                hasAutoFocus=auto_focus,
            ),
        )


class DropdownMenu(Widget):
    """Render a button-backed Astryx dropdown menu.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    label : str
        Visible or accessible label for the component.
    variant : str, default 'secondary'
        Astryx visual variant.
    disabled : bool, default False
        Whether the component should render disabled.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked for frontend activations.
    action_callbacks : Iterable[Callable[[ComponentWidget, Any], None]] | None
        Python callbacks receiving the selected menu value.
    open : bool, default False
        Controlled menu visibility.
    menu_width : int | float | str | None, default None
        Menu width; defaults to the trigger width.
    chevron : bool | None, default None
        Whether the trigger shows a chevron.
    placement : str | None, default None
        Menu placement relative to the trigger.
    auto_focus : bool | None, default None
        Whether the first menu item receives focus on open.
    **props : Any
        JSON-safe DropdownMenu props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe DropdownMenu props forwarded to Astryx.

    Supported Astryx props include:

    - ``button`` (DropdownMenuButtonProps): Props for the trigger button (Button props except
      onClick).
    - ``items`` (DropdownMenuOption[]; required): Array of menu entries. Each entry is one of: an
      action item '{label, onClick?, icon?, isDisabled?}', a divider '{type: "divider"}', or a
      section '{type: "section", title?, items: [...action items]}'.
    - ``isMenuOpen`` (boolean): Controlled open state for the menu.
    - ``onOpenChange`` ((isOpen: boolean) => void): Callback fired when the open state changes.
    - ``menuWidth`` (number or string): Custom menu width; defaults to matching the trigger button
      width.
    - ``onClick`` (() => void): Callback fired when the trigger button is clicked.
    - ``hasChevron`` (boolean): Whether to show a chevron icon on the trigger button. Set to false
      for icon-only triggers.
    - ``children`` ((item: DropdownMenuItemData) => ReactNode): Custom render function for each item
      in the list.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/DropdownMenu>.
    """

    def __init__(
        self,
        items: Iterable[Any],
        *,
        label: str,
        variant: str = "secondary",
        disabled: bool = False,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        action_callbacks: Iterable[Callable[[ComponentWidget, Any], None]]
        | None = None,
        open: bool = False,
        menu_width: int | float | str | None = None,
        chevron: bool | None = None,
        placement: str | None = None,
        auto_focus: bool | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "DropdownMenu",
            label=label,
            variant=variant,
            disabled=disabled,
            callbacks=callbacks,
            action_callbacks=action_callbacks,
            open=open,
            props=_named_props(
                props,
                items=_option_records(items),
                button={"label": label, "variant": variant},
                menuWidth=menu_width,
                hasChevron=chevron,
                placement=placement,
                hasAutoFocus=auto_focus,
            ),
        )


class MoreMenu(Widget):
    """Render a compact overflow action menu.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    label : str, default 'More options'
        Visible or accessible label for the component.
    variant : str, default 'ghost'
        Astryx visual variant.
    disabled : bool, default False
        Whether the component should render disabled.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked for frontend activations.
    action_callbacks : Iterable[Callable[[ComponentWidget, Any], None]] | None
        Python callbacks receiving the selected menu value.
    size : str | None, default None
        Trigger button size.
    open : bool, default False
        Controlled menu visibility.
    auto_focus : bool | None, default None
        Whether the first menu item receives focus on open.
    **props : Any
        JSON-safe MoreMenu props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe MoreMenu props forwarded to Astryx.

    Supported Astryx props include:

    - ``items`` (DropdownMenuOption[]; required): Menu items: data array of actions, dividers, and
      sections. Same type as DropdownMenu items prop.
    - ``label`` (string): Accessible label for the trigger button (aria-label) and tooltip text.
    - ``variant`` (ButtonVariant): Visual style variant of the trigger button.
    - ``size`` (ButtonSize): Size of the trigger button.
    - ``icon`` (ReactNode): Override the default three-dot icon. Accepts any ReactNode.
    - ``isDisabled`` (boolean): Whether the menu trigger is disabled.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/MoreMenu>.
    """

    def __init__(
        self,
        items: Iterable[Any],
        *,
        label: str = "More options",
        variant: str = "ghost",
        disabled: bool = False,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        action_callbacks: Iterable[Callable[[ComponentWidget, Any], None]]
        | None = None,
        size: str | None = None,
        open: bool = False,
        auto_focus: bool | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "MoreMenu",
            label=label,
            variant=variant,
            disabled=disabled,
            callbacks=callbacks,
            action_callbacks=action_callbacks,
            open=open,
            props=_named_props(
                props,
                items=_option_records(items),
                label=label,
                variant=variant,
                size=size,
                hasAutoFocus=auto_focus,
            ),
        )


class Calendar(Widget):
    """Render an Astryx calendar date picker.

    Parameters
    ----------
    value : str | Mapping[str, str] | None
        Synchronized component value.
    mode : str, default 'single'
        Component mode.
    number_of_months : int | None, default None
        Number of months displayed.
    min : str | None, default None
        Minimum selectable ISO date.
    max : str | None, default None
        Maximum selectable ISO date.
    outside_days : bool | None, default None
        Whether to show dates from adjacent months.
    week_numbers : bool | None, default None
        Whether to show ISO week numbers.
    variable_rows : bool | None, default None
        Whether the calendar uses a variable row count.
    week_starts_on : int | str | None, default None
        First day of the week.
    **props : Any
        JSON-safe Calendar props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Calendar props forwarded to Astryx.

    Supported Astryx props include:

    - ``mode`` ('single' or 'range'): Selection mode.
    - ``value`` (ISODateString or DateRange): Controlled selected value.
    - ``defaultValue`` (ISODateString or DateRange): Uncontrolled default value.
    - ``onChange`` (Function): Selection callback.
    - ``numberOfMonths`` (1 or 2): Number of months to display.
    - ``min`` (ISODateString): Minimum selectable date.
    - ``max`` (ISODateString): Maximum selectable date.
    - ``dateConstraints`` (Array<(date: Date) => boolean>): Custom constraint functions.
    - ``focusDate`` (ISODateString): Controlled visible month.
    - ``onFocusDateChange`` ((focusDate: ISODateString) => void): Navigation callback.
    - ``handleRef`` (React.Ref<CalendarHandle>): Imperative handle for calendar navigation,
      including navigateTo().
    - ``hasOutsideDays`` (boolean): Show days from adjacent months.
    - ``hasWeekNumbers`` (boolean): Show ISO week numbers.
    - ``hasVariableRowCount`` (boolean): Variable vs fixed 6-row grid.
    - ``weekStartsOn`` (0 or 1 or 2 or 3 or 4 or 5 or 6 or 'sun' or 'mon' or 'tue' or 'wed' or 'thu'
      or 'fri' or 'sat'): First day of week. Accepts a number (0=Sunday) or a three-letter day
      name (e.g. "mon").

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Calendar>.
    """

    def __init__(
        self,
        value: str | Mapping[str, str] | None = None,
        *,
        mode: str = "single",
        number_of_months: int | None = None,
        min: str | None = None,
        max: str | None = None,
        outside_days: bool | None = None,
        week_numbers: bool | None = None,
        variable_rows: bool | None = None,
        week_starts_on: int | str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Calendar",
            value=value,
            props=_named_props(
                props,
                mode=mode,
                numberOfMonths=number_of_months,
                min=min,
                max=max,
                hasOutsideDays=outside_days,
                hasWeekNumbers=week_numbers,
                hasVariableRowCount=variable_rows,
                weekStartsOn=week_starts_on,
            ),
        )


class FileInput(Widget):
    """Render an Astryx file input.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    value : Any
        Synchronized component value.
    multiple : bool, default False
        Whether multiple files can be selected.
    disabled : bool, default False
        Whether the component should render disabled.
    accept : str | None, default None
        Accepted MIME types or file extensions.
    max_size : int | None, default None
        Maximum file size in bytes.
    max_files : int | None, default None
        Maximum number of selected files.
    label_hidden : bool | None, default None
        Whether to visually hide the accessible label.
    description : str | None, default None
        Helper text displayed with the input.
    loading : bool | None, default None
        Whether to show the loading state.
    placeholder : str | None, default None
        Placeholder text.
    mode : str | None, default None
        Compact input or dropzone presentation.
    status : Mapping[str, Any] | None, default None
        Validation status record.
    **props : Any
        JSON-safe FileInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe FileInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessible label for the file input.
    - ``value`` (File or File[] or null; required): Currently selected file(s). Controlled
      component.
    - ``onChange`` ((files: File or File[] or null) => void; required): Callback fired when files
      are selected or removed.
    - ``changeAction`` ((files: File or File[] or null) => Promise<void>): Async change action
      (React 19 transitions pattern). Use for immediate upload on file selection.
    - ``accept`` (string): Accepted file types. Uses the HTML accept attribute format (e.g.
      "image/*", ".pdf,.doc").
    - ``isMultiple`` (boolean): Whether multiple files can be selected. When true, value and
      onChange use File[] instead of File.
    - ``maxSize`` (number): Maximum file size in bytes. Files exceeding this are rejected with an
      error status.
    - ``maxFiles`` (number): Maximum number of files (only applies when isMultiple is true).
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible to screen
      readers.
    - ``description`` (string): Description text displayed between the label and input.
    - ``isOptional`` (boolean): Displays an "Optional" indicator next to the label. Mutually
      exclusive with isRequired.
    - ``isRequired`` (boolean): Displays a "Required" indicator next to the label and sets
      aria-required. Mutually exclusive with isOptional.
    - ``isDisabled`` (boolean): Disables the input, preventing interaction and dimming the element.
    - ``isLoading`` (boolean): Puts the input in a loading state, showing a spinner and setting
      aria-busy.
    - ``placeholder`` (string): Placeholder text shown when no file is selected.
    - ``mode`` ('input' or 'dropzone'): Visual mode. 'input' is a compact inline style; 'dropzone'
      is a larger area with drag-and-drop support.
    - ``status`` ({type: 'error' or 'warning' or 'success', message?: string}): Validation status:
      applies a colored border. If message is provided, displays a floating message below the
      input. Error type also sets aria-invalid.
    - ``labelTooltip`` (string): Tooltip text displayed in an info icon at the end of the label.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/FileInput>.

    Notes
    -----
    The synchronized value contains file metadata only; file bytes are not sent to Python."""

    def __init__(
        self,
        *,
        label: str,
        value: Any = None,
        multiple: bool = False,
        disabled: bool = False,
        accept: str | None = None,
        max_size: int | None = None,
        max_files: int | None = None,
        label_hidden: bool | None = None,
        description: str | None = None,
        loading: bool | None = None,
        placeholder: str | None = None,
        mode: str | None = None,
        status: Mapping[str, Any] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "FileInput",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props,
                label=label,
                isMultiple=multiple,
                accept=accept,
                maxSize=max_size,
                maxFiles=max_files,
                isLabelHidden=label_hidden,
                description=description,
                isLoading=loading,
                placeholder=placeholder,
                mode=mode,
                status=status,
            ),
        )


class Typeahead(Widget):
    """Render a notebook-safe Astryx typeahead.

    Parameters
    ----------
    items : Iterable[Any] | Mapping[str, Any]
        Searchable items. Mappings, pairs, strings, and dictionaries are
        normalized into ``{"id": ..., "label": ...}`` records.
    value : str | None
        Selected item id synchronized back to Python. Use ``None`` for no
        initial selection.
    label : str
        Accessible field label.
    disabled : bool, default False
        Whether the input should render disabled.
    search : Callable[[str], Iterable[Any]] | None
        Optional Python-backed search source. The callback receives the current
        query string and returns item records, pairs, mappings, or strings that
        can be normalized into ``{"id": ..., "label": ...}`` records. When
        omitted, the frontend uses a static in-browser search source backed by
        ``items``.
    placeholder : str | None, default None
        Input placeholder text.
    entries_on_focus : bool | None, default None
        Whether focus displays bootstrap results.
    clear : bool | None, default None
        Whether to show a clear button.
    max_menu_items : int | None, default None
        Maximum visible search results.
    label_hidden : bool | None, default None
        Whether to visually hide the accessible label.
    description : str | None, default None
        Helper text displayed with the input.
    size : str | None, default None
        Input size.
    debounce_ms : int | None, default None
        Search debounce duration.
    **props : Any
        JSON-safe Typeahead props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Typeahead props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessible label for the input.
    - ``searchSource`` (SearchSource<T>; required): Data source providing search and bootstrap
      methods for populating the dropdown.
    - ``value`` (T or null; required): Currently selected item, or null if nothing is selected.
    - ``onChange`` ((item: T or null) => void; required): Called when the selection changes.
    - ``placeholder`` (string): Input placeholder text.
    - ``hasEntriesOnFocus`` (boolean): Show bootstrap results on focus before typing.
    - ``hasClear`` (boolean): Show clear button to deselect the current value.
    - ``isDisabled`` (boolean): Disables the input.
    - ``maxMenuItems`` (number): Maximum number of dropdown items to display.
    - ``status`` (InputStatus): Validation status object with type and message for
      error/warning/success states.
    - ``renderItem`` ((item: T) => ReactNode): Custom render function for dropdown items. Default
      renders TypeaheadItem.
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible.
    - ``description`` (string): Helper text displayed below the label.
    - ``isRequired`` (boolean): Marks the field as required.
    - ``isOptional`` (boolean): Shows an optional indicator on the label.
    - ``labelTooltip`` (string): Tooltip text shown on the label.
    - ``emptySearchResultsText`` (string): Text shown when search returns no results.
    - ``hasAutoFocus`` (boolean): Auto-focus the input on mount.
    - ``size`` ('sm' or 'md' or 'lg'): Input and token size.
    - ``debounceMs`` (number): Debounce delay in ms before triggering search. Set to 0 for
      synchronous sources.
    - ``onChangeQuery`` ((query: string) => void): Callback fired when the search query text
      changes.
    - ``onOpenChange`` ((isOpen: boolean) => void): Callback when the dropdown opens or closes.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Typeahead>.

    Notes
    -----
    With ``search=None``, the frontend receives an Astryx ``createStaticSource``
    backed by ``items``. With a Python search callback, the frontend uses
    Astryx's async ``SearchSource`` interface and resolves each query through
    the anywidget comm channel. The selected item id is stored in ``value``."""

    def __init__(
        self,
        items: Iterable[Any] | Mapping[str, Any],
        value: str | None = None,
        *,
        label: str,
        disabled: bool = False,
        search: Callable[[str], Iterable[Any]] | None = None,
        placeholder: str | None = None,
        entries_on_focus: bool | None = None,
        clear: bool | None = None,
        max_menu_items: int | None = None,
        label_hidden: bool | None = None,
        description: str | None = None,
        size: str | None = None,
        debounce_ms: int | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Typeahead",
            label=label,
            value=value,
            disabled=disabled,
            search=search,
            props=_named_props(
                props,
                items=_search_records(items),
                label=label,
                placeholder=placeholder,
                hasEntriesOnFocus=entries_on_focus,
                hasClear=clear,
                maxMenuItems=max_menu_items,
                isLabelHidden=label_hidden,
                description=description,
                size=size,
                debounceMs=debounce_ms,
            ),
        )


class Tokenizer(Widget):
    """Render a notebook-safe Astryx tokenizer.

    Parameters
    ----------
    items : Iterable[Any] | Mapping[str, Any]
        Searchable items. Mappings, pairs, strings, and dictionaries are
        normalized into ``{"id": ..., "label": ...}`` records.
    value : Iterable[str], default ()
        Selected item ids synchronized back to Python.
    label : str
        Accessible field label.
    disabled : bool, default False
        Whether the input and token interactions should render disabled.
    search : Callable[[str], Iterable[Any]] | None
        Optional Python-backed search source. The callback receives the current
        query string and returns item records, pairs, mappings, or strings that
        can be normalized into ``{"id": ..., "label": ...}`` records. When
        omitted, the frontend uses a static in-browser search source backed by
        ``items``.
    placeholder : str | None, default None
        Input placeholder text.
    max_entries : int | None, default None
        Maximum selected tokens.
    clear : bool | None, default None
        Whether to show a clear-all button.
    create : bool | None, default None
        Whether users can create tokens from free text.
    max_menu_items : int | None, default None
        Maximum visible search results.
    label_hidden : bool | None, default None
        Whether to visually hide the accessible label.
    description : str | None, default None
        Helper text displayed with the input.
    size : str | None, default None
        Input and token size.
    debounce_ms : int | None, default None
        Search debounce duration.
    **props : Any
        JSON-safe Tokenizer props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Tokenizer props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessible label for the input.
    - ``searchSource`` (SearchSource<T>; required): Data source providing search and bootstrap
      methods for populating the dropdown.
    - ``value`` (T[]; required): Array of currently selected items.
    - ``onChange`` ((items: T[], change: TokenizerChange<T>) => void; required): Called when
      selection changes. The change argument includes the affected item and type ('add' or
      'create' or 'remove' or 'reorder').
    - ``placeholder`` (string): Input placeholder text. Only shown when no tokens are selected.
    - ``maxEntries`` (number): Maximum number of selections allowed. Input is hidden when the limit
      is reached.
    - ``hasClear`` (boolean): Show a clear-all button for bulk removal of all tokens.
    - ``renderToken`` ((item: T, onRemove: () => void) => ReactNode): Custom render function for
      selected tokens. Default renders Token with label and onRemove.
    - ``renderItem`` ((item: T) => ReactNode): Custom render function for dropdown items. Default
      renders TypeaheadItem.
    - ``isDisabled`` (boolean): Disables the input and all token interactions.
    - ``status`` (InputStatus): Validation status object with type and message for
      error/warning/success states.
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible.
    - ``description`` (string): Helper text displayed below the label.
    - ``isRequired`` (boolean): Marks the field as required.
    - ``isOptional`` (boolean): Shows an optional indicator on the label.
    - ``labelTooltip`` (string): Tooltip text shown on the label.
    - ``hasEntriesOnFocus`` (boolean): Show bootstrap results on focus before typing.
    - ``maxMenuItems`` (number): Maximum number of dropdown items to display.
    - ``emptySearchResultsText`` (string): Text shown when search returns no results.
    - ``hasAutoFocus`` (boolean): Auto-focus the input on mount.
    - ``size`` ('sm' or 'md' or 'lg'): Input and token size.
    - ``debounceMs`` (number): Debounce delay in ms before triggering search. Set to 0 for
      synchronous sources.
    - ``hasCreate`` (boolean): Allow users to create new tokens from free-text input. When true, a
      "Create" option appears in the dropdown for typed text that doesn't match existing
      results. The onChange change type is 'create' for these items.
    - ``onChangeQuery`` ((query: string) => void): Callback fired when the search query text
      changes.
    - ``endContent`` (ReactNode): Content to display at the end of the input row. Useful for
      buttons, result counts, or other controls.
    - ``handleRef`` (React.Ref<TokenizerHandle>): Imperative handle for focus() and blur() control.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value - not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Tokenizer>.

    Notes
    -----
    The wrapper stores selected ids in ``value`` rather than complete item
    records so notebook state remains compact and JSON-safe."""

    def __init__(
        self,
        items: Iterable[Any] | Mapping[str, Any],
        value: Iterable[str] = (),
        *,
        label: str,
        disabled: bool = False,
        search: Callable[[str], Iterable[Any]] | None = None,
        placeholder: str | None = None,
        max_entries: int | None = None,
        clear: bool | None = None,
        create: bool | None = None,
        max_menu_items: int | None = None,
        label_hidden: bool | None = None,
        description: str | None = None,
        size: str | None = None,
        debounce_ms: int | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Tokenizer",
            label=label,
            value=list(value),
            disabled=disabled,
            search=search,
            props=_named_props(
                props,
                items=_search_records(items),
                label=label,
                placeholder=placeholder,
                maxEntries=max_entries,
                hasClear=clear,
                hasCreate=create,
                maxMenuItems=max_menu_items,
                isLabelHidden=label_hidden,
                description=description,
                size=size,
                debounceMs=debounce_ms,
            ),
        )


class CommandPalette(Widget):
    """Render an inline Astryx command palette for notebook output areas.

    Parameters
    ----------
    items : Iterable[Any] | Mapping[str, Any]
        Command records. Mappings, pairs, strings, and dictionaries are
        normalized into ``{"id": ..., "label": ...}`` records.
    value : str | None
        Selected command id synchronized back to Python.
    label : str, default 'Command palette'
        Accessible dialog label.
    search : Callable[[str], Iterable[Any]] | None, default None
        Optional Python search callback. When provided, Astryx search queries
        are sent to Python and callback results are normalized into
        ``{"id": ..., "label": ...}`` command records. When omitted, the
        frontend builds a static search source from ``items``.
    open : bool, default True
        Controlled palette visibility.
    inline : bool, default True
        Whether to render inside the notebook output instead of as a modal.
    width : int | float | str | None, default None
        Palette width.
    max_height : int | float | str | None, default None
        Maximum palette height.
    empty_search_text : str | None, default None
        Message shown when a query has no results.
    empty_bootstrap_text : str | None, default None
        Message shown when the initial item source is empty.
    **props : Any
        JSON-safe CommandPalette props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe CommandPalette props forwarded to Astryx.

    Supported Astryx props include:

    - ``isOpen`` (boolean; required): Whether the command palette dialog is visible.
    - ``onOpenChange`` ((isOpen: boolean) => void; required): Called when the palette visibility
      changes.
    - ``searchSource`` (SearchSource<T>; required): Search source providing items via search(query)
      and bootstrap(). Use createStaticSource for static lists.
    - ``input`` (ReactNode): Input slot. Defaults to CommandPaletteInput with standard behavior.
    - ``footer`` (ReactNode): Footer slot. Defaults to CommandPaletteFooter showing keyboard hints.
    - ``renderItem`` ((item: T, isSelected: boolean) => ReactNode): Per-item render function.
      Auto-grouping by auxiliaryData.group is preserved. When omitted, renders label text.
    - ``emptySearchText`` (ReactNode): Content shown when a search query returns no results.
    - ``emptyBootstrapText`` (ReactNode): Content shown when there is no search query and
      bootstrap() returns nothing.
    - ``value`` (string): Controlled selected value for picker mode.
    - ``onValueChange`` ((value: string) => void): Called when the selected value changes in picker
      mode.
    - ``label`` (string): Accessible label for the command palette dialog.
    - ``width`` (number or string): Width of the dialog.
    - ``maxHeight`` (number or string): Maximum height of the dialog.
    - ``isInline`` (boolean): Renders command palette content inline without modal behavior.
      Automatically disables input auto-focus and initial highlighted-item auto-scroll. For
      documentation previews and showcases only.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/CommandPalette>.

    Notes
    -----
    The palette renders inline and open by default so it remains contained in a
    Jupyter output area instead of creating a page-level modal overlay."""

    def __init__(
        self,
        items: Iterable[Any] | Mapping[str, Any],
        value: str | None = None,
        *,
        label: str = "Command palette",
        search: Callable[[str], Iterable[Any]] | None = None,
        open: bool = True,
        inline: bool = True,
        width: int | float | str | None = None,
        max_height: int | float | str | None = None,
        empty_search_text: str | None = None,
        empty_bootstrap_text: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "CommandPalette",
            label=label,
            value=value,
            search=search,
            open=open,
            width=width,
            props=_named_props(
                props,
                items=_search_records(items),
                label=label,
                isInline=inline,
                width=width,
                maxHeight=max_height,
                emptySearchText=empty_search_text,
                emptyBootstrapText=empty_bootstrap_text,
            ),
        )


class Dialog(Widget):
    """Render Astryx dialog content inline in notebook output.

    Parameters
    ----------
    children : ChildInput
        Dialog body content. Pass a widget, a sequence of widgets, or a mapping
        of slot names to widgets.
    open : bool, default True
        Controlled open state synchronized through ``is_open``.
    inline : bool, default True
        Whether dialog content renders inline instead of using native modal
        behavior.
    width : int | float | str | None, default None
        Dialog width.
    max_height : int | float | str | None, default None
        Maximum dialog height.
    position : Mapping[str, Any] | None, default None
        Static top, right, bottom, and left position values.
    variant : str | None, default None
        Standard or fullscreen dialog presentation.
    purpose : str | None, default None
        Required, form, or informational dismissal behavior.
    **props : Any
        JSON-safe Dialog props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Dialog props forwarded to Astryx.

    Supported Astryx props include:

    - ``isOpen`` (boolean; required): Whether the dialog is open.
    - ``onOpenChange`` ((isOpen: boolean) => unknown; required): Callback when dialog visibility
      changes.
    - ``children`` (ReactNode; required): Dialog content.
    - ``width`` (number or string): Width of the dialog in pixels or any CSS value.
    - ``maxHeight`` (number or string): Maximum height of the dialog.
    - ``position`` (DialogPosition): Static position for the dialog; centered by default when
      omitted.
    - ``variant`` ('standard' or 'fullscreen'): Dialog variant: fullscreen expands to fill the
      entire viewport.
    - ``purpose`` ('required' or 'form' or 'info'): Controls dismissal behavior: required disables
      Escape and backdrop click; form disables backdrop click after interaction; info allows
      both.
    - ``isInline`` (boolean): Renders dialog content inline without the <dialog> element, backdrop,
      or modal behavior. For documentation previews and showcases only.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Dialog>.

    Notes
    -----
    The wrapper defaults to inline rendering to avoid modal focus-management
    conflicts inside Jupyter output areas. Set ``inline=False`` only when the
    surrounding notebook environment can safely host modal dialogs."""

    def __init__(
        self,
        children: ChildInput = None,
        *,
        open: bool = True,
        inline: bool = True,
        width: int | float | str | None = None,
        max_height: int | float | str | None = None,
        position: Mapping[str, Any] | None = None,
        variant: str | None = None,
        purpose: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Dialog",
            children,
            open=open,
            width=width,
            props=_named_props(
                props,
                isInline=inline,
                width=width,
                maxHeight=max_height,
                position=position,
                variant=variant,
                purpose=purpose,
            ),
        )


class AlertDialog(Widget):
    """Render an inline Astryx alert dialog for confirmations.

    Parameters
    ----------
    title : str
        Dialog title linked to the alert for accessibility.
    description : str
        Consequence or confirmation text linked to the alert for accessibility.
    action_label : str
        Primary action button label.
    cancel_label : str, default 'Cancel'
        Cancel button label.
    open : bool, default True
        Controlled open state synchronized through ``is_open``.
    inline : bool, default True
        Whether dialog content renders inline instead of using native modal
        behavior.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked when the primary action is activated.
    action_callbacks : Iterable[Callable[[ComponentWidget, Any], None]] | None
        Python callbacks receiving the ``"confirm"`` action identifier.
    action_variant : str | None, default None
        Primary action button variant.
    action_loading : bool | None, default None
        Whether the primary action shows a loading state.
    width : int | float | str | None, default None
        Dialog width.
    **props : Any
        JSON-safe AlertDialog props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe AlertDialog props forwarded to Astryx.

    Supported Astryx props include:

    - ``isOpen`` (boolean; required): Whether the dialog is open.
    - ``onOpenChange`` ((isOpen: boolean) => unknown; required): Visibility change callback.
    - ``title`` (string; required): Dialog title. Linked via aria-labelledby.
    - ``description`` (string; required): Consequence description. Linked via aria-describedby.
    - ``actionLabel`` (string; required): Action button label.
    - ``onAction`` (() => unknown; required): Called when action button is clicked. Does NOT
      auto-close.
    - ``cancelLabel`` (string): Cancel button label.
    - ``actionVariant`` (ButtonVariant): Action button variant.
    - ``isActionLoading`` (boolean): Shows loading spinner on the action button.
    - ``width`` (number or string): Dialog width.
    - ``isInline`` (boolean): Renders alert dialog content inline without modal behavior. For
      documentation previews and showcases only.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/AlertDialog>.

    Notes
    -----
    The wrapper defaults to inline rendering to avoid modal focus-management
    conflicts inside Jupyter output areas. The primary action emits a click
    message with ``action="confirm"``."""

    def __init__(
        self,
        title: str,
        description: str,
        *,
        action_label: str,
        cancel_label: str = "Cancel",
        open: bool = True,
        inline: bool = True,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        action_callbacks: Iterable[Callable[[ComponentWidget, Any], None]]
        | None = None,
        action_variant: str | None = None,
        action_loading: bool | None = None,
        width: int | float | str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "AlertDialog",
            label=title,
            text=description,
            open=open,
            callbacks=callbacks,
            action_callbacks=action_callbacks,
            width=width,
            props=_named_props(
                props,
                title=title,
                description=description,
                actionLabel=action_label,
                cancelLabel=cancel_label,
                isInline=inline,
                actionVariant=action_variant,
                isActionLoading=action_loading,
                width=width,
            ),
        )
