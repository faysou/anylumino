from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any

import anywidget
import traitlets as t

from ._common import REQUIRED as _REQUIRED
from ._common import doc as _doc
from ._common import document_control as _document_control
from ._common import json_value as _json_value
from ._common import option_value as _option_value
from ._common import options_tuple as _options_tuple
from ._common import signature as _signature
from ._common import static_asset
from ._components import ComponentWidget
from ._layout import ChildInput
from ._layout import TitleInput


def _range_value(value: Any, min_value: int | float, max_value: int | float) -> list[Any]:
    if value is None:
        return [min_value, max_value]
    return list(_json_value(value))


class ControlWidget(anywidget.AnyWidget):
    """Base class for Spectrum-backed anylumino controls.

    Controls are anywidget-native and render Spectrum Web Components where a
    matching Spectrum component exists. They do not use the classic Jupyter
    controls frontend.
    """

    _esm = static_asset("control_widget.bundle.js")
    _css = static_asset("control_widget.css")

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
    variant = t.Unicode("").tag(sync=True)
    icon = t.Unicode("").tag(sync=True)
    icon_src = t.Unicode("").tag(sync=True)
    icon_size = t.Unicode("s").tag(sync=True)
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
    href = t.Unicode("").tag(sync=True)
    quiet = t.Bool(False).tag(sync=True)
    spectrum_color = t.Unicode("light").tag(sync=True)
    spectrum_scale = t.Unicode("medium").tag(sync=True)
    spectrum_size = t.Unicode("m").tag(sync=True)

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
            value=value,
            description=description,
            placeholder=placeholder,
            disabled=disabled,
            continuous_update=continuous_update,
            **kwargs,
        )
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


class SearchInput(Text):
    """Spectrum search input control."""

    def __init__(
        self,
        value: str = "",
        description: str = "",
        placeholder: str = "",
        disabled: bool = False,
        continuous_update: bool = True,
        quiet: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            description=description,
            placeholder=placeholder,
            disabled=disabled,
            continuous_update=continuous_update,
            quiet=quiet,
            **kwargs,
        )
        self.control_kind = "search"


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

    def __init__(
        self,
        value: Iterable[Any] = (),
        allowed_tags: Iterable[str] | None = None,
        allow_duplicates: bool = False,
        description: str = "",
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            allowed_tags=allowed_tags,
            allow_duplicates=allow_duplicates,
            description=description,
            disabled=disabled,
            **kwargs,
        )
        self.control_kind = "colors"


class FloatsInput(TagsInput):
    """List input for float values."""

    def __init__(
        self,
        value: Iterable[Any] = (),
        allowed_tags: Iterable[str] | None = None,
        allow_duplicates: bool = False,
        description: str = "",
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            allowed_tags=allowed_tags,
            allow_duplicates=allow_duplicates,
            description=description,
            disabled=disabled,
            **kwargs,
        )
        self.control_kind = "floats"


class IntsInput(TagsInput):
    """List input for integer values."""

    def __init__(
        self,
        value: Iterable[Any] = (),
        allowed_tags: Iterable[str] | None = None,
        allow_duplicates: bool = False,
        description: str = "",
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            allowed_tags=allowed_tags,
            allow_duplicates=allow_duplicates,
            description=description,
            disabled=disabled,
            **kwargs,
        )
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

    def __init__(
        self,
        options: Iterable[Any] = (),
        value: Any = None,
        index: int | None = None,
        description: str = "",
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            options=options,
            value=value,
            index=index,
            description=description,
            disabled=disabled,
            **kwargs,
        )
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
        variant: str = "",
        tooltips: Iterable[str] | None = None,
        icons: Iterable[str | dict[str, Any]] | None = None,
        icon_size: str = "s",
        quiet: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            options=options,
            value=value,
            index=index,
            description=description,
            disabled=disabled,
            variant=variant,
            tooltips=list(tooltips) if tooltips is not None else None,
            icons=list(icons) if icons is not None else None,
            icon_size=icon_size,
            quiet=quiet,
            **kwargs,
        )
        self.control_kind = "toggle-buttons"


class Select(Dropdown):
    """List-box single-selection control."""

    def __init__(
        self,
        options: Iterable[Any] = (),
        value: Any = None,
        index: int | None = None,
        description: str = "",
        disabled: bool = False,
        rows: int = 5,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            options=options,
            value=value,
            index=index,
            description=description,
            disabled=disabled,
            rows=rows,
            **kwargs,
        )
        self.control_kind = "select"


class SelectMultiple(Dropdown):
    """List-box multi-selection control."""

    def __init__(
        self,
        options: Iterable[Any] = (),
        value: Iterable[Any] | None = (),
        index: int | Iterable[int] | None = None,
        rows: int = 5,
        description: str = "",
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            options=options,
            value=list(value or []),
            index=index,
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
        description: str = "",
        disabled: bool = False,
        orientation: str = "horizontal",
        readout: bool = True,
        **kwargs: Any,
    ) -> None:
        option_tuple = _options_tuple(options)
        if value is None and index is not None and option_tuple:
            index_list = list(index)
            value = [_option_value(option_tuple[index_list[0]]), _option_value(option_tuple[index_list[1]])]
        super().__init__(
            options=option_tuple,
            value=list(value or []),
            index=index,
            description=description,
            disabled=disabled,
            orientation=orientation,
            readout=readout,
            **kwargs,
        )
        self.control_kind = "selection-range-slider"


class Button(ControlWidget):
    """Clickable button control."""

    def __init__(
        self,
        description: str = "",
        icon: str = "",
        icon_src: str = "",
        icon_size: str = "s",
        disabled: bool = False,
        variant: str = "",
        tooltip: str = "",
        quiet: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="button",
            description=description,
            icon=icon,
            icon_src=icon_src,
            icon_size=icon_size,
            disabled=disabled,
            variant=variant,
            tooltip=tooltip,
            quiet=quiet,
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
        indent: bool = True,
        icon: str = "",
        icon_src: str = "",
        icon_size: str = "s",
        disabled: bool = False,
        variant: str = "",
        tooltip: str = "",
        quiet: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            description=description,
            disabled=disabled,
            indent=indent,
            icon=icon,
            icon_src=icon_src,
            icon_size=icon_size,
            variant=variant,
            tooltip=tooltip,
            quiet=quiet,
            **kwargs,
        )
        self.control_kind = "toggle"


class Switch(Checkbox):
    """Spectrum switch control."""

    def __init__(
        self,
        value: bool = False,
        description: str = "",
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(value=value, description=description, disabled=disabled, **kwargs)
        self.control_kind = "switch"


class Valid(Checkbox):
    """Boolean validity indicator control."""

    def __init__(self, value: bool = False, description: str = "", readout: str = "", **kwargs: Any) -> None:
        super().__init__(value=value, description=description, **kwargs)
        self.control_kind = "valid"
        self.placeholder = readout


class StatusLight(ControlWidget):
    """Spectrum status-light display control."""

    def __init__(
        self,
        value: bool = True,
        description: str = "",
        variant: str = "",
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="status-light",
            value=value,
            description=description,
            variant=variant,
            disabled=disabled,
            **kwargs,
        )


class Badge(ControlWidget):
    """Spectrum badge display control."""

    def __init__(
        self,
        value: str = "",
        description: str = "",
        variant: str = "neutral",
        icon: str = "",
        icon_src: str = "",
        icon_size: str = "s",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="badge",
            value=value,
            description=description,
            variant=variant,
            icon=icon,
            icon_src=icon_src,
            icon_size=icon_size,
            **kwargs,
        )


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
        description: str = "",
        disabled: bool = False,
        continuous_update: bool = True,
        orientation: str = "horizontal",
        readout: bool = True,
        readout_format: str = "d",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=_range_value(value, min, max),
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

    def __init__(
        self,
        value: int = 0,
        min: int = 0,
        max: int = 100,
        step: int = 1,
        description: str = "",
        disabled: bool = False,
        continuous_update: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            min=min,
            max=max,
            step=step,
            description=description,
            disabled=disabled,
            continuous_update=continuous_update,
            **kwargs,
        )
        self.control_kind = "bounded-int-text"


class FloatSlider(IntSlider):
    """Float slider control."""

    def __init__(
        self,
        value: float = 0.0,
        min: float = 0.0,
        max: float = 100.0,
        step: float = 0.1,
        description: str = "",
        disabled: bool = False,
        continuous_update: bool = True,
        orientation: str = "horizontal",
        readout: bool = True,
        readout_format: str = ".2f",
        **kwargs: Any,
    ) -> None:
        super().__init__(
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
        self.control_kind = "float-slider"


class FloatRangeSlider(FloatSlider):
    """Float range slider control."""

    def __init__(
        self,
        value: Iterable[float] | None = None,
        min: float = 0.0,
        max: float = 100.0,
        step: float = 0.1,
        description: str = "",
        disabled: bool = False,
        continuous_update: bool = True,
        orientation: str = "horizontal",
        readout: bool = True,
        readout_format: str = ".2f",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=_range_value(value, min, max),
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
        description: str = "",
        disabled: bool = False,
        continuous_update: bool = True,
        orientation: str = "horizontal",
        readout: bool = True,
        readout_format: str = ".3g",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            base=base,
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
        self.control_kind = "float-log-slider"


class FloatText(IntText):
    """Float text input control."""

    def __init__(
        self,
        value: float = 0.0,
        description: str = "",
        disabled: bool = False,
        continuous_update: bool = True,
        min: int | float | None = None,
        max: int | float | None = None,
        step: int | float | str = "any",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            description=description,
            disabled=disabled,
            continuous_update=continuous_update,
            min=min,
            max=max,
            step=step,
            **kwargs,
        )
        self.control_kind = "float-text"


class BoundedFloatText(FloatText):
    """Bounded float text input control."""

    def __init__(
        self,
        value: float = 0.0,
        min: float = 0.0,
        max: float = 100.0,
        step: float = 0.1,
        description: str = "",
        disabled: bool = False,
        continuous_update: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            min=min,
            max=max,
            step=step,
            description=description,
            disabled=disabled,
            continuous_update=continuous_update,
            **kwargs,
        )
        self.control_kind = "bounded-float-text"


class IntProgress(IntSlider):
    """Integer progress bar control."""

    def __init__(
        self,
        value: int = 0,
        min: int = 0,
        max: int = 100,
        description: str = "",
        bar_style: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(value=value, min=min, max=max, description=description, variant=bar_style, **kwargs)
        self.control_kind = "int-progress"


class FloatProgress(FloatSlider):
    """Float progress bar control."""

    def __init__(
        self,
        value: float = 0.0,
        min: float = 0.0,
        max: float = 100.0,
        description: str = "",
        bar_style: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(value=value, min=min, max=max, description=description, variant=bar_style, **kwargs)
        self.control_kind = "float-progress"


class Meter(ControlWidget):
    """Spectrum meter display control."""

    def __init__(
        self,
        value: float = 0.0,
        description: str = "",
        variant: str = "informative",
        readout: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="meter",
            value=value,
            description=description,
            variant=variant,
            readout=readout,
            **kwargs,
        )


class Play(IntSlider):
    """Playback stepper control."""

    def __init__(
        self,
        value: int = 0,
        min: int = 0,
        max: int = 100,
        step: int = 1,
        interval: int = 100,
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(value=value, min=min, max=max, step=step, disabled=disabled, **kwargs)
        self.control_kind = "play"
        self.rows = interval


class ColorPicker(ControlWidget):
    """Color picker control."""

    def __init__(
        self,
        value: str = "black",
        description: str = "",
        concise: bool = False,
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="color",
            value=value,
            description=description,
            concise=concise,
            disabled=disabled,
            **kwargs,
        )


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
        icon: str = "Upload",
        icon_src: str = "",
        icon_size: str = "s",
        variant: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            description=description,
            icon=icon,
            disabled=disabled,
            accept=accept,
            multiple=multiple,
            value=[],
            icon_src=icon_src,
            icon_size=icon_size,
            variant=variant,
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

    def __init__(self, value: bytes | str = "", format: str = "mp3", **kwargs: Any) -> None:
        super().__init__(value=value, format=format, **kwargs)
        self.control_kind = "audio"


class Video(Image):
    """Video display widget."""

    def __init__(
        self,
        value: bytes | str = "",
        format: str = "mp4",
        width: str = "",
        height: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(value=value, format=format, width=width, height=height, **kwargs)
        self.control_kind = "video"


class HTML(ControlWidget):
    """HTML display widget."""

    def __init__(self, value: str = "", description: str = "", **kwargs: Any) -> None:
        super().__init__(control_kind="html", value=value, description=description, html=True, **kwargs)


class HTMLMath(HTML):
    """HTML display alias matching the ipywidgets HTMLMath API."""


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


class Link(ControlWidget):
    """Spectrum link display control."""

    def __init__(
        self,
        href: str,
        description: str = "",
        variant: str = "primary",
        quiet: bool = False,
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="link",
            value=href,
            href=href,
            description=description,
            variant=variant,
            quiet=quiet,
            disabled=disabled,
            **kwargs,
        )


class Divider(ControlWidget):
    """Spectrum divider display control."""

    def __init__(
        self,
        orientation: str = "horizontal",
        spectrum_size: str = "m",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="divider",
            orientation=orientation,
            spectrum_size=spectrum_size,
            **kwargs,
        )


TextInput = Text
TextArea = Textarea
PasswordInput = Password
ListBox = Select
MultiSelect = SelectMultiple
IntegerInput = IntText
IntegerSlider = IntSlider
IntegerRangeSlider = IntRangeSlider


_CONTROL_PARAM_DOCS = {
    "accept": "Accepted file extensions or MIME types.",
    "allow_duplicates": "Whether duplicate entries are allowed.",
    "allowed_tags": "Optional allowed values for tag-style inputs.",
    "bar_style": "Progress-bar style name such as ``'success'`` or ``'warning'``.",
    "base": "Logarithm base for logarithmic sliders.",
    "concise": "Whether to use a compact color-picker display.",
    "continuous_update": "Whether Python receives updates while the user is typing or dragging.",
    "description": "Label shown above the control.",
    "disabled": "Whether user interaction is disabled.",
    "ensure_option": "Whether combobox values must be present in ``options``.",
    "format": "Media format such as ``'png'``, ``'mp3'``, or ``'mp4'``.",
    "href": "Destination URL for link controls.",
    "height": "CSS height for media widgets.",
    "icon": "Spectrum workflow icon name, for example ``'AddContent'`` or ``'HelpCircle'``.",
    "icon_size": "Spectrum icon size such as ``'s'``, ``'m'``, ``'l'``, ``'xl'``, or ``'xxl'``.",
    "icon_src": "Custom icon image URL or data URI for ``sp-icon``.",
    "icons": "Spectrum workflow icon names or per-option icon dictionaries for toggle-button options.",
    "indent": "Whether checkbox labels are indented.",
    "index": "Selected option index.",
    "interval": "Delay between play-widget ticks in milliseconds.",
    "max": "Maximum numeric, date, or time value.",
    "min": "Minimum numeric, date, or time value.",
    "multiple": "Whether multiple files can be selected.",
    "options": "Selectable values or ``(label, value)`` pairs.",
    "orientation": "``'horizontal'`` or ``'vertical'``.",
    "placeholder": "Text shown while the input is empty.",
    "quiet": "Whether to use Spectrum's quiet visual treatment.",
    "readout": "Whether to show the current value.",
    "readout_format": "Format string used for slider readouts.",
    "rows": "Visible row count.",
    "spectrum_size": "Spectrum component size such as ``'s'``, ``'m'``, ``'l'``, or ``'xl'``.",
    "step": "Increment size.",
    "tooltips": "Per-option tooltips.",
    "tooltip": "Hover text.",
    "value": "Initial value and synced Python value.",
    "variant": "Spectrum visual variant such as ``'accent'``, ``'primary'``, ``'negative'``, ``'positive'``, or ``'informative'``.",
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
_SEARCH_PARAMS = [*_TEXT_PARAMS, ("quiet", False)]
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
    ("icon_src", ""),
    ("icon_size", "s"),
    ("disabled", False),
    ("variant", ""),
    ("tooltip", ""),
    ("quiet", False),
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
    (SearchInput, "Spectrum search input control.", _SEARCH_PARAMS),
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
            ("variant", ""),
            ("tooltips", None),
            ("icons", None),
            ("icon_size", "s"),
            ("quiet", False),
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
            ("icon_src", ""),
            ("icon_size", "s"),
            ("variant", ""),
            ("tooltip", ""),
            ("quiet", False),
        ],
    ),
    (Switch, "Spectrum switch control.", [("value", False), ("description", ""), ("disabled", False)]),
    (Valid, "Boolean validity indicator control.", [("value", False), ("description", ""), ("readout", "")]),
    (
        StatusLight,
        "Spectrum status-light display control.",
        [("value", True), ("description", ""), ("variant", ""), ("disabled", False)],
    ),
    (
        Badge,
        "Spectrum badge display control.",
        [
            ("value", ""),
            ("description", ""),
            ("variant", "neutral"),
            ("icon", ""),
            ("icon_src", ""),
            ("icon_size", "s"),
        ],
    ),
    (IntSlider, "Integer slider control.", _INT_SLIDER_PARAMS),
    (IntRangeSlider, "Integer range slider control.", [("value", None), *_INT_SLIDER_PARAMS[1:]]),
    (
        IntText,
        "Integer text input control.",
        [
            ("value", 0),
            ("description", ""),
            ("disabled", False),
            ("continuous_update", True),
            ("min", None),
            ("max", None),
            ("step", 1),
        ],
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
        [
            ("value", 0.0),
            ("description", ""),
            ("disabled", False),
            ("continuous_update", True),
            ("min", None),
            ("max", None),
            ("step", "any"),
        ],
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
        Meter,
        "Spectrum meter display control.",
        [("value", 0.0), ("description", ""), ("variant", "informative"), ("readout", False)],
    ),
    (
        Play,
        "Playback stepper control.",
        [("value", 0), ("min", 0), ("max", 100), ("step", 1), ("interval", 100), ("disabled", False)],
    ),
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
            ("icon", "Upload"),
            ("icon_src", ""),
            ("icon_size", "s"),
            ("variant", ""),
        ],
    ),
    (Image, "Image display widget.", [("value", ""), ("format", "png"), ("width", ""), ("height", "")]),
    (Audio, "Audio display widget.", [("value", ""), ("format", "mp3")]),
    (Video, "Video display widget.", [("value", ""), ("format", "mp4"), ("width", ""), ("height", "")]),
    (Output, "Simple output display widget.", [("value", "")]),
    (HTML, "HTML display widget.", [("value", ""), ("description", "")]),
    (HTMLMath, "HTML display alias matching the ipywidgets HTMLMath API.", [("value", ""), ("description", "")]),
    (Label, "Plain text label widget.", [("value", ""), ("description", "")]),
    (
        Link,
        "Spectrum link display control.",
        [("href", _REQUIRED), ("description", ""), ("variant", "primary"), ("quiet", False), ("disabled", False)],
    ),
    (Divider, "Spectrum divider display control.", [("orientation", "horizontal"), ("spectrum_size", "m")]),
]:
    _document_control(_cls, _summary, _params, _CONTROL_PARAM_DOCS, required_marker=_REQUIRED)


class SpectrumWidget(ComponentWidget):
    """Base class for standalone Spectrum Web Component anywidgets.

    ``SpectrumWidget`` exposes Spectrum components that are not ordinary input
    controls. Components can contain child anywidgets, which makes wrappers
    such as dialogs, popovers, trays, and field groups composable.
    """

    _esm = static_asset("spectrum_widget.bundle.js")
    _css = static_asset("spectrum_widget.css")

    component_family = t.Unicode("spectrum").tag(sync=True)
    spectrum_color = t.Unicode("light").tag(sync=True)
    spectrum_scale = t.Unicode("medium").tag(sync=True)
    spectrum_size = t.Unicode("m").tag(sync=True)


class SpectrumElement(SpectrumWidget):
    """Generic Spectrum element wrapper for custom or future Spectrum tags."""

    def __init__(
        self,
        tag: str,
        children: ChildInput = None,
        *,
        text: str = "",
        label: str = "",
        attributes: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            children,
            component_kind="element",
            tag=tag,
            text=text,
            label=label,
            attributes=dict(attributes or {}),
            **kwargs,
        )


class Icon(SpectrumWidget):
    """Spectrum icon anywidget."""

    def __init__(
        self,
        icon: str = "",
        *,
        icon_src: str = "",
        icon_size: str = "m",
        label: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            component_kind="icon",
            icon=icon,
            icon_src=icon_src,
            icon_size=icon_size,
            label=label,
            **kwargs,
        )


class UIIcon(SpectrumWidget):
    """Spectrum UI icon anywidget."""

    def __init__(
        self,
        value: str = "checkmark100",
        *,
        label: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(component_kind="ui-icon", value=value, label=label, **kwargs)


class ClearButton(SpectrumWidget):
    """Spectrum clear-button style action widget."""

    def __init__(
        self,
        label: str = "Clear",
        *,
        component_kind: str = "clear-button",
        disabled: bool = False,
        callbacks: Iterable[Callable[[SpectrumWidget], None]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            component_kind=component_kind,
            label=label,
            text=label,
            disabled=disabled,
            callbacks=callbacks,
            **kwargs,
        )


class CloseButton(ClearButton):
    """Spectrum close-button style action widget."""

    def __init__(
        self,
        label: str = "Close",
        *,
        disabled: bool = False,
        callbacks: Iterable[Callable[[SpectrumWidget], None]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            label=label,
            component_kind="close-button",
            disabled=disabled,
            callbacks=callbacks,
            **kwargs,
        )


class InfieldButton(SpectrumWidget):
    """Spectrum infield button widget."""

    def __init__(
        self,
        label: str = "",
        *,
        component_kind: str = "infield-button",
        icon: str = "",
        disabled: bool = False,
        callbacks: Iterable[Callable[[SpectrumWidget], None]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            component_kind=component_kind,
            label=label,
            text=label,
            icon=icon,
            disabled=disabled,
            callbacks=callbacks,
            **kwargs,
        )


class PickerButton(InfieldButton):
    """Spectrum picker button widget."""

    def __init__(
        self,
        label: str = "",
        *,
        icon: str = "",
        disabled: bool = False,
        callbacks: Iterable[Callable[[SpectrumWidget], None]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            label=label,
            component_kind="picker-button",
            icon=icon,
            disabled=disabled,
            callbacks=callbacks,
            **kwargs,
        )


class FieldGroup(SpectrumWidget):
    """Spectrum field group container for composed controls."""

    def __init__(
        self,
        children: ChildInput = None,
        *,
        label: str = "",
        orientation: str = "horizontal",
        **kwargs: Any,
    ) -> None:
        super().__init__(children, component_kind="field-group", label=label, orientation=orientation, **kwargs)


class HelpText(SpectrumWidget):
    """Spectrum help text widget."""

    def __init__(
        self,
        text: str,
        *,
        variant: str = "neutral",
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(component_kind="help-text", text=text, variant=variant, disabled=disabled, **kwargs)


class ProgressCircle(SpectrumWidget):
    """Spectrum progress circle widget."""

    def __init__(
        self,
        value: int | float = 0,
        *,
        label: str = "",
        indeterminate: bool = False,
        spectrum_size: str = "m",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            component_kind="progress-circle",
            value=value,
            label=label,
            indeterminate=indeterminate,
            spectrum_size=spectrum_size,
            **kwargs,
        )


class ColorHandle(SpectrumWidget):
    """Spectrum color handle widget."""

    def __init__(
        self,
        value: str = "#1473e6",
        *,
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(component_kind="color-handle", value=value, disabled=disabled, **kwargs)


class ColorLoupe(SpectrumWidget):
    """Spectrum color loupe widget."""

    def __init__(
        self,
        value: str = "#1473e6",
        *,
        open: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(component_kind="color-loupe", value=value, is_open=open, **kwargs)


class OpacityCheckerboard(SpectrumWidget):
    """Spectrum opacity-checkerboard display widget."""

    def __init__(self, *, width: int | float | str | None = 120, height: int | float | str | None = 48, **kwargs: Any) -> None:
        super().__init__(component_kind="opacity-checkerboard", width=width, height=height, **kwargs)


class Popover(SpectrumWidget):
    """Spectrum popover surface with composable child content."""

    def __init__(
        self,
        children: ChildInput = None,
        *,
        open: bool = True,
        placement: str = "bottom",
        **kwargs: Any,
    ) -> None:
        super().__init__(children, component_kind="popover", is_open=open, placement=placement, **kwargs)


class Tooltip(SpectrumWidget):
    """Spectrum tooltip with optional trigger child."""

    def __init__(
        self,
        text: str,
        children: ChildInput = None,
        *,
        open: bool = False,
        placement: str = "top",
        variant: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            children,
            component_kind="tooltip",
            text=text,
            is_open=open,
            placement=placement,
            variant=variant,
            **kwargs,
        )


class Tray(SpectrumWidget):
    """Spectrum tray surface with composable child content."""

    def __init__(
        self,
        children: ChildInput = None,
        *,
        open: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(children, component_kind="tray", is_open=open, **kwargs)


class Underlay(SpectrumWidget):
    """Spectrum underlay widget."""

    def __init__(
        self,
        *,
        open: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(component_kind="underlay", is_open=open, **kwargs)


class Overlay(SpectrumWidget):
    """Spectrum overlay wrapper for composed child content."""

    def __init__(
        self,
        children: ChildInput = None,
        *,
        open: bool = True,
        placement: str = "bottom",
        **kwargs: Any,
    ) -> None:
        super().__init__(children, component_kind="overlay", is_open=open, placement=placement, **kwargs)


class DialogBox(SpectrumWidget):
    """Composable Spectrum-style dialog anywidget."""

    def __init__(
        self,
        children: ChildInput = None,
        *,
        title: str = "",
        open: bool = False,
        width: int | float | str | None = 420,
        callbacks: Iterable[Callable[[SpectrumWidget], None]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            children,
            component_kind="dialog",
            label=title,
            is_open=open,
            width=width,
            callbacks=callbacks,
            **kwargs,
        )


class Modal(DialogBox):
    """Alias for a composable Spectrum-style modal dialog."""


_COMPONENT_PARAM_DOCS = {
    "attributes": "HTML attributes forwarded to the rendered Spectrum element.",
    "callbacks": "Optional callbacks invoked when the widget sends an activation event.",
    "children": "Child anywidgets or keyed child mapping rendered inside the component.",
    "component_kind": "Internal component kind used by specialized button subclasses.",
    "disabled": "Whether user interaction is disabled.",
    "height": "CSS height for display-oriented components.",
    "icon": "Spectrum workflow icon name.",
    "icon_size": "Spectrum icon size such as ``'s'``, ``'m'``, ``'l'``, ``'xl'``, or ``'xxl'``.",
    "icon_src": "Custom icon image URL or data URI.",
    "indeterminate": "Whether progress should render as an indeterminate indicator.",
    "label": "Accessible label or visible label, depending on the component.",
    "open": "Whether an overlay-like component starts open.",
    "orientation": "Component orientation such as ``'horizontal'`` or ``'vertical'``.",
    "placement": "Preferred overlay placement such as ``'top'``, ``'bottom'``, ``'left'``, or ``'right'``.",
    "spectrum_size": "Spectrum component size such as ``'s'``, ``'m'``, ``'l'``, or ``'xl'``.",
    "tag": "Spectrum custom element tag name to render.",
    "text": "Visible text content.",
    "title": "Dialog title text.",
    "value": "Initial value and synced Python value.",
    "variant": "Spectrum visual variant.",
    "width": "CSS width for display-oriented components.",
}


def _component_doc(summary: str, parameters: list[tuple[str, object]]) -> str:
    return _doc(
        summary,
        parameters,
        _COMPONENT_PARAM_DOCS,
        fallback="Component option.",
        required_marker=_REQUIRED,
    )


def _document_component(cls: type, summary: str, parameters: list[tuple[str, object]]) -> None:
    cls.__signature__ = _signature(parameters)
    cls.__doc__ = _component_doc(summary, parameters)


for _cls, _summary, _params in [
    (
        SpectrumElement,
        "Generic wrapper for rendering a Spectrum custom element.",
        [("tag", _REQUIRED), ("children", None), ("text", ""), ("label", ""), ("attributes", None)],
    ),
    (Icon, "Display a Spectrum workflow icon.", [("icon", ""), ("icon_src", ""), ("icon_size", "m"), ("label", "")]),
    (UIIcon, "Display a Spectrum UI icon.", [("value", "checkmark100"), ("label", "")]),
    (
        ClearButton,
        "Compact clear-style action button.",
        [("label", "Clear"), ("component_kind", "clear-button"), ("disabled", False), ("callbacks", None)],
    ),
    (CloseButton, "Compact close-style action button.", [("label", "Close"), ("disabled", False), ("callbacks", None)]),
    (
        InfieldButton,
        "Button designed for placement inside an input field.",
        [("label", ""), ("component_kind", "infield-button"), ("icon", ""), ("disabled", False), ("callbacks", None)],
    ),
    (
        PickerButton,
        "Button styled for opening picker-style popups.",
        [("label", ""), ("icon", ""), ("disabled", False), ("callbacks", None)],
    ),
    (
        FieldGroup,
        "Group child controls into a horizontal or vertical field layout.",
        [("children", None), ("label", ""), ("orientation", "horizontal")],
    ),
    (HelpText, "Display contextual help or validation text.", [("text", _REQUIRED), ("variant", "neutral"), ("disabled", False)]),
    (
        ProgressCircle,
        "Display circular progress or indeterminate activity.",
        [("value", 0), ("label", ""), ("indeterminate", False), ("spectrum_size", "m")],
    ),
    (ColorHandle, "Display a draggable-looking color handle.", [("value", "#1473e6"), ("disabled", False)]),
    (ColorLoupe, "Display a color loupe preview.", [("value", "#1473e6"), ("open", True)]),
    (OpacityCheckerboard, "Display an opacity checkerboard swatch.", [("width", 120), ("height", 48)]),
    (Popover, "Display child content in a popover surface.", [("children", None), ("open", True), ("placement", "bottom")]),
    (
        Tooltip,
        "Display tooltip text with an optional trigger child.",
        [("text", _REQUIRED), ("children", None), ("open", False), ("placement", "top"), ("variant", "")],
    ),
    (Tray, "Display child content in a tray surface.", [("children", None), ("open", True)]),
    (Underlay, "Display a page underlay backdrop.", [("open", True)]),
    (Overlay, "Position child content as an overlay.", [("children", None), ("open", True), ("placement", "bottom")]),
    (
        DialogBox,
        "Display a composable modal dialog.",
        [("children", None), ("title", ""), ("open", False), ("width", 420), ("callbacks", None)],
    ),
    (
        Modal,
        "Alias for a composable modal dialog.",
        [("children", None), ("title", ""), ("open", False), ("width", 420), ("callbacks", None)],
    ),
]:
    _document_component(_cls, _summary, _params)


__all__ = [
    "Audio",
    "Badge",
    "BoundedFloatText",
    "BoundedIntText",
    "Button",
    "Checkbox",
    "ColorPicker",
    "ColorsInput",
    "Combobox",
    "ControlWidget",
    "Divider",
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
    "Link",
    "ListBox",
    "Meter",
    "MultiSelect",
    "Output",
    "Password",
    "PasswordInput",
    "Play",
    "RadioButtons",
    "SearchInput",
    "Select",
    "SelectMultiple",
    "SelectionRangeSlider",
    "SelectionSlider",
    "TagsInput",
    "Text",
    "TextArea",
    "TextInput",
    "Textarea",
    "ToggleButton",
    "ToggleButtons",
    "StatusLight",
    "Switch",
    "Valid",
    "Video",
    "ClearButton",
    "CloseButton",
    "ColorHandle",
    "ColorLoupe",
    "DialogBox",
    "FieldGroup",
    "HelpText",
    "Icon",
    "InfieldButton",
    "Modal",
    "OpacityCheckerboard",
    "Overlay",
    "PickerButton",
    "Popover",
    "ProgressCircle",
    "SpectrumElement",
    "SpectrumWidget",
    "Tooltip",
    "Tray",
    "UIIcon",
    "Underlay",
]
