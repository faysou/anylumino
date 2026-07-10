"""Astryx input and typography widgets."""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any

from ..components import ComponentWidget
from .base import Widget
from .base import _named_props
from .base import _option_records


class Text(Widget):
    """Render themed Astryx body text.

    Parameters
    ----------
    text : str
        Text content synchronized to the frontend component.
    text_type : str | None, default None
        Semantic Astryx text type, such as ``"body"``, ``"supporting"``, or ``"display-1"``.
    size : str | None, default None
        Explicit font-size override.
    color : str | None, default None
        Theme text color.
    weight : str | None, default None
        Font-weight override.
    display : str | None, default None
        Inline or block display mode.
    max_lines : int | None, default None
        Maximum rendered lines before truncation.
    text_wrap : str | None, default None
        Text wrapping behavior.
    justify : str | None, default None
        Logical text alignment.
    tabular_numbers : bool | None, default None
        Whether numeric glyphs use tabular widths.
    **props : Any
        Additional JSON-safe Text props forwarded to Astryx. The older
        ``props={...}`` mapping form remains supported.

    Astryx Props
    ------------
    JSON-safe Text props forwarded to Astryx.

    Supported Astryx props include:

    - ``type`` ('body' or 'large' or 'label' or 'supporting' or 'code' or 'display-1' or 'display-2'
      or 'display-3'): Semantic text type. Determines size, weight, and line-height from the
      theme. Note: this prop is called 'type', not 'variant'.
    - ``children`` (ReactNode; required): Text content.
    - ``size`` ('4xs' or '3xs' or '2xs' or 'xsm' or 'sm' or 'base' or 'lg' or 'xl' or '2xl' or '3xl'
      or '4xl'): Explicit font size override. Overrides the size from 'type' but preserves other
      type properties. Prefer using 'type' alone.
    - ``color`` ('primary' or 'secondary' or 'disabled' or 'placeholder' or 'accent' or 'inherit'):
      Text color. Defaults to 'secondary' for the 'supporting' type, 'primary' for all others.
    - ``weight`` ('normal' or 'medium' or 'semibold' or 'bold'): Font weight override.
    - ``display`` ('inline' or 'block'): Display type. Silently overridden to 'block' when maxLines
      > 0 or hasCapsize is true.
    - ``as`` ('span' or 'p' or 'div' or 'label'): HTML element to render.
    - ``maxLines`` (number): Maximum lines before truncation. 0 means no truncation. When set, shows
      a tooltip on hover if content is truncated.
    - ``hasTruncateTooltip`` (boolean or 'above' or 'below' or 'start' or 'end'): Controls tooltip
      behavior for truncated text. true shows the tooltip at the default position, false
      disables it, or a placement string ('above' or 'below' or 'start' or 'end') sets a
      specific position.
    - ``wordBreak`` ('break-word' or 'break-all'): Word break behavior when truncating. Defaults to
      'break-all' for single-line truncation, 'break-word' otherwise.
    - ``textWrap`` ('wrap' or 'nowrap' or 'balance' or 'pretty'): Text wrapping behavior.
    - ``justify`` ('start' or 'center' or 'end'): Text alignment (justification). Uses logical
      values (start/end) for i18n/RTL compatibility.
    - ``hasCapsize`` (boolean): Enable optical alignment using text-box-trim. Forces block display.
    - ``hasStrikethrough`` (boolean): Apply strikethrough text decoration.
    - ``hasTabularNumbers`` (boolean): Use tabular (monospace) numbers for aligned numeric data.
    - ``id`` (string): HTML id attribute.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Text>.
    """

    def __init__(
        self,
        text: str,
        *,
        text_type: str | None = None,
        size: str | None = None,
        color: str | None = None,
        weight: str | None = None,
        display: str | None = None,
        max_lines: int | None = None,
        text_wrap: str | None = None,
        justify: str | None = None,
        tabular_numbers: bool | None = None,
        **props: Any,
    ) -> None:
        legacy_props = props.pop("props", None)
        extra_props = {**dict(legacy_props or {}), **props}
        super().__init__(
            "Text",
            text=text,
            props=_named_props(
                extra_props,
                type=text_type,
                size=size,
                color=color,
                weight=weight,
                display=display,
                maxLines=max_lines,
                textWrap=text_wrap,
                justify=justify,
                hasTabularNumbers=tabular_numbers,
            ),
        )


class Heading(Widget):
    """Render a semantic Astryx heading.

    Parameters
    ----------
    text : str
        Text content synchronized to the frontend component.
    level : int, default 3
        Heading level from 1 through 6.
    display_type : str | None, default None
        Optional Astryx display-scale type.
    color : str | None, default None
        Theme text color.
    max_lines : int | None, default None
        Maximum rendered lines before truncation.
    text_wrap : str | None, default None
        Text wrapping behavior.
    justify : str | None, default None
        Logical text alignment.
    **props : Any
        Additional JSON-safe Heading props forwarded to Astryx. The older
        ``props={...}`` mapping form remains supported.

    Astryx Props
    ------------
    JSON-safe Heading props forwarded to Astryx.

    Supported Astryx props include:

    - ``level`` (1 or 2 or 3 or 4 or 5 or 6; required): Heading level. Determines the semantic HTML
      element (h1-h6) and the visual styling from the theme (unless 'type' is set).
    - ``type`` ('display-1' or 'display-2' or 'display-3'): Display type variant. Overrides the
      visual styling from 'level' with display-scale sizing (larger, lighter weight, tighter
      line-height). The 'level' still determines the HTML element for accessibility. Use for
      hero banners, marketing headlines, and data callouts.
    - ``children`` (ReactNode; required): Heading content.
    - ``accessibilityLevel`` (1 or 2 or 3 or 4 or 5 or 6): Accessibility level override. When set
      and different from 'level', applies 'aria-level' so the document outline differs from the
      visual style.
    - ``color`` ('primary' or 'secondary' or 'disabled' or 'placeholder' or 'accent' or 'inherit'):
      Text color.
    - ``display`` ('inline' or 'block'): Display type. Silently overridden to 'block' when maxLines
      > 0 or hasCapsize is true.
    - ``maxLines`` (number): Maximum lines before truncation. 0 means no truncation. When set, shows
      a tooltip on hover if content is truncated.
    - ``hasTruncateTooltip`` (boolean or 'above' or 'below' or 'start' or 'end'): Controls tooltip
      behavior for truncated text. true shows the tooltip at the default position, false
      disables it, or a placement string ('above' or 'below' or 'start' or 'end') sets a
      specific position.
    - ``wordBreak`` ('break-word' or 'break-all'): Word break behavior when truncating. Defaults to
      'break-all' for single-line truncation, 'break-word' otherwise.
    - ``textWrap`` ('wrap' or 'nowrap' or 'balance' or 'pretty'): Text wrapping behavior.
    - ``justify`` ('start' or 'center' or 'end'): Text alignment (justification). Uses logical
      values (start/end) for i18n/RTL compatibility.
    - ``hasCapsize`` (boolean): Enable optical alignment using text-box-trim. Forces block display.
    - ``hasStrikethrough`` (boolean): Apply strikethrough text decoration.
    - ``id`` (string): HTML id attribute.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Heading>.
    """

    def __init__(
        self,
        text: str,
        *,
        level: int = 3,
        display_type: str | None = None,
        color: str | None = None,
        max_lines: int | None = None,
        text_wrap: str | None = None,
        justify: str | None = None,
        **props: Any,
    ) -> None:
        if not 1 <= level <= 6:
            raise ValueError("heading level must be between 1 and 6")
        legacy_props = props.pop("props", None)
        extra_props = {**dict(legacy_props or {}), **props}
        super().__init__(
            "Heading",
            text=text,
            props=_named_props(
                extra_props,
                level=level,
                type=display_type,
                color=color,
                maxLines=max_lines,
                textWrap=text_wrap,
                justify=justify,
            ),
        )


class Badge(Widget):
    """Render a compact status or category badge.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    variant : str, default 'neutral'
        Astryx visual variant.
    **props : Any
        JSON-safe Badge props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Badge props forwarded to Astryx.

    Supported Astryx props include:

    - ``variant`` ('neutral' or 'info' or 'success' or 'warning' or 'error' or 'blue' or 'cyan' or
      'green' or 'orange' or 'pink' or 'purple' or 'red' or 'teal' or 'yellow'): Visual style
      variant. Semantic variants (neutral, info, success, warning, error) use solid backgrounds.
      Non-semantic color variants use tinted backgrounds with colored text for categorization
      and tagging.
    - ``label`` (ReactNode): Badge text content.
    - ``icon`` (ReactNode): Optional leading icon.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Badge>.
    """

    def __init__(self, label: str, *, variant: str = "neutral", **props: Any) -> None:
        super().__init__("Badge", label=label, variant=variant, props=props)


class Button(Widget):
    """Render an Astryx push button.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    variant : str, default 'secondary'
        Astryx visual variant.
    disabled : bool, default False
        Whether the component should render disabled.
    size : str | None, default None
        Button size.
    loading : bool | None, default None
        Whether to show the loading state.
    tooltip : str | None, default None
        Hover tooltip text.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked for frontend activations.
    **props : Any
        JSON-safe Button props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Button props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessible label. Rendered as visible text by default; used as
      aria-label when isIconOnly is true.
    - ``variant`` ('primary' or 'secondary' or 'ghost' or 'destructive'): Visual style variant.
    - ``size`` ('sm' or 'md' or 'lg'): Size variant.
    - ``type`` ('button' or 'submit' or 'reset'): HTML button type attribute.
    - ``name`` (string): HTML name attribute for form submission.
    - ``value`` (string or number or readonly string[]): HTML value attribute for form submission.
    - ``form`` (string): Associates the button with a form element by ID.
    - ``isLoading`` (boolean): Shows a loading spinner and disables interaction. Announces "Loading"
      via a live region.
    - ``isInterruptible`` (boolean): Keep the button clickable while a clickAction is pending: the
      spinner and aria-busy still show, but the button is not disabled and the action is not
      deduped, so a re-click lands and interrupts the in-flight action with a fresh one.
    - ``isDisabled`` (boolean): Disables the button. When a tooltip is present, uses aria-disabled
      instead of native disabled so the button stays focusable.
    - ``icon`` (ReactNode): Icon element rendered before the label text.
    - ``isIconOnly`` (boolean): When true, renders as a square icon-only button with label as
      aria-label. Requires icon. Tip: for a dedicated icon-only button component, use IconButton
      from '@astryxdesign/core/IconButton' instead.
    - ``children`` (ReactNode): Optional override for visible text. When provided, displayed instead
      of label, but label is still required (it provides the accessible name). For most cases,
      just use label alone: <Button label="Save" />.
    - ``endContent`` (ReactElement<IconProps> or ReactElement<BadgeProps>): Trailing icon or badge
      rendered after the label. Ignored when isIconOnly is true. Color is inherited from the
      button variant.
    - ``tooltip`` (string): Tooltip text shown on hover.
    - ``onClick`` ((e: MouseEvent) => void): Standard click handler (passed through from
      ButtonHTMLAttributes).
    - ``clickAction`` ((e: MouseEvent) => void or Promise<void>): Async click handler. Shows loading
      state while the returned promise is pending.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Button>.
    """

    def __init__(
        self,
        label: str,
        *,
        variant: str = "secondary",
        disabled: bool = False,
        size: str | None = None,
        loading: bool | None = None,
        tooltip: str | None = None,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Button",
            label=label,
            variant=variant,
            disabled=disabled,
            callbacks=callbacks,
            props=_named_props(props, size=size, isLoading=loading, tooltip=tooltip),
        )


class IconButton(Widget):
    """Render an icon-only Astryx button.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    icon : str, default 'close'
        Astryx icon name.
    variant : str, default 'secondary'
        Astryx visual variant.
    disabled : bool, default False
        Whether the component should render disabled.
    size : str | None, default None
        Button size.
    loading : bool | None, default None
        Whether to show the loading state.
    tooltip : str | None, default None
        Hover tooltip text.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked for frontend activations.
    **props : Any
        JSON-safe IconButton props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe IconButton props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessible label. Used as aria-label (not rendered as visible
      text).
    - ``icon`` (ReactNode; required): Icon element rendered inside the button.
    - ``variant`` ('primary' or 'secondary' or 'ghost' or 'destructive'): Visual style variant.
    - ``size`` ('sm' or 'md' or 'lg'): Size variant.
    - ``isLoading`` (boolean): Shows a loading spinner and disables interaction.
    - ``isDisabled`` (boolean): Disables the button.
    - ``tooltip`` (string): Tooltip text shown on hover.
    - ``onClick`` ((e: MouseEvent) => void): Standard click handler.
    - ``clickAction`` ((e: MouseEvent) => void or Promise<void>): Async click handler with automatic
      loading state.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/IconButton>.
    """

    def __init__(
        self,
        label: str,
        *,
        icon: str = "close",
        variant: str = "secondary",
        disabled: bool = False,
        size: str | None = None,
        loading: bool | None = None,
        tooltip: str | None = None,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "IconButton",
            label=label,
            icon=icon,
            variant=variant,
            disabled=disabled,
            callbacks=callbacks,
            props=_named_props(
                props, icon=icon, size=size, isLoading=loading, tooltip=tooltip
            ),
        )


class ToggleButton(Widget):
    """Render a two-state Astryx toggle button.

    Parameters
    ----------
    value : bool, default False
        Synchronized component value.
    label : str
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the component should render disabled.
    size : str | None, default None
        Button size.
    loading : bool | None, default None
        Whether to show the loading state.
    tooltip : str | None, default None
        Hover tooltip text.
    **props : Any
        JSON-safe ToggleButton props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe ToggleButton props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessible label for the button. Used as visible text, or as
      aria-label for icon-only buttons.
    - ``isPressed`` (boolean): Whether the button is currently pressed. Ignored when inside a group.
    - ``onPressedChange`` ((isPressed: boolean, event: MouseEvent) => void): Called when pressed
      state should change. Receives the next state and the click event; call
      event.preventDefault() to skip pressedChangeAction. Ignored when inside a group.
    - ``pressedChangeAction`` ((isPressed: boolean) => void or Promise<void>): Action handler for
      API- or navigation-backed toggles, run in a transition. Shows an optimistic pressed state
      immediately and a spinner while pending; the button stays interruptible by re-clicks.
    - ``size`` ('sm' or 'md' or 'lg'): Button size. Defaults to group size when inside a group.
    - ``isDisabled`` (boolean): Whether the button is disabled.
    - ``isLoading`` (boolean): Whether the button shows a loading spinner.
    - ``icon`` (ReactNode): Icon element. When provided without children, button becomes icon-only
      with tooltip from label.
    - ``isIconOnly`` (boolean): When true, renders as a square icon-only button with 'label' as the
      aria-label and an automatic tooltip from the label.
    - ``pressedIcon`` (ReactNode): Icon shown when pressed. Falls back to icon if not provided.
    - ``children`` (ReactNode): Visible content. If omitted with icon, button becomes icon-only.
    - ``tooltip`` (string): Tooltip text shown on hover.
    - ``value`` (string): Value identifier when used inside ToggleButtonGroup. Required in groups.
    - ``data-testid`` (string): Test selector for automated testing frameworks.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/ToggleButton>.
    """

    def __init__(
        self,
        value: bool = False,
        *,
        label: str,
        disabled: bool = False,
        size: str | None = None,
        loading: bool | None = None,
        tooltip: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "ToggleButton",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(props, size=size, isLoading=loading, tooltip=tooltip),
        )


class TextInput(Widget):
    """Render a single-line Astryx text input.

    Parameters
    ----------
    value : str, default ''
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    placeholder : str, default ''
        Placeholder text shown when the control is empty.
    disabled : bool, default False
        Whether the component should render disabled.
    input_type : str | None, default None
        HTML text input type.
    size : str | None, default None
        Input size.
    label_hidden : bool | None, default None
        Whether to visually hide the accessible label.
    description : str | None, default None
        Helper text displayed with the input.
    optional : bool | None, default None
        Whether to mark the field optional.
    required : bool | None, default None
        Whether to mark the field required.
    loading : bool | None, default None
        Whether to show the loading state.
    status : Mapping[str, Any] | None, default None
        Validation status record.
    clear : bool | None, default None
        Whether to show a clear button.
    auto_focus : bool | None, default None
        Whether to focus the input when mounted.
    **props : Any
        JSON-safe TextInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe TextInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``type`` ('text' or 'password' or 'email'): The HTML input type.
    - ``label`` (string; required): Label text for the input: always rendered for accessibility.
    - ``value`` (string; required): Current value of the input.
    - ``onChange`` ((value: string, e: ChangeEvent<HTMLInputElement>) => void): Callback fired when
      the input value changes.
    - ``changeAction`` ((value: string, e: ChangeEvent<HTMLInputElement>) => void or Promise<void>):
      Async action fired after onChange (if not prevented). Triggers optimistic update and shows
      a loading spinner while pending.
    - ``size`` ('sm' or 'md' or 'lg'): Size variant of the input.
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
    - ``placeholder`` (string): Placeholder text shown when the input is empty.
    - ``labelTooltip`` (string): Tooltip text displayed in an info icon at the end of the label.
    - ``startIcon`` (IconType): SVG icon component displayed at the start of the input. See 'npx
      astryx docs icons' for valid semantic names.
    - ``status`` ({type: 'error' or 'warning' or 'success', message?: string}): Validation status:
      applies a colored border and status icon. If message is provided, displays a floating
      message below the input. Error type also sets aria-invalid.
    - ``hasClear`` (boolean): Shows a clear (x) button when the input has a value. Clicking it
      clears the value and returns focus to the input.
    - ``hasAutoFocus`` (boolean): Automatically focuses the input on mount.
    - ``htmlName`` (string): The HTML name attribute for the input, useful for form submissions.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/TextInput>.
    """

    def __init__(
        self,
        value: str = "",
        *,
        label: str = "",
        placeholder: str = "",
        disabled: bool = False,
        input_type: str | None = None,
        size: str | None = None,
        label_hidden: bool | None = None,
        description: str | None = None,
        optional: bool | None = None,
        required: bool | None = None,
        loading: bool | None = None,
        status: Mapping[str, Any] | None = None,
        clear: bool | None = None,
        auto_focus: bool | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "TextInput",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props,
                placeholder=placeholder,
                type=input_type,
                size=size,
                isLabelHidden=label_hidden,
                description=description,
                isOptional=optional,
                isRequired=required,
                isLoading=loading,
                status=status,
                hasClear=clear,
                hasAutoFocus=auto_focus,
            ),
        )


class TextArea(Widget):
    """Render a multiline Astryx text area.

    Parameters
    ----------
    value : str, default ''
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    placeholder : str, default ''
        Placeholder text shown when the control is empty.
    rows : int, default 3
        Rows or records rendered by the component.
    disabled : bool, default False
        Whether the component should render disabled.
    size : str | None, default None
        Text-area size.
    label_hidden : bool | None, default None
        Whether to visually hide the accessible label.
    description : str | None, default None
        Helper text displayed with the input.
    optional : bool | None, default None
        Whether to mark the field optional.
    required : bool | None, default None
        Whether to mark the field required.
    loading : bool | None, default None
        Whether to show the loading state.
    max_length : int | None, default None
        Maximum length used by the character counter.
    spell_check : bool | None, default None
        Whether browser spell checking is enabled.
    status : Mapping[str, Any] | None, default None
        Validation status record.
    **props : Any
        JSON-safe TextArea props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe TextArea props forwarded to Astryx.

    Supported Astryx props include:

    - ``ref`` (React.Ref<HTMLTextAreaElement>): Ref forwarded to the underlying <textarea> element.
    - ``label`` (string; required): Label text for the textarea. Always rendered for accessibility.
    - ``value`` (string; required): Current value of the textarea.
    - ``onChange`` ((value: string, e: ChangeEvent<HTMLTextAreaElement>) => void): Callback fired
      when the textarea value changes.
    - ``changeAction`` ((value: string, e: ChangeEvent<HTMLTextAreaElement>) => void or
      Promise<void>): Async action fired after onChange inside a React transition. Enables
      optimistic updates via useOptimistic.
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible to screen
      readers.
    - ``description`` (string): Helper text displayed between the label and textarea.
    - ``isOptional`` (boolean): Displays an "Optional" indicator next to the label. Mutually
      exclusive with isRequired.
    - ``isRequired`` (boolean): Displays a "Required" indicator next to the label and sets
      aria-required. Mutually exclusive with isOptional.
    - ``isDisabled`` (boolean): Disables the textarea, preventing interaction.
    - ``isLoading`` (boolean): Puts the textarea in a loading state, showing a spinner inside the
      input.
    - ``placeholder`` (string): Placeholder text shown when the textarea is empty.
    - ``rows`` (number): Number of visible text rows.
    - ``maxLength`` (number): Maximum number of characters allowed. When set, a character counter
      (current/max) is displayed below the textarea. Does not enforce the limit natively; the
      counter shows error styling when exceeded.
    - ``status`` ({ type: 'warning' or 'error' or 'success'; message?: string }): Status indicator
      that applies a colored border and icon. An optional message is displayed in a floating box
      below the textarea.
    - ``labelTooltip`` (string): Tooltip text displayed in an info icon at the end of the label.
    - ``startIcon`` (IconType): Icon component rendered inside the leading edge of the textarea
      wrapper. See 'npx astryx docs icons' for valid semantic names.
    - ``hasSpellCheck`` (boolean): Enables or disables browser spell checking.
    - ``hasAutoFocus`` (boolean): Automatically focuses the textarea on mount.
    - ``size`` ('sm' or 'md' or 'lg'): Size of the textarea, affecting internal padding. Height is
      controlled by rows, not size.
    - ``onPaste`` ((e: ClipboardEvent<HTMLTextAreaElement>) => void): Callback fired when content is
      pasted into the textarea.
    - ``htmlName`` (string): HTML name attribute for the textarea element, useful for form
      submissions.
    - ``onFocus`` ((e: FocusEvent<HTMLTextAreaElement>) => void): Callback fired when the textarea
      receives focus.
    - ``onBlur`` ((e: FocusEvent<HTMLTextAreaElement>) => void): Callback fired when the textarea
      loses focus.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/TextArea>.
    """

    def __init__(
        self,
        value: str = "",
        *,
        label: str = "",
        placeholder: str = "",
        rows: int = 3,
        disabled: bool = False,
        size: str | None = None,
        label_hidden: bool | None = None,
        description: str | None = None,
        optional: bool | None = None,
        required: bool | None = None,
        loading: bool | None = None,
        max_length: int | None = None,
        spell_check: bool | None = None,
        status: Mapping[str, Any] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "TextArea",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props,
                placeholder=placeholder,
                rows=rows,
                size=size,
                isLabelHidden=label_hidden,
                description=description,
                isOptional=optional,
                isRequired=required,
                isLoading=loading,
                maxLength=max_length,
                hasSpellCheck=spell_check,
                status=status,
            ),
        )


class NumberInput(Widget):
    """Render an Astryx numeric input.

    Parameters
    ----------
    value : int | float | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the component should render disabled.
    min : int | float | None, default None
        Minimum accepted value.
    max : int | float | None, default None
        Maximum accepted value.
    step : int | float | None, default None
        Numeric step increment.
    units : str | None, default None
        Units displayed after the value.
    size : str | None, default None
        Input size.
    placeholder : str | None, default None
        Placeholder text.
    integer_only : bool | None, default None
        Whether to accept only integer values.
    clear : bool | None, default None
        Whether to show a clear button.
    description : str | None, default None
        Helper text displayed with the input.
    status : Mapping[str, Any] | None, default None
        Validation status record.
    **props : Any
        JSON-safe NumberInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe NumberInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for the input (always rendered for accessibility).
    - ``value`` (number or null or undefined; required): Current value of the input.
    - ``onChange`` ((value: number) => void; required): Callback fired when input value changes
      (only on valid input).
    - ``size`` ('sm' or 'md' or 'lg'): Size variant.
    - ``isLabelHidden`` (boolean): Visually hide the label (still accessible to screen readers).
    - ``description`` (string): Description text displayed between the label and input.
    - ``isOptional`` (boolean): Whether the field is optional (mutually exclusive with isRequired).
    - ``isRequired`` (boolean): Whether the field is required (mutually exclusive with isOptional).
    - ``isDisabled`` (boolean): Whether the input is disabled.
    - ``placeholder`` (string): Placeholder text.
    - ``labelTooltip`` (string): Tooltip text to display in an info icon at the end of the label.
    - ``startIcon`` (IconType): Icon to display at the start of the input. See 'npx astryx docs
      icons' for valid semantic names.
    - ``labelIcon`` (IconType): Icon to display before the label text. See 'npx astryx docs icons'
      for valid semantic names.
    - ``status`` ({type: 'error' or 'warning' or 'success', message?: string}): Validation status
      with optional message.
    - ``min`` (number or null): Minimum value allowed.
    - ``max`` (number or null): Maximum value allowed.
    - ``step`` (number or null): Step increment for the input.
    - ``units`` (string or null): Units text to display at the end of the input (e.g., "%" or "GB").
    - ``isIntegerOnly`` (boolean): Only allow integer values (no floating point).
    - ``hasClear`` (boolean): Shows a clear (x) button when the input has a value. When true, the
      onChange callback also accepts null to signal the user cleared the input.
    - ``htmlName`` (string): HTML name attribute for form submissions.
    - ``autoComplete`` (string): HTML autocomplete attribute.
    - ``hasAutoFocus`` (boolean): Whether to focus the input on mount.
    - ``onFocus`` ((e: FocusEvent<HTMLInputElement>) => void): Callback fired when the input
      receives focus.
    - ``onBlur`` ((e: FocusEvent<HTMLInputElement>) => void): Callback fired when the input loses
      focus.
    - ``onEnter`` (() => void): Callback fired when the user presses the Enter key.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/NumberInput>.
    """

    def __init__(
        self,
        value: int | float | None = None,
        *,
        label: str = "",
        disabled: bool = False,
        min: int | float | None = None,
        max: int | float | None = None,
        step: int | float | None = None,
        units: str | None = None,
        size: str | None = None,
        placeholder: str | None = None,
        integer_only: bool | None = None,
        clear: bool | None = None,
        description: str | None = None,
        status: Mapping[str, Any] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "NumberInput",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props,
                min=min,
                max=max,
                step=step,
                units=units,
                size=size,
                placeholder=placeholder,
                isIntegerOnly=integer_only,
                hasClear=clear,
                description=description,
                status=status,
            ),
        )


class Slider(Widget):
    """Render an Astryx slider control.

    Parameters
    ----------
    value : int | float | tuple[int | float, int | float] | list[int | float], default 0
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the component should render disabled.
    min : int | float | None, default None
        Minimum slider value.
    max : int | float | None, default None
        Maximum slider value.
    step : int | float | None, default None
        Slider step increment.
    orientation : str | None, default None
        Horizontal or vertical orientation.
    value_display : str | None, default None
        Tooltip, text, or hidden value presentation.
    marks : Iterable[Mapping[str, Any]] | None, default None
        Optional slider tick-mark records.
    description : str | None, default None
        Helper text displayed with the slider.
    status : Mapping[str, Any] | None, default None
        Validation status record.
    **props : Any
        JSON-safe Slider props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Slider props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text (always rendered for accessibility).
    - ``value`` (number or [number, number]; required): Current value: a 'number' for single thumb
      mode or '[number, number]' for range mode.
    - ``onChange`` ((value: number) => void or (value: [number, number]) => void): Callback fired on
      value change during drag.
    - ``onChangeEnd`` ((value: number) => void or (value: [number, number]) => void): Callback fired
      when drag ends.
    - ``min`` (number): Minimum value.
    - ``max`` (number): Maximum value.
    - ``step`` (number): Step increment.
    - ``orientation`` ('horizontal' or 'vertical'): Orientation of the slider.
    - ``formatValue`` ((value: number) => string): Custom value formatting function used for display
      and 'aria-valuetext'.
    - ``valueDisplay`` ('tooltip' or 'text' or 'none'): How the current value is displayed.
    - ``marks`` (Array<{ value: number; label?: string }>): Tick marks at specified positions with
      optional labels.
    - ``minStepsBetweenThumbs`` (number): Minimum number of steps between thumbs in range mode;
      prevents thumbs from overlapping.
    - ``isDisabled`` (boolean): Whether the slider is disabled.
    - ``isOptional`` (boolean): Whether the field is optional.
    - ``isRequired`` (boolean): Whether the field is required.
    - ``isLabelHidden`` (boolean): Whether to visually hide the label.
    - ``description`` (string): Description text rendered below the label.
    - ``status`` (InputStatus): Status indicator object ('{ type, message }') for validation
      feedback.
    - ``labelTooltip`` (string): Tooltip text for an info icon displayed next to the label.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Slider>.
    """

    def __init__(
        self,
        value: int | float | tuple[int | float, int | float] | list[int | float] = 0,
        *,
        label: str = "",
        disabled: bool = False,
        min: int | float | None = None,
        max: int | float | None = None,
        step: int | float | None = None,
        orientation: str | None = None,
        value_display: str | None = None,
        marks: Iterable[Mapping[str, Any]] | None = None,
        description: str | None = None,
        status: Mapping[str, Any] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Slider",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props,
                min=min,
                max=max,
                step=step,
                orientation=orientation,
                valueDisplay=value_display,
                marks=list(marks) if marks is not None else None,
                description=description,
                status=status,
            ),
        )


class Checkbox(Widget):
    """Render an Astryx checkbox input.

    Parameters
    ----------
    value : bool, default False
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the component should render disabled.
    size : str | None, default None
        Checkbox size.
    label_hidden : bool | None, default None
        Whether to visually hide the accessible label.
    description : str | None, default None
        Helper text displayed below the label.
    loading : bool | None, default None
        Whether to show the loading state.
    read_only : bool | None, default None
        Whether interaction is disabled without dimming the value.
    status : Mapping[str, Any] | None, default None
        Validation status record.
    **props : Any
        JSON-safe CheckboxInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe CheckboxInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``ref`` (React.Ref<HTMLInputElement>): Ref forwarded to the underlying <input> element.
    - ``label`` (string; required): Label text for the checkbox (always rendered for accessibility).
    - ``isLabelHidden`` (boolean): Whether to visually hide the label (still accessible to screen
      readers).
    - ``description`` (string): Description text displayed below the label.
    - ``value`` (boolean or 'indeterminate'; required): Whether the checkbox is checked, unchecked,
      or indeterminate.
    - ``onChange`` ((checked: boolean, e: ChangeEvent<HTMLInputElement>) => void): Callback fired
      when the checkbox state changes.
    - ``changeAction`` ((checked: boolean, e: ChangeEvent<HTMLInputElement>) => void or
      Promise<void>): Async action on change. Fires after onChange if not prevented. Shows
      loading spinner while pending.
    - ``isLoading`` (boolean): Whether the checkbox is in a loading state. Shows spinner and
      prevents interaction.
    - ``isDisabled`` (boolean): Whether the checkbox is disabled.
    - ``isReadOnly`` (boolean): Whether the checkbox is read-only. Displays the current state at
      full opacity but prevents interaction. Unlike 'isDisabled', read-only checkboxes are not
      visually dimmed.
    - ``isOptional`` (boolean): Whether the field is optional. Mutually exclusive with isRequired.
    - ``isRequired`` (boolean): Whether the checkbox is required. Mutually exclusive with
      isOptional.
    - ``size`` ('sm' or 'md'): The size of the checkbox. sm for compact layouts, md for default.
    - ``onFocus`` ((e: FocusEvent<HTMLInputElement>) => void): Callback fired when the checkbox
      receives focus.
    - ``onBlur`` ((e: FocusEvent<HTMLInputElement>) => void): Callback fired when the checkbox loses
      focus.
    - ``labelIcon`` (IconType): Icon to display before the label text. See 'npx astryx docs icons'
      for valid semantic names.
    - ``status`` ({ type: 'error' or 'warning' or 'success', message: string }): Status indicator.
      Displays a colored message box below the checkbox and sets aria-invalid for errors.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/CheckboxInput>.
    """

    def __init__(
        self,
        value: bool = False,
        *,
        label: str = "",
        disabled: bool = False,
        size: str | None = None,
        label_hidden: bool | None = None,
        description: str | None = None,
        loading: bool | None = None,
        read_only: bool | None = None,
        status: Mapping[str, Any] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "CheckboxInput",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props,
                size=size,
                isLabelHidden=label_hidden,
                description=description,
                isLoading=loading,
                isReadOnly=read_only,
                status=status,
            ),
        )


class Switch(Widget):
    """Render an Astryx switch for binary settings.

    Parameters
    ----------
    value : bool, default False
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the component should render disabled.
    label_hidden : bool | None, default None
        Whether to visually hide the accessible label.
    description : str | None, default None
        Helper text displayed below the label.
    loading : bool | None, default None
        Whether to show the loading state.
    status : Mapping[str, Any] | None, default None
        Validation status record.
    label_position : str | None, default None
        Whether the label appears before or after the switch.
    label_spacing : str | None, default None
        Default or spread label spacing.
    **props : Any
        JSON-safe Switch props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Switch props forwarded to Astryx.

    Supported Astryx props include:

    - ``ref`` (React.Ref<HTMLInputElement>): Ref forwarded to the underlying <input> element.
    - ``label`` (string; required): Label text for the switch (always rendered for accessibility).
    - ``value`` (boolean; required): Whether the switch is on or off.
    - ``onChange`` ((checked: boolean, e: ChangeEvent<HTMLInputElement>) => void): Callback fired
      when the switch state changes.
    - ``changeAction`` ((checked: boolean, e: ChangeEvent<HTMLInputElement>) => void or
      Promise<void>): Async action fired after onChange. Triggers optimistic UI and shows a
      loading spinner until the promise resolves.
    - ``isLoading`` (boolean): Whether the switch is in a loading state, showing a spinner inside
      the thumb.
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible to screen
      readers.
    - ``description`` (string): Description text displayed below the label.
    - ``isDisabled`` (boolean): Whether the switch is disabled.
    - ``isOptional`` (boolean): Whether the field is optional. Mutually exclusive with isRequired.
    - ``isRequired`` (boolean): Whether the switch is required. Mutually exclusive with isOptional.
    - ``status`` (InputStatus): Status indicator with type and message. Displays a colored message
      box below the switch and sets aria-invalid when type is "error".
    - ``onFocus`` ((e: FocusEvent<HTMLInputElement>) => void): Callback fired when the switch
      receives focus.
    - ``onBlur`` ((e: FocusEvent<HTMLInputElement>) => void): Callback fired when the switch loses
      focus.
    - ``labelIcon`` (IconType): Icon displayed before the label text. See 'npx astryx docs icons'
      for valid semantic names.
    - ``labelTooltip`` (string): Tooltip text shown in an info icon at the end of the label.
    - ``labelPosition`` ('start' or 'end'): Which side of the switch the label appears on. "start"
      places the label before the switch.
    - ``labelSpacing`` ('default' or 'spread'): Spacing behavior between label and switch. "spread"
      pushes them to opposite ends of the container (full width).

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Switch>.
    """

    def __init__(
        self,
        value: bool = False,
        *,
        label: str = "",
        disabled: bool = False,
        label_hidden: bool | None = None,
        description: str | None = None,
        loading: bool | None = None,
        status: Mapping[str, Any] | None = None,
        label_position: str | None = None,
        label_spacing: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Switch",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props,
                isLabelHidden=label_hidden,
                description=description,
                isLoading=loading,
                status=status,
                labelPosition=label_position,
                labelSpacing=label_spacing,
            ),
        )


class Selector(Widget):
    """Render a single-value Astryx selector.

    Parameters
    ----------
    options : Iterable[Any] | Mapping[str, Any]
        Option records. Mappings, pairs, strings, and dictionaries are normalized.
    value : str | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the selector is disabled.
    placeholder : str | None, default None
        Placeholder shown when no option is selected.
    size : str | None, default None
        Selector size.
    clear : bool | None, default None
        Whether to show a clear button.
    search : bool | None, default None
        Whether to show option filtering.
    search_placeholder : str | None, default None
        Placeholder for the search input.
    label_hidden : bool | None, default None
        Whether to visually hide the accessible label.
    description : str | None, default None
        Helper text displayed with the selector.
    status : Mapping[str, Any] | None, default None
        Validation status record.
    **props : Any
        JSON-safe Selector props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Selector props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for accessibility.
    - ``options`` (SelectorOption[]; required): Array of items: strings, objects with
      value/label/icon/disabled, dividers ({type: "divider"}), or sections ({type: "section",
      title, items}).
    - ``value`` (string): Currently selected value.
    - ``onChange`` ((value: string) => void): Callback fired when the selection changes.
    - ``hasClear`` (boolean): Shows a clear (x) button when a value is selected. When true, onChange
      also accepts null to signal the user cleared the selection.
    - ``hasSearch`` (boolean): Whether to show a search input for filtering options.
    - ``searchPlaceholder`` (string): Placeholder text for the search input.
    - ``placeholder`` (string): Placeholder text shown when no value is selected.
    - ``size`` ('sm' or 'md' or 'lg'): Size variant for the selector.
    - ``isDisabled`` (boolean): Disables the selector.
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible.
    - ``description`` (string): Helper text displayed below the label.
    - ``isOptional`` (boolean): Marks the field as optional.
    - ``isRequired`` (boolean): Marks the field as required.
    - ``status`` ({type: 'error' or 'warning' or 'success', message?: string}): Validation status
      with an optional message.
    - ``renderOption`` ((option: SelectorOptionData) => ReactNode): Custom render function for each
      selectable option in the dropdown. Use this instead of JSX children; dividers and sections
      are rendered by the selector.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Selector>.
    """

    def __init__(
        self,
        options: Iterable[Any] | Mapping[str, Any],
        value: str | None = None,
        *,
        label: str = "",
        disabled: bool = False,
        placeholder: str | None = None,
        size: str | None = None,
        clear: bool | None = None,
        search: bool | None = None,
        search_placeholder: str | None = None,
        label_hidden: bool | None = None,
        description: str | None = None,
        status: Mapping[str, Any] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Selector",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props,
                options=_option_records(options),
                placeholder=placeholder,
                size=size,
                hasClear=clear,
                hasSearch=search,
                searchPlaceholder=search_placeholder,
                isLabelHidden=label_hidden,
                description=description,
                status=status,
            ),
        )


class MultiSelector(Widget):
    """Render an Astryx selector that accepts multiple values.

    Parameters
    ----------
    options : Iterable[Any] | Mapping[str, Any]
        Option records. Mappings, pairs, strings, and dictionaries are normalized.
    value : Iterable[str], default ()
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the selector is disabled.
    placeholder : str | None, default None
        Placeholder shown when no option is selected.
    size : str | None, default None
        Selector size.
    loading : bool | None, default None
        Whether to show the loading state.
    clear : bool | None, default None
        Whether to show a clear button.
    select_all : bool | None, default None
        Whether to show the select-all control.
    search : bool | None, default None
        Whether to show option filtering.
    trigger_display : str | None, default None
        Count, labels, or badges selection summary.
    max_badges : int | None, default None
        Maximum badges shown in the trigger.
    description : str | None, default None
        Helper text displayed with the selector.
    status : Mapping[str, Any] | None, default None
        Validation status record.
    **props : Any
        JSON-safe MultiSelector props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe MultiSelector props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for the multi-selector, always rendered for
      accessibility unless hidden visually.
    - ``isLabelHidden`` (boolean; default false): Visually hides the label while keeping it
      available to screen readers.
    - ``description`` (string): Helper text displayed between the label and selector.
    - ``isOptional`` (boolean; default false): Marks the field as optional; mutually exclusive with
      isRequired.
    - ``isRequired`` (boolean; default false): Marks the field as required; mutually exclusive with
      isOptional.
    - ``isDisabled`` (boolean; default false): Disables the selector.
    - ``options`` (option[]; required): Options displayed in the selector. Astryx accepts strings,
      option objects, dividers, and sections.
    - ``value`` (string[]; required): Selected option values.
    - ``onChange`` ((value: string[]) => void; required): Called when selected values change.
    - ``changeAction`` ((value: string[]) => void or Promise<void>): Async action fired after
      onChange.
    - ``isLoading`` (boolean; default false): Shows the selector loading state.
    - ``placeholder`` (string; default 'Select...'): Placeholder text when no value is selected.
    - ``size`` ('sm' or 'md' or 'lg'; default 'md'): Selector size.
    - ``status`` (MultiSelectorStatus): Validation status for warning, error, or success states.
    - ``width`` (number or string): Field width. Numbers are pixels; strings are used as CSS values.
    - ``labelTooltip`` (string): Tooltip text for an info icon at the end of the label.
    - ``startIcon`` (ReactNode or IconType): Icon displayed at the start of the trigger.
    - ``hasClear`` (boolean; default false): Shows a clear button when values are selected.
    - ``hasSelectAll`` (boolean; default false): Shows a select-all checkbox.
    - ``selectAllLabel`` (string; default 'Select all'): Label for the select-all checkbox.
    - ``hasSearch`` (boolean; default false): Shows a search input in the dropdown.
    - ``searchPlaceholder`` (string; default 'Search...'): Placeholder text for the search input.
    - ``triggerDisplay`` ('count' or 'labels' or 'badges'; default 'count'): Controls how selected
      items are summarized in the trigger.
    - ``maxBadges`` (number; default 3): Maximum visible badges before showing a +N summary.
    - ``renderOption`` ((option: MultiSelectorOptionData) => ReactNode): Custom render function for
      selectable options.
    - ``isDefaultOpen`` (boolean; default false): Opens the dropdown on mount, useful for previews.
    - ``data-testid`` (string): Test selector for automated testing.
    - ``xstyle`` (StyleXStyles): StyleX layout customization.
    - ``className`` (string): CSS class names for the root element.
    - ``style`` (CSSProperties): Inline styles for the root element.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/MultiSelector>.
    """

    def __init__(
        self,
        options: Iterable[Any] | Mapping[str, Any],
        value: Iterable[str] = (),
        *,
        label: str = "",
        disabled: bool = False,
        placeholder: str | None = None,
        size: str | None = None,
        loading: bool | None = None,
        clear: bool | None = None,
        select_all: bool | None = None,
        search: bool | None = None,
        trigger_display: str | None = None,
        max_badges: int | None = None,
        description: str | None = None,
        status: Mapping[str, Any] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "MultiSelector",
            label=label,
            value=list(value),
            disabled=disabled,
            props=_named_props(
                props,
                options=_option_records(options),
                placeholder=placeholder,
                size=size,
                isLoading=loading,
                hasClear=clear,
                hasSelectAll=select_all,
                hasSearch=search,
                triggerDisplay=trigger_display,
                maxBadges=max_badges,
                description=description,
                status=status,
            ),
        )


class DateInput(Widget):
    """Render an Astryx date input.

    Parameters
    ----------
    value : str | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the input is disabled.
    min : str | None, default None
        Minimum ISO date.
    max : str | None, default None
        Maximum ISO date.
    placeholder : str | None, default None
        Placeholder text.
    size : str | None, default None
        Input size.
    clear : bool | None, default None
        Whether to show a clear button.
    number_of_months : int | None, default None
        Number of calendar months to display.
    **props : Any
        JSON-safe DateInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe DateInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text.
    - ``isLabelHidden`` (boolean): Visually hide the label.
    - ``description`` (string): Helper text displayed below the label.
    - ``isOptional`` (boolean): Show an "(optional)" indicator next to the label.
    - ``isRequired`` (boolean): Mark the field as required.
    - ``isDisabled`` (boolean): Disable the input and calendar.
    - ``value`` (ISODateString): Selected date in YYYY-MM-DD format.
    - ``onChange`` ((value: ISODateString or undefined) => void): Callback invoked when the selected
      date changes.
    - ``changeAction`` ((value: ISODateString or undefined) => void or Promise<void>): Async action
      fired after onChange. Drives optimistic UI updates via useTransition.
    - ``isLoading`` (boolean): Whether the input is in a loading state. Disables interaction and
      shows a spinner.
    - ``min`` (ISODateString): Minimum selectable date (YYYY-MM-DD).
    - ``max`` (ISODateString): Maximum selectable date (YYYY-MM-DD).
    - ``dateConstraints`` (Array<(date: Date) => boolean>): Array of custom constraint functions
      that disable specific dates.
    - ``placeholder`` (string): Placeholder text shown in the text input.
    - ``size`` ('sm' or 'md' or 'lg'): Size of the input control.
    - ``status`` (InputStatus): Status indicator object for error, warning, or success states with a
      message.
    - ``labelTooltip`` (string): Tooltip text displayed via an info icon at the end of the label.
    - ``hasClear`` (boolean): Shows a clear (x) button when a date value is set. Clicking it clears
      the value and returns focus to the input.
    - ``numberOfMonths`` (1 or 2): Number of months displayed simultaneously in the calendar
      popover.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/DateInput>.
    """

    def __init__(
        self,
        value: str | None = None,
        *,
        label: str = "",
        disabled: bool = False,
        min: str | None = None,
        max: str | None = None,
        placeholder: str | None = None,
        size: str | None = None,
        clear: bool | None = None,
        number_of_months: int | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "DateInput",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props,
                min=min,
                max=max,
                placeholder=placeholder,
                size=size,
                hasClear=clear,
                numberOfMonths=number_of_months,
            ),
        )


class TimeInput(Widget):
    """Render an Astryx time input.

    Parameters
    ----------
    value : str | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the input is disabled.
    min : str | None, default None
        Minimum ISO time.
    max : str | None, default None
        Maximum ISO time.
    seconds : bool | None, default None
        Whether to include seconds.
    clear : bool | None, default None
        Whether to show a clear button.
    hour_format : str | None, default None
        Twelve- or twenty-four-hour display format.
    increment : int | None, default None
        Arrow-key minute increment.
    placeholder : str | None, default None
        Placeholder text.
    size : str | None, default None
        Input size.
    **props : Any
        JSON-safe TimeInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe TimeInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for the input (required for accessibility).
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible to screen
      readers.
    - ``description`` (string): Description text displayed between the label and input.
    - ``isOptional`` (boolean): Shows an "(optional)" indicator next to the label. Mutually
      exclusive with isRequired.
    - ``isRequired`` (boolean): Marks the field as required and sets aria-required. Mutually
      exclusive with isOptional.
    - ``isDisabled`` (boolean): Disables the input and suppresses interactions.
    - ``value`` (ISOTimeString): Controlled time value in ISO format (HH:MM or HH:MM:SS).
    - ``onChange`` ((value: ISOTimeString or undefined) => void): Callback fired when the time
      changes. Receives undefined when the input is cleared.
    - ``changeAction`` ((value: ISOTimeString or undefined) => void or Promise<void>): Async action
      fired after onChange. Wrapped in a React transition to provide optimistic UI; triggers the
      loading spinner while pending.
    - ``isLoading`` (boolean): Puts the input into a loading state, displaying a spinner.
    - ``min`` (ISOTimeString): Minimum selectable time in ISO format. Values outside the range are
      rejected.
    - ``max`` (ISOTimeString): Maximum selectable time in ISO format. Values outside the range are
      rejected.
    - ``hasSeconds`` (boolean): Includes seconds in the time display and parsing.
    - ``hasClear`` (boolean): Shows a clear button when a value is set and the input is not
      disabled.
    - ``hourFormat`` ('12h' or '24h'): Controls the display format. '12h' shows AM/PM (e.g. '2:30
      PM'); '24h' uses 24-hour notation (e.g. '14:30').
    - ``increment`` (number): Number of minutes to add or subtract when the user presses the up or
      down arrow key.
    - ``placeholder`` (string): Placeholder text shown when no time is selected. When the input is
      focused and empty, a format hint overrides this text.
    - ``size`` ('sm' or 'md' or 'lg'): Controls the height of the input element.
    - ``status`` (InputStatus): Status indicator that colors the border and displays an icon. When a
      message is provided it is rendered below the input.
    - ``labelTooltip`` (string): Tooltip text rendered as an info icon at the end of the label row.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/TimeInput>.
    """

    def __init__(
        self,
        value: str | None = None,
        *,
        label: str = "",
        disabled: bool = False,
        min: str | None = None,
        max: str | None = None,
        seconds: bool | None = None,
        clear: bool | None = None,
        hour_format: str | None = None,
        increment: int | None = None,
        placeholder: str | None = None,
        size: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "TimeInput",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props,
                min=min,
                max=max,
                hasSeconds=seconds,
                hasClear=clear,
                hourFormat=hour_format,
                increment=increment,
                placeholder=placeholder,
                size=size,
            ),
        )


class DateTimeInput(Widget):
    """Render an Astryx date-time input.

    Parameters
    ----------
    value : str | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the input is disabled.
    min : str | None, default None
        Minimum ISO datetime.
    max : str | None, default None
        Maximum ISO datetime.
    seconds : bool | None, default None
        Whether to include seconds.
    hour_format : str | None, default None
        Twelve- or twenty-four-hour display format.
    time_increment : int | None, default None
        Arrow-key minute increment.
    clear : bool | None, default None
        Whether to show a clear button.
    number_of_months : int | None, default None
        Number of calendar months to display.
    **props : Any
        JSON-safe DateTimeInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe DateTimeInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text.
    - ``isLabelHidden`` (boolean): Visually hide the label.
    - ``description`` (string): Helper text displayed below the label.
    - ``isOptional`` (boolean): Show an "(optional)" indicator next to the label.
    - ``isRequired`` (boolean): Mark the field as required.
    - ``isDisabled`` (boolean): Disable the input and picker.
    - ``value`` (ISODateTimeString): Selected datetime in ISO 8601 format (YYYY-MM-DDTHH:MM or
      YYYY-MM-DDTHH:MM:SS).
    - ``onChange`` ((value: ISODateTimeString or undefined) => void; required): Callback invoked
      when the selected datetime changes.
    - ``changeAction`` ((value: ISODateTimeString or undefined) => void or Promise<void>): Async
      action fired after onChange. Drives optimistic UI updates via useTransition.
    - ``isLoading`` (boolean): Whether the input is in a loading state. Disables interaction and
      shows a spinner.
    - ``min`` (ISODateTimeString): Minimum selectable datetime. Constrains both date and time
      selection.
    - ``max`` (ISODateTimeString): Maximum selectable datetime. Constrains both date and time
      selection.
    - ``dateConstraints`` (Array<(date: Date) => boolean>): Array of custom constraint functions
      that disable specific dates.
    - ``hasSeconds`` (boolean): Include seconds in the time portion.
    - ``hourFormat`` ('12h' or '24h'): Hour display format. '12h' shows AM/PM; '24h' uses 24-hour
      notation.
    - ``timeIncrement`` (number): Minutes to add or subtract when using arrow keys in the time
      input.
    - ``hasClear`` (boolean): Shows a clear button when a datetime value is set.
    - ``placeholder`` (string): Placeholder text shown in the date portion when no date is selected.
    - ``timePlaceholder`` (string): Placeholder text shown in the time portion when no time is
      selected.
    - ``timeLabel`` (string): Accessible label for the time portion. Defaults to "{label} time" so
      it is tied to the field label and localizable.
    - ``size`` ('sm' or 'md' or 'lg'): Size of the input control.
    - ``status`` (InputStatus): Status indicator object for error, warning, or success states with a
      message.
    - ``labelTooltip`` (string): Tooltip text displayed via an info icon at the end of the label.
    - ``numberOfMonths`` (1 or 2): Number of months displayed simultaneously in the calendar.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/DateTimeInput>.
    """

    def __init__(
        self,
        value: str | None = None,
        *,
        label: str = "",
        disabled: bool = False,
        min: str | None = None,
        max: str | None = None,
        seconds: bool | None = None,
        hour_format: str | None = None,
        time_increment: int | None = None,
        clear: bool | None = None,
        number_of_months: int | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "DateTimeInput",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props,
                min=min,
                max=max,
                hasSeconds=seconds,
                hourFormat=hour_format,
                timeIncrement=time_increment,
                hasClear=clear,
                numberOfMonths=number_of_months,
            ),
        )


class DateRangeInput(Widget):
    """Render an Astryx date-range input.

    Parameters
    ----------
    value : Mapping[str, str] | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the input is disabled.
    min : str | None, default None
        Minimum ISO date.
    max : str | None, default None
        Maximum ISO date.
    presets : Iterable[Mapping[str, Any]] | None, default None
        Named date-range presets.
    clear : bool | None, default None
        Whether to show a clear button.
    placeholder : str | None, default None
        Placeholder text.
    size : str | None, default None
        Input size.
    number_of_months : int | None, default None
        Number of calendar months to display.
    **props : Any
        JSON-safe DateRangeInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe DateRangeInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text.
    - ``isLabelHidden`` (boolean): Visually hide the label.
    - ``description`` (string): Helper text displayed below the label.
    - ``isOptional`` (boolean): Show an "(optional)" indicator.
    - ``isRequired`` (boolean): Mark the field as required.
    - ``isDisabled`` (boolean): Disable the trigger and picker.
    - ``value`` (DateRange or null; required): Selected date range ({start, end} in ISO format), or
      null.
    - ``onChange`` ((value: DateRange or null) => void; required): Callback when the range changes.
      Called with null on clear.
    - ``changeAction`` ((value: DateRange or null) => void or Promise<void>): Async action fired
      after onChange. Drives optimistic UI updates via useTransition.
    - ``isLoading`` (boolean): Whether the input is in a loading state. Disables interaction and
      shows a spinner.
    - ``min`` (ISODateString): Minimum selectable date.
    - ``max`` (ISODateString): Maximum selectable date.
    - ``dateConstraints`` (Array<(date: Date) => boolean>): Custom constraint functions to disable
      specific dates.
    - ``presets`` (Array<DateRangePreset>): Preset ranges shown as quick-select options beside the
      calendar.
    - ``hasClear`` (boolean): Shows a clear button when a range is selected.
    - ``placeholder`` (string): Placeholder text when no range is selected.
    - ``size`` ('sm' or 'md' or 'lg'): Size of the trigger.
    - ``status`` (InputStatus): Status indicator for error, warning, or success states.
    - ``labelTooltip`` (string): Tooltip text via info icon at label end.
    - ``numberOfMonths`` (1 or 2): Number of months in the calendar.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/DateRangeInput>.
    """

    def __init__(
        self,
        value: Mapping[str, str] | None = None,
        *,
        label: str = "",
        disabled: bool = False,
        min: str | None = None,
        max: str | None = None,
        presets: Iterable[Mapping[str, Any]] | None = None,
        clear: bool | None = None,
        placeholder: str | None = None,
        size: str | None = None,
        number_of_months: int | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "DateRangeInput",
            label=label,
            value=value,
            disabled=disabled,
            props=_named_props(
                props,
                min=min,
                max=max,
                presets=list(presets) if presets is not None else None,
                hasClear=clear,
                placeholder=placeholder,
                size=size,
                numberOfMonths=number_of_months,
            ),
        )
