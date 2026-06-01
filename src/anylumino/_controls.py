from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date
from datetime import datetime
from datetime import time
from inspect import Parameter
from inspect import Signature
from pathlib import Path
from typing import Any

import anywidget
import traitlets as t


PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"


def _load_static(filename: str) -> str:
    return (STATIC_DIR / filename).read_text()


def _json_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (date, time)):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value


def _options_tuple(options: Iterable[Any] | None) -> tuple[Any, ...]:
    if options is None:
        return ()
    if isinstance(options, dict):
        return tuple((str(label), _json_value(value)) for label, value in options.items())
    return tuple(_json_value(option) for option in options)


def _range_value(value: Any, min_value: int | float, max_value: int | float) -> list[Any]:
    if value is None:
        return [min_value, max_value]
    return list(_json_value(value))


class ControlWidget(anywidget.AnyWidget):
    """Base class for portable anylumino controls.

    Controls are anywidget-native and render browser controls styled with
    Web Awesome-inspired tokens and component structure. They do not use the
    classic Jupyter controls frontend.
    """

    _esm = _load_static("control_widget.js")
    _css = _load_static("control_widget.css")

    control_kind = t.Unicode("text").tag(sync=True)
    value = t.Any(None, allow_none=True).tag(sync=True)
    description = t.Unicode("").tag(sync=True)
    placeholder = t.Unicode("").tag(sync=True)
    disabled = t.Bool(False).tag(sync=True)
    continuous_update = t.Bool(True).tag(sync=True)
    options = t.Tuple(default_value=()).tag(sync=True)
    index = t.Any(None, allow_none=True).tag(sync=True)
    min = t.Any(None, allow_none=True).tag(sync=True)
    max = t.Any(None, allow_none=True).tag(sync=True)
    step = t.Any(None, allow_none=True).tag(sync=True)
    base = t.Float(10.0).tag(sync=True)
    orientation = t.Unicode("horizontal").tag(sync=True)
    readout = t.Bool(True).tag(sync=True)
    readout_format = t.Unicode("").tag(sync=True)
    rows = t.Int(4, allow_none=True).tag(sync=True)
    button_style = t.Unicode("").tag(sync=True)
    icon = t.Unicode("").tag(sync=True)
    icon_family = t.Unicode("classic").tag(sync=True)
    icon_variant = t.Unicode("solid").tag(sync=True)
    icon_library = t.Unicode("default").tag(sync=True)
    icons = t.Any(None, allow_none=True).tag(sync=True)
    tooltips = t.Any(None, allow_none=True).tag(sync=True)
    tooltip = t.Unicode("").tag(sync=True)
    allowed_tags = t.Any(None, allow_none=True).tag(sync=True)
    allow_duplicates = t.Bool(False).tag(sync=True)
    ensure_option = t.Bool(False).tag(sync=True)
    concise = t.Bool(False).tag(sync=True)
    indent = t.Bool(True).tag(sync=True)
    accept = t.Unicode("").tag(sync=True)
    multiple = t.Bool(False).tag(sync=True)
    format = t.Unicode("").tag(sync=True)
    width = t.Unicode("").tag(sync=True)
    height = t.Unicode("").tag(sync=True)
    html = t.Bool(False).tag(sync=True)
    autoplay = t.Bool(False).tag(sync=True)
    controls = t.Bool(True).tag(sync=True)
    loop = t.Bool(False).tag(sync=True)

    def __init__(self, **kwargs: Any) -> None:
        callbacks = kwargs.pop("callbacks", None)
        if "options" in kwargs:
            kwargs["options"] = _options_tuple(kwargs["options"])
        if "value" in kwargs:
            kwargs["value"] = _json_value(kwargs["value"])
        for name in ("min", "max"):
            if name in kwargs:
                kwargs[name] = _json_value(kwargs[name])
        self._click_callbacks: list[Callable[[ControlWidget], None]] = []
        super().__init__(**kwargs)
        self.on_msg(self._handle_frontend_message)
        if callbacks is not None:
            for callback in callbacks:
                self.on_click(callback)

    def on_click(
        self,
        callback: Callable[[ControlWidget], None],
        remove: bool = False,
    ) -> None:
        """Register or unregister a callback for button-like activations."""
        if remove:
            self._click_callbacks = [item for item in self._click_callbacks if item is not callback]
            return
        self._click_callbacks.append(callback)

    def _handle_frontend_message(self, _widget: object, content: dict[str, Any], _buffers: object) -> None:
        if content.get("type") != "click":
            return
        for callback in list(self._click_callbacks):
            callback(self)


class Text(ControlWidget):
    """Single-line text input control.

    Parameters
    ----------
    value : str, optional
        Initial value and synced Python value.
    description : str, optional
        Label shown above the control.
    placeholder : str, optional
        Empty-state text inside the input.
    disabled : bool, optional
        Whether user interaction is disabled.
    continuous_update : bool, optional
        Whether Python receives updates while the user is typing.
    """

    def __init__(
        self,
        value: str = "",
        description: str = "",
        placeholder: str = "",
        disabled: bool = False,
        continuous_update: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="text",
            value=value,
            description=description,
            placeholder=placeholder,
            disabled=disabled,
            continuous_update=continuous_update,
            **kwargs,
        )


class Textarea(ControlWidget):
    """Multiline text input control.

    Parameters
    ----------
    value : str, optional
        Initial value and synced Python value.
    description : str, optional
        Label shown above the control.
    placeholder : str, optional
        Empty-state text inside the input.
    rows : int, optional
        Visible row count.
    disabled : bool, optional
        Whether user interaction is disabled.
    continuous_update : bool, optional
        Whether Python receives updates while the user is typing.
    """

    def __init__(
        self,
        value: str = "",
        description: str = "",
        placeholder: str = "",
        rows: int = 4,
        disabled: bool = False,
        continuous_update: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="textarea",
            value=value,
            description=description,
            placeholder=placeholder,
            rows=rows,
            disabled=disabled,
            continuous_update=continuous_update,
            **kwargs,
        )


class Password(Text):
    """Password text input control."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.control_kind = "password"


class Combobox(Text):
    """Text input with dropdown suggestions."""

    def __init__(
        self,
        value: str = "",
        options: Iterable[Any] = (),
        description: str = "",
        placeholder: str = "",
        ensure_option: bool = False,
        disabled: bool = False,
        continuous_update: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            description=description,
            placeholder=placeholder,
            disabled=disabled,
            continuous_update=continuous_update,
            options=options,
            ensure_option=ensure_option,
            **kwargs,
        )
        self.control_kind = "combobox"


class TagsInput(ControlWidget):
    """List input for string tags."""

    def __init__(
        self,
        value: Iterable[Any] = (),
        allowed_tags: Iterable[Any] | None = None,
        allow_duplicates: bool = False,
        description: str = "",
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="tags",
            value=list(value),
            allowed_tags=list(allowed_tags) if allowed_tags is not None else None,
            allow_duplicates=allow_duplicates,
            description=description,
            disabled=disabled,
            **kwargs,
        )


class ColorsInput(TagsInput):
    """List input for color tags."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.control_kind = "colors"


class FloatsInput(TagsInput):
    """List input for float values."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.control_kind = "floats"


class IntsInput(TagsInput):
    """List input for integer values."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.control_kind = "ints"


class Dropdown(ControlWidget):
    """Dropdown selection control."""

    def __init__(
        self,
        options: Iterable[Any] = (),
        value: Any = None,
        index: int | None = None,
        description: str = "",
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        option_tuple = _options_tuple(options)
        if value is None and index is not None and option_tuple:
            value = _option_value(option_tuple[index])
        super().__init__(
            control_kind="dropdown",
            options=option_tuple,
            value=value,
            index=index,
            description=description,
            disabled=disabled,
            **kwargs,
        )


class RadioButtons(Dropdown):
    """Radio-button selection control."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.control_kind = "radio"


class ToggleButtons(Dropdown):
    """Segmented toggle-button selection control."""

    def __init__(
        self,
        options: Iterable[Any] = (),
        value: Any = None,
        index: int | None = None,
        description: str = "",
        disabled: bool = False,
        button_style: str = "",
        tooltips: Iterable[str] | None = None,
        icons: Iterable[str | dict[str, Any]] | None = None,
        icon_family: str = "classic",
        icon_variant: str = "solid",
        icon_library: str = "default",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            options=options,
            value=value,
            index=index,
            description=description,
            disabled=disabled,
            button_style=button_style,
            tooltips=list(tooltips) if tooltips is not None else None,
            icons=list(icons) if icons is not None else None,
            icon_family=icon_family,
            icon_variant=icon_variant,
            icon_library=icon_library,
            **kwargs,
        )
        self.control_kind = "toggle-buttons"


class Select(Dropdown):
    """List-box single-selection control."""

    def __init__(self, rows: int = 5, **kwargs: Any) -> None:
        super().__init__(rows=rows, **kwargs)
        self.control_kind = "select"


class SelectMultiple(Dropdown):
    """List-box multi-selection control."""

    def __init__(
        self,
        options: Iterable[Any] = (),
        value: Iterable[Any] = (),
        rows: int = 5,
        description: str = "",
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            options=options,
            value=list(value),
            rows=rows,
            description=description,
            disabled=disabled,
            **kwargs,
        )
        self.control_kind = "select-multiple"


class SelectionSlider(Dropdown):
    """Slider selection control."""

    def __init__(
        self,
        options: Iterable[Any] = (),
        value: Any = None,
        index: int | None = None,
        description: str = "",
        disabled: bool = False,
        orientation: str = "horizontal",
        readout: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            options=options,
            value=value,
            index=index,
            description=description,
            disabled=disabled,
            orientation=orientation,
            readout=readout,
            **kwargs,
        )
        self.control_kind = "selection-slider"


class SelectionRangeSlider(SelectionSlider):
    """Range slider selection control."""

    def __init__(
        self,
        options: Iterable[Any] = (),
        value: Iterable[Any] | None = None,
        index: Iterable[int] | None = None,
        **kwargs: Any,
    ) -> None:
        option_tuple = _options_tuple(options)
        if value is None and index is not None and option_tuple:
            index_list = list(index)
            value = [_option_value(option_tuple[index_list[0]]), _option_value(option_tuple[index_list[1]])]
        super().__init__(options=option_tuple, value=list(value or []), index=index, **kwargs)
        self.control_kind = "selection-range-slider"


class Button(ControlWidget):
    """Clickable button control."""

    def __init__(
        self,
        description: str = "",
        icon: str = "",
        disabled: bool = False,
        button_style: str = "",
        tooltip: str = "",
        icon_family: str = "classic",
        icon_variant: str = "solid",
        icon_library: str = "default",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="button",
            description=description,
            icon=icon,
            disabled=disabled,
            button_style=button_style,
            tooltip=tooltip,
            icon_family=icon_family,
            icon_variant=icon_variant,
            icon_library=icon_library,
            **kwargs,
        )


class Checkbox(ControlWidget):
    """Boolean checkbox control."""

    def __init__(
        self,
        value: bool = False,
        description: str = "",
        disabled: bool = False,
        indent: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="checkbox",
            value=value,
            description=description,
            disabled=disabled,
            indent=indent,
            **kwargs,
        )


class ToggleButton(Checkbox):
    """Boolean toggle-button control."""

    def __init__(
        self,
        value: bool = False,
        description: str = "",
        icon: str = "",
        disabled: bool = False,
        button_style: str = "",
        tooltip: str = "",
        icon_family: str = "classic",
        icon_variant: str = "solid",
        icon_library: str = "default",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            description=description,
            disabled=disabled,
            icon=icon,
            button_style=button_style,
            tooltip=tooltip,
            icon_family=icon_family,
            icon_variant=icon_variant,
            icon_library=icon_library,
            **kwargs,
        )
        self.control_kind = "toggle"


class Valid(Checkbox):
    """Boolean validity indicator control."""

    def __init__(self, value: bool = False, description: str = "", readout: str = "", **kwargs: Any) -> None:
        super().__init__(value=value, description=description, **kwargs)
        self.control_kind = "valid"
        self.placeholder = readout


class IntSlider(ControlWidget):
    """Integer slider control."""

    def __init__(
        self,
        value: int = 0,
        min: int = 0,
        max: int = 100,
        step: int = 1,
        description: str = "",
        disabled: bool = False,
        continuous_update: bool = True,
        orientation: str = "horizontal",
        readout: bool = True,
        readout_format: str = "d",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="int-slider",
            value=value,
            min=min,
            max=max,
            step=step,
            description=description,
            disabled=disabled,
            continuous_update=continuous_update,
            orientation=orientation,
            readout=readout,
            readout_format=readout_format,
            **kwargs,
        )


class IntRangeSlider(IntSlider):
    """Integer range slider control."""

    def __init__(
        self,
        value: Iterable[int] | None = None,
        min: int = 0,
        max: int = 100,
        step: int = 1,
        **kwargs: Any,
    ) -> None:
        super().__init__(value=_range_value(value, min, max), min=min, max=max, step=step, **kwargs)
        self.control_kind = "int-range-slider"


class IntText(ControlWidget):
    """Integer text input control."""

    def __init__(
        self,
        value: int = 0,
        description: str = "",
        disabled: bool = False,
        continuous_update: bool = True,
        min: int | float | None = None,
        max: int | float | None = None,
        step: int | float | str = 1,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="int-text",
            value=value,
            description=description,
            disabled=disabled,
            continuous_update=continuous_update,
            min=min,
            max=max,
            step=step,
            **kwargs,
        )


class BoundedIntText(IntText):
    """Bounded integer text input control."""

    def __init__(self, value: int = 0, min: int = 0, max: int = 100, step: int = 1, **kwargs: Any) -> None:
        super().__init__(value=value, min=min, max=max, step=step, **kwargs)
        self.control_kind = "bounded-int-text"


class FloatSlider(IntSlider):
    """Float slider control."""

    def __init__(
        self,
        value: float = 0.0,
        min: float = 0.0,
        max: float = 100.0,
        step: float = 0.1,
        readout_format: str = ".2f",
        **kwargs: Any,
    ) -> None:
        super().__init__(value=value, min=min, max=max, step=step, readout_format=readout_format, **kwargs)
        self.control_kind = "float-slider"


class FloatRangeSlider(FloatSlider):
    """Float range slider control."""

    def __init__(
        self,
        value: Iterable[float] | None = None,
        min: float = 0.0,
        max: float = 100.0,
        step: float = 0.1,
        **kwargs: Any,
    ) -> None:
        super().__init__(value=_range_value(value, min, max), min=min, max=max, step=step, **kwargs)
        self.control_kind = "float-range-slider"


class FloatLogSlider(FloatSlider):
    """Logarithmic float slider control."""

    def __init__(
        self,
        value: float = 1.0,
        base: float = 10.0,
        min: float = 0.0,
        max: float = 4.0,
        step: float = 0.1,
        readout_format: str = ".3g",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            base=base,
            min=min,
            max=max,
            step=step,
            readout_format=readout_format,
            **kwargs,
        )
        self.control_kind = "float-log-slider"


class FloatText(IntText):
    """Float text input control."""

    def __init__(self, value: float = 0.0, **kwargs: Any) -> None:
        kwargs.setdefault("step", "any")
        super().__init__(value=value, **kwargs)
        self.control_kind = "float-text"


class BoundedFloatText(FloatText):
    """Bounded float text input control."""

    def __init__(
        self,
        value: float = 0.0,
        min: float = 0.0,
        max: float = 100.0,
        step: float = 0.1,
        **kwargs: Any,
    ) -> None:
        super().__init__(value=value, min=min, max=max, step=step, **kwargs)
        self.control_kind = "bounded-float-text"


class IntProgress(IntSlider):
    """Integer progress bar control."""

    def __init__(self, value: int = 0, min: int = 0, max: int = 100, bar_style: str = "", **kwargs: Any) -> None:
        super().__init__(value=value, min=min, max=max, button_style=bar_style, **kwargs)
        self.control_kind = "int-progress"


class FloatProgress(FloatSlider):
    """Float progress bar control."""

    def __init__(
        self,
        value: float = 0.0,
        min: float = 0.0,
        max: float = 100.0,
        bar_style: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(value=value, min=min, max=max, button_style=bar_style, **kwargs)
        self.control_kind = "float-progress"


class Play(IntSlider):
    """Playback stepper control."""

    def __init__(self, interval: int = 100, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.control_kind = "play"
        self.rows = interval


class DatePicker(ControlWidget):
    """Date picker control."""

    def __init__(self, value: Any = None, description: str = "", disabled: bool = False, **kwargs: Any) -> None:
        super().__init__(
            control_kind="date",
            value=_json_value(value),
            description=description,
            disabled=disabled,
            **kwargs,
        )


class TimePicker(DatePicker):
    """Time picker control.

    The frontend renders a time input with an anylumino popup picker. The popup
    presents hours and minutes in separate columns, allowing per-minute
    selection rather than fixed 15-minute increments. ``datetime.time`` values
    are serialized with ``isoformat()`` before syncing to the frontend.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.control_kind = "time"


class DatetimePicker(DatePicker):
    """Datetime picker control.

    The frontend renders separate date and time inputs. The time input uses the
    same hour/minute popup as :class:`TimePicker`, so users can pick any minute
    value. ``datetime.datetime`` values are serialized with ``isoformat()``
    before syncing to the frontend.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.control_kind = "datetime"


class ColorPicker(DatePicker):
    """Color picker control."""

    def __init__(self, value: str = "black", concise: bool = False, **kwargs: Any) -> None:
        super().__init__(value=value, concise=concise, **kwargs)
        self.control_kind = "color"


class FileUpload(Button):
    """File upload control.

    The synced value contains file metadata dictionaries with ``name``,
    ``size`` and ``type`` fields. File bytes are intentionally not synced in
    this portable first implementation.
    """

    def __init__(
        self,
        accept: str = "",
        multiple: bool = False,
        disabled: bool = False,
        description: str = "Upload",
        icon: str = "upload",
        icon_family: str = "classic",
        icon_variant: str = "solid",
        icon_library: str = "default",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            description=description,
            icon=icon,
            disabled=disabled,
            accept=accept,
            multiple=multiple,
            value=[],
            icon_family=icon_family,
            icon_variant=icon_variant,
            icon_library=icon_library,
            **kwargs,
        )
        self.control_kind = "file"


class Image(ControlWidget):
    """Image display widget."""

    def __init__(
        self,
        value: str | bytes = "",
        format: str = "png",
        width: str = "",
        height: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="image",
            value=value if isinstance(value, str) else "",
            format=format,
            width=width,
            height=height,
            **kwargs,
        )


class Audio(Image):
    """Audio display widget."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.control_kind = "audio"


class Video(Image):
    """Video display widget."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.control_kind = "video"


class HTML(ControlWidget):
    """HTML display widget."""

    def __init__(self, value: str = "", description: str = "", **kwargs: Any) -> None:
        super().__init__(control_kind="html", value=value, description=description, html=True, **kwargs)


class HTMLMath(HTML):
    """HTML and math display widget."""


class Label(ControlWidget):
    """Plain text label widget."""

    def __init__(self, value: str = "", description: str = "", **kwargs: Any) -> None:
        super().__init__(control_kind="label", value=value, description=description, **kwargs)


class Output(ControlWidget):
    """Simple output display widget."""

    def __init__(self, value: str = "", **kwargs: Any) -> None:
        super().__init__(control_kind="output", value=value, **kwargs)

    def append_stdout(self, text: str) -> None:
        self.value = f"{self.value or ''}{text}"

    def append_stderr(self, text: str) -> None:
        self.append_stdout(text)

    def clear_output(self, *_args: Any, **_kwargs: Any) -> None:
        self.value = ""


def _option_value(option: Any) -> Any:
    if isinstance(option, (list, tuple)) and len(option) == 2:
        return option[1]
    return option


TextInput = Text
TextArea = Textarea
PasswordInput = Password
ListBox = Select
MultiSelect = SelectMultiple
IntegerInput = IntText
IntegerSlider = IntSlider
IntegerRangeSlider = IntRangeSlider


_REQUIRED = object()


def _parameter(name: str, default: object = None) -> Parameter:
    if default is _REQUIRED:
        return Parameter(name, Parameter.POSITIONAL_OR_KEYWORD)
    return Parameter(name, Parameter.POSITIONAL_OR_KEYWORD, default=default)


def _signature(parameters: list[tuple[str, object]]) -> Signature:
    return Signature([_parameter(name, default) for name, default in parameters])


def _doc(summary: str, parameters: list[tuple[str, object]]) -> str:
    lines = [summary, "", "Parameters", "----------"]
    for name, _default in parameters:
        lines.append(f"{name} : optional")
        lines.append(f"    {_CONTROL_PARAM_DOCS.get(name, 'Control option.')}")
    return "\n".join(lines)


def _document_control(cls: type, summary: str, parameters: list[tuple[str, object]]) -> None:
    cls.__signature__ = _signature(parameters)
    cls.__doc__ = _doc(summary, parameters)


_CONTROL_PARAM_DOCS = {
    "accept": "Accepted file extensions or MIME types.",
    "allow_duplicates": "Whether duplicate entries are allowed.",
    "allowed_tags": "Optional allowed values for tag-style inputs.",
    "bar_style": "Progress-bar style name such as ``'success'`` or ``'warning'``.",
    "base": "Logarithm base for logarithmic sliders.",
    "button_style": "Visual variant such as ``'primary'``, ``'success'``, or ``'danger'``.",
    "concise": "Whether to use a compact color-picker display.",
    "continuous_update": "Whether Python receives updates while the user is typing or dragging.",
    "description": "Label shown above the control.",
    "disabled": "Whether user interaction is disabled.",
    "ensure_option": "Whether combobox values must be present in ``options``.",
    "format": "Media format such as ``'png'``, ``'mp3'``, or ``'mp4'``.",
    "height": "CSS height for media widgets.",
    "icon": "Web Awesome icon name.",
    "icon_family": "Web Awesome icon family, for example ``'classic'``.",
    "icon_library": "Web Awesome icon library, for example ``'default'``.",
    "icon_variant": "Web Awesome icon variant, for example ``'solid'`` or ``'regular'``.",
    "icons": "Web Awesome icon names or per-option icon dictionaries for toggle-button options.",
    "indent": "Whether checkbox labels are indented.",
    "index": "Selected option index.",
    "interval": "Delay between play-widget ticks in milliseconds.",
    "max": "Maximum numeric, date, or time value.",
    "min": "Minimum numeric, date, or time value.",
    "multiple": "Whether multiple files can be selected.",
    "options": "Selectable values or ``(label, value)`` pairs.",
    "orientation": "``'horizontal'`` or ``'vertical'``.",
    "placeholder": "Text shown while the input is empty.",
    "readout": "Whether to show the current value.",
    "readout_format": "Format string used for slider readouts.",
    "rows": "Visible row count.",
    "step": "Increment size.",
    "tooltips": "Per-option tooltips.",
    "tooltip": "Hover text.",
    "value": "Initial value and synced Python value.",
    "width": "CSS width for media widgets.",
}


_TEXT_PARAMS = [
    ("value", ""),
    ("description", ""),
    ("placeholder", ""),
    ("disabled", False),
    ("continuous_update", True),
]
_TEXTAREA_PARAMS = [*_TEXT_PARAMS, ("rows", 4)]
_SELECTION_PARAMS = [
    ("options", ()),
    ("value", None),
    ("index", None),
    ("description", ""),
    ("disabled", False),
]
_BUTTON_PARAMS = [
    ("description", ""),
    ("icon", ""),
    ("disabled", False),
    ("button_style", ""),
    ("tooltip", ""),
    ("icon_family", "classic"),
    ("icon_variant", "solid"),
    ("icon_library", "default"),
]
_CHECKBOX_PARAMS = [
    ("value", False),
    ("description", ""),
    ("disabled", False),
    ("indent", True),
]
_INT_SLIDER_PARAMS = [
    ("value", 0),
    ("min", 0),
    ("max", 100),
    ("step", 1),
    ("description", ""),
    ("disabled", False),
    ("continuous_update", True),
    ("orientation", "horizontal"),
    ("readout", True),
    ("readout_format", "d"),
]
_FLOAT_SLIDER_PARAMS = [
    ("value", 0.0),
    ("min", 0.0),
    ("max", 100.0),
    ("step", 0.1),
    ("description", ""),
    ("disabled", False),
    ("continuous_update", True),
    ("orientation", "horizontal"),
    ("readout", True),
    ("readout_format", ".2f"),
]
_TAG_PARAMS = [
    ("value", ()),
    ("allowed_tags", None),
    ("allow_duplicates", False),
    ("description", ""),
    ("disabled", False),
]

for _cls, _summary, _params in [
    (Text, "Single-line text input control.", _TEXT_PARAMS),
    (Textarea, "Multiline text input control.", _TEXTAREA_PARAMS),
    (Password, "Password text input control.", _TEXT_PARAMS),
    (Combobox, "Text input with dropdown suggestions.", [*_TEXT_PARAMS, ("options", ()), ("ensure_option", False)]),
    (TagsInput, "List input for string tags.", _TAG_PARAMS),
    (ColorsInput, "List input for color tags.", _TAG_PARAMS),
    (FloatsInput, "List input for float values.", _TAG_PARAMS),
    (IntsInput, "List input for integer values.", _TAG_PARAMS),
    (Dropdown, "Dropdown selection control.", _SELECTION_PARAMS),
    (RadioButtons, "Radio-button selection control.", _SELECTION_PARAMS),
    (
        ToggleButtons,
        "Segmented toggle-button selection control.",
        [
            *_SELECTION_PARAMS,
            ("button_style", ""),
            ("tooltips", None),
            ("icons", None),
            ("icon_family", "classic"),
            ("icon_variant", "solid"),
            ("icon_library", "default"),
        ],
    ),
    (Select, "List-box single-selection control.", [*_SELECTION_PARAMS, ("rows", 5)]),
    (SelectMultiple, "List-box multi-selection control.", [*_SELECTION_PARAMS, ("rows", 5)]),
    (
        SelectionSlider,
        "Slider selection control.",
        [*_SELECTION_PARAMS, ("orientation", "horizontal"), ("readout", True)],
    ),
    (
        SelectionRangeSlider,
        "Range slider selection control.",
        [*_SELECTION_PARAMS, ("orientation", "horizontal"), ("readout", True)],
    ),
    (Button, "Clickable button control.", _BUTTON_PARAMS),
    (Checkbox, "Boolean checkbox control.", _CHECKBOX_PARAMS),
    (
        ToggleButton,
        "Boolean toggle-button control.",
        [
            *_CHECKBOX_PARAMS,
            ("icon", ""),
            ("button_style", ""),
            ("tooltip", ""),
            ("icon_family", "classic"),
            ("icon_variant", "solid"),
            ("icon_library", "default"),
        ],
    ),
    (Valid, "Boolean validity indicator control.", [("value", False), ("description", ""), ("readout", "")]),
    (IntSlider, "Integer slider control.", _INT_SLIDER_PARAMS),
    (IntRangeSlider, "Integer range slider control.", [("value", None), *_INT_SLIDER_PARAMS[1:]]),
    (
        IntText,
        "Integer text input control.",
        [("value", 0), ("description", ""), ("disabled", False), ("continuous_update", True)],
    ),
    (
        BoundedIntText,
        "Bounded integer text input control.",
        [
            ("value", 0),
            ("min", 0),
            ("max", 100),
            ("step", 1),
            ("description", ""),
            ("disabled", False),
            ("continuous_update", True),
        ],
    ),
    (FloatSlider, "Float slider control.", _FLOAT_SLIDER_PARAMS),
    (FloatRangeSlider, "Float range slider control.", [("value", None), *_FLOAT_SLIDER_PARAMS[1:]]),
    (
        FloatLogSlider,
        "Logarithmic float slider control.",
        [
            ("value", 1.0),
            ("base", 10.0),
            ("min", 0.0),
            ("max", 4.0),
            ("step", 0.1),
            ("description", ""),
            ("disabled", False),
            ("continuous_update", True),
            ("orientation", "horizontal"),
            ("readout", True),
            ("readout_format", ".3g"),
        ],
    ),
    (
        FloatText,
        "Float text input control.",
        [("value", 0.0), ("description", ""), ("disabled", False), ("continuous_update", True)],
    ),
    (
        BoundedFloatText,
        "Bounded float text input control.",
        [
            ("value", 0.0),
            ("min", 0.0),
            ("max", 100.0),
            ("step", 0.1),
            ("description", ""),
            ("disabled", False),
            ("continuous_update", True),
        ],
    ),
    (
        IntProgress,
        "Integer progress bar control.",
        [("value", 0), ("min", 0), ("max", 100), ("description", ""), ("bar_style", "")],
    ),
    (
        FloatProgress,
        "Float progress bar control.",
        [("value", 0.0), ("min", 0.0), ("max", 100.0), ("description", ""), ("bar_style", "")],
    ),
    (
        Play,
        "Playback stepper control.",
        [("value", 0), ("min", 0), ("max", 100), ("step", 1), ("interval", 100), ("disabled", False)],
    ),
    (DatePicker, "Date picker control.", [("value", None), ("description", ""), ("disabled", False)]),
    (TimePicker, "Time picker control.", [("value", None), ("description", ""), ("disabled", False)]),
    (DatetimePicker, "Datetime picker control.", [("value", None), ("description", ""), ("disabled", False)]),
    (
        ColorPicker,
        "Color picker control.",
        [("value", "black"), ("description", ""), ("concise", False), ("disabled", False)],
    ),
    (
        FileUpload,
        "File upload control.",
        [
            ("accept", ""),
            ("multiple", False),
            ("disabled", False),
            ("description", "Upload"),
            ("icon", "upload"),
            ("icon_family", "classic"),
            ("icon_variant", "solid"),
            ("icon_library", "default"),
        ],
    ),
    (Image, "Image display widget.", [("value", ""), ("format", "png"), ("width", ""), ("height", "")]),
    (Audio, "Audio display widget.", [("value", ""), ("format", "mp3")]),
    (Video, "Video display widget.", [("value", ""), ("format", "mp4"), ("width", ""), ("height", "")]),
    (Output, "Simple output display widget.", [("value", "")]),
    (HTML, "HTML display widget.", [("value", ""), ("description", "")]),
    (HTMLMath, "HTML and math display widget.", [("value", ""), ("description", "")]),
    (Label, "Plain text label widget.", [("value", ""), ("description", "")]),
]:
    _document_control(_cls, _summary, _params)


__all__ = [
    "Audio",
    "BoundedFloatText",
    "BoundedIntText",
    "Button",
    "Checkbox",
    "ColorPicker",
    "ColorsInput",
    "Combobox",
    "ControlWidget",
    "DatePicker",
    "DatetimePicker",
    "Dropdown",
    "FileUpload",
    "FloatLogSlider",
    "FloatProgress",
    "FloatRangeSlider",
    "FloatSlider",
    "FloatText",
    "FloatsInput",
    "HTML",
    "HTMLMath",
    "Image",
    "IntProgress",
    "IntRangeSlider",
    "IntSlider",
    "IntText",
    "IntsInput",
    "IntegerInput",
    "IntegerRangeSlider",
    "IntegerSlider",
    "Label",
    "ListBox",
    "MultiSelect",
    "Output",
    "Password",
    "PasswordInput",
    "Play",
    "RadioButtons",
    "Select",
    "SelectMultiple",
    "SelectionRangeSlider",
    "SelectionSlider",
    "TagsInput",
    "Text",
    "TextArea",
    "TextInput",
    "Textarea",
    "TimePicker",
    "ToggleButton",
    "ToggleButtons",
    "Valid",
    "Video",
]
