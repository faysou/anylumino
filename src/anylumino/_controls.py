from __future__ import annotations

from inspect import Parameter
from inspect import Signature

from ipywidgets import Audio
from ipywidgets import BoundedFloatText
from ipywidgets import BoundedIntText
from ipywidgets import Button
from ipywidgets import Checkbox
from ipywidgets import ColorPicker
from ipywidgets import ColorsInput
from ipywidgets import Combobox
from ipywidgets import DatePicker
from ipywidgets import DatetimePicker
from ipywidgets import Dropdown
from ipywidgets import FileUpload
from ipywidgets import FloatLogSlider
from ipywidgets import FloatProgress
from ipywidgets import FloatRangeSlider
from ipywidgets import FloatSlider
from ipywidgets import FloatText
from ipywidgets import FloatsInput
from ipywidgets import HTML
from ipywidgets import HTMLMath
from ipywidgets import Image
from ipywidgets import IntProgress
from ipywidgets import IntRangeSlider
from ipywidgets import IntSlider
from ipywidgets import IntText
from ipywidgets import IntsInput
from ipywidgets import Label
from ipywidgets import Output
from ipywidgets import Password
from ipywidgets import Play
from ipywidgets import RadioButtons
from ipywidgets import Select
from ipywidgets import SelectMultiple
from ipywidgets import SelectionRangeSlider
from ipywidgets import SelectionSlider
from ipywidgets import TagsInput
from ipywidgets import Text
from ipywidgets import Textarea
from ipywidgets import TimePicker
from ipywidgets import ToggleButton
from ipywidgets import ToggleButtons
from ipywidgets import Valid
from ipywidgets import Video


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
    "button_style": "Predefined button style such as ``'primary'`` or ``'success'``.",
    "concise": "Whether to use a compact color-picker display.",
    "continuous_update": "Whether Python receives updates while the user is typing or dragging.",
    "description": "Label shown next to the control.",
    "disabled": "Whether user interaction is disabled.",
    "ensure_option": "Whether combobox values must be present in ``options``.",
    "format": "Media format such as ``'png'``, ``'mp3'``, or ``'mp4'``.",
    "height": "CSS height for media widgets.",
    "icon": "Font Awesome icon name without the ``fa-`` prefix.",
    "icons": "Icon names for toggle-button options.",
    "indent": "Whether checkbox labels are indented.",
    "index": "Selected option index.",
    "interval": "Delay between play-widget ticks in milliseconds.",
    "layout": "ipywidgets ``Layout`` object for CSS sizing and spacing.",
    "max": "Maximum numeric, date, or time value.",
    "min": "Minimum numeric, date, or time value.",
    "multiple": "Whether multiple files can be uploaded.",
    "options": "Selectable values or ``(label, value)`` pairs.",
    "orientation": "``'horizontal'`` or ``'vertical'``.",
    "placeholder": "Text shown while the input is empty.",
    "readout": "Slider readout visibility or validity readout text.",
    "readout_format": "Format string used for slider readouts.",
    "rows": "Visible row count.",
    "step": "Increment size.",
    "style": "ipywidgets style object or style dictionary.",
    "tooltips": "Per-option tooltips.",
    "tooltip": "Hover text.",
    "value": "Initial value and synced Python value.",
    "width": "CSS width for media widgets.",
}


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
        lines.append(f"    {_CONTROL_PARAM_DOCS.get(name, 'Widget option.')}")
    return "\n".join(lines)


def _document_control(cls: type, summary: str, parameters: list[tuple[str, object]]) -> None:
    cls.__signature__ = _signature(parameters)
    cls.__doc__ = _doc(summary, parameters)


_REQUIRED = object()
_TEXT_PARAMS = [
    ("value", ""),
    ("description", ""),
    ("placeholder", ""),
    ("disabled", False),
    ("continuous_update", True),
    ("layout", None),
    ("style", None),
]
_SELECTION_PARAMS = [
    ("options", ()),
    ("value", None),
    ("index", None),
    ("description", ""),
    ("disabled", False),
    ("layout", None),
    ("style", None),
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
    ("layout", None),
    ("style", None),
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
    ("layout", None),
    ("style", None),
]
_TEXT_VALUE_PARAMS = [
    ("value", ""),
    ("description", ""),
    ("disabled", False),
    ("layout", None),
    ("style", None),
]
_NUMERIC_TEXT_PARAMS = [
    ("value", 0),
    ("description", ""),
    ("disabled", False),
    ("continuous_update", True),
    ("layout", None),
    ("style", None),
]
_BOUNDED_INT_TEXT_PARAMS = [
    ("value", 0),
    ("min", 0),
    ("max", 100),
    ("step", 1),
    ("description", ""),
    ("disabled", False),
    ("continuous_update", True),
    ("layout", None),
    ("style", None),
]
_BOUNDED_FLOAT_TEXT_PARAMS = [
    ("value", 0.0),
    ("min", 0.0),
    ("max", 100.0),
    ("step", 0.1),
    ("description", ""),
    ("disabled", False),
    ("continuous_update", True),
    ("layout", None),
    ("style", None),
]
_COMBOBOX_PARAMS = [
    ("value", ""),
    ("options", ()),
    ("description", ""),
    ("placeholder", ""),
    ("ensure_option", False),
    ("disabled", False),
    ("continuous_update", True),
    ("layout", None),
    ("style", None),
]
_TAGS_INPUT_PARAMS = [
    ("value", ()),
    ("allowed_tags", None),
    ("allow_duplicates", False),
    ("description", ""),
    ("disabled", False),
    ("layout", None),
    ("style", None),
]
_TOGGLE_BUTTONS_PARAMS = [
    *_SELECTION_PARAMS,
    ("button_style", ""),
    ("tooltips", None),
    ("icons", None),
]
_SELECTION_SLIDER_PARAMS = [
    *_SELECTION_PARAMS,
    ("orientation", "horizontal"),
    ("readout", True),
]
_BUTTON_PARAMS = [
    ("description", ""),
    ("icon", ""),
    ("disabled", False),
    ("button_style", ""),
    ("tooltip", ""),
    ("layout", None),
    ("style", None),
]
_CHECKBOX_PARAMS = [
    ("value", False),
    ("description", ""),
    ("disabled", False),
    ("indent", True),
    ("layout", None),
    ("style", None),
]
_TOGGLE_BUTTON_PARAMS = [
    ("value", False),
    ("description", ""),
    ("icon", ""),
    ("disabled", False),
    ("button_style", ""),
    ("tooltip", ""),
    ("layout", None),
    ("style", None),
]
_VALID_PARAMS = [
    ("value", False),
    ("description", ""),
    ("readout", ""),
    ("layout", None),
    ("style", None),
]
_INT_RANGE_SLIDER_PARAMS = [
    ("value", None),
    ("min", 0),
    ("max", 100),
    ("step", 1),
    ("description", ""),
    ("disabled", False),
    ("continuous_update", True),
    ("orientation", "horizontal"),
    ("readout", True),
    ("readout_format", "d"),
    ("layout", None),
    ("style", None),
]
_FLOAT_RANGE_SLIDER_PARAMS = [
    ("value", None),
    ("min", 0.0),
    ("max", 100.0),
    ("step", 0.1),
    ("description", ""),
    ("disabled", False),
    ("continuous_update", True),
    ("orientation", "horizontal"),
    ("readout", True),
    ("readout_format", ".2f"),
    ("layout", None),
    ("style", None),
]
_FLOAT_LOG_SLIDER_PARAMS = [
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
    ("layout", None),
    ("style", None),
]
_FLOAT_TEXT_PARAMS = [
    ("value", 0.0),
    ("description", ""),
    ("disabled", False),
    ("continuous_update", True),
    ("layout", None),
    ("style", None),
]
_INT_PROGRESS_PARAMS = [
    ("value", 0),
    ("min", 0),
    ("max", 100),
    ("description", ""),
    ("bar_style", ""),
    ("orientation", "horizontal"),
    ("layout", None),
    ("style", None),
]
_FLOAT_PROGRESS_PARAMS = [
    ("value", 0.0),
    ("min", 0.0),
    ("max", 100.0),
    ("description", ""),
    ("bar_style", ""),
    ("orientation", "horizontal"),
    ("layout", None),
    ("style", None),
]
_PLAY_PARAMS = [
    ("value", 0),
    ("min", 0),
    ("max", 100),
    ("step", 1),
    ("interval", 100),
    ("disabled", False),
    ("layout", None),
    ("style", None),
]
_DATE_PARAMS = [
    ("value", None),
    ("description", ""),
    ("disabled", False),
    ("layout", None),
    ("style", None),
]
_TIME_PARAMS = [
    ("value", None),
    ("min", None),
    ("max", None),
    ("step", 60),
    ("description", ""),
    ("disabled", False),
    ("layout", None),
    ("style", None),
]
_COLOR_PICKER_PARAMS = [
    ("value", "black"),
    ("description", ""),
    ("concise", False),
    ("disabled", False),
    ("layout", None),
    ("style", None),
]
_FILE_UPLOAD_PARAMS = [
    ("accept", ""),
    ("multiple", False),
    ("disabled", False),
    ("description", ""),
    ("icon", "upload"),
    ("button_style", ""),
    ("layout", None),
    ("style", None),
]
_IMAGE_PARAMS = [
    ("value", b""),
    ("format", "png"),
    ("width", ""),
    ("height", ""),
    ("layout", None),
]
_AUDIO_PARAMS = [
    ("value", b""),
    ("format", "mp3"),
    ("layout", None),
]
_VIDEO_PARAMS = [
    ("value", b""),
    ("format", "mp4"),
    ("width", ""),
    ("height", ""),
    ("layout", None),
]


for _cls, _summary, _params in [
    (Text, "Single-line text input control.", _TEXT_PARAMS),
    (Textarea, "Multiline text input control.", [*_TEXT_PARAMS, ("rows", None)]),
    (Password, "Password text input control.", _TEXT_PARAMS),
    (Combobox, "Text input with dropdown suggestions.", _COMBOBOX_PARAMS),
    (TagsInput, "List input for string tags.", _TAGS_INPUT_PARAMS),
    (ColorsInput, "List input for color tags.", _TAGS_INPUT_PARAMS),
    (FloatsInput, "List input for float values.", _TAGS_INPUT_PARAMS),
    (IntsInput, "List input for integer values.", _TAGS_INPUT_PARAMS),
    (Dropdown, "Dropdown selection control.", _SELECTION_PARAMS),
    (RadioButtons, "Radio-button selection control.", _SELECTION_PARAMS),
    (ToggleButtons, "Toggle-button selection control.", _TOGGLE_BUTTONS_PARAMS),
    (Select, "List-box single-selection control.", [*_SELECTION_PARAMS, ("rows", None)]),
    (SelectMultiple, "List-box multi-selection control.", [*_SELECTION_PARAMS, ("rows", None)]),
    (SelectionSlider, "Slider selection control.", _SELECTION_SLIDER_PARAMS),
    (SelectionRangeSlider, "Range slider selection control.", _SELECTION_SLIDER_PARAMS),
    (Button, "Clickable button control.", _BUTTON_PARAMS),
    (Checkbox, "Boolean checkbox control.", _CHECKBOX_PARAMS),
    (ToggleButton, "Boolean toggle-button control.", _TOGGLE_BUTTON_PARAMS),
    (Valid, "Boolean validity indicator control.", _VALID_PARAMS),
    (IntSlider, "Integer slider control.", _INT_SLIDER_PARAMS),
    (IntRangeSlider, "Integer range slider control.", _INT_RANGE_SLIDER_PARAMS),
    (IntText, "Integer text input control.", _NUMERIC_TEXT_PARAMS),
    (BoundedIntText, "Bounded integer text input control.", _BOUNDED_INT_TEXT_PARAMS),
    (FloatSlider, "Float slider control.", _FLOAT_SLIDER_PARAMS),
    (FloatRangeSlider, "Float range slider control.", _FLOAT_RANGE_SLIDER_PARAMS),
    (FloatLogSlider, "Logarithmic float slider control.", _FLOAT_LOG_SLIDER_PARAMS),
    (FloatText, "Float text input control.", _FLOAT_TEXT_PARAMS),
    (BoundedFloatText, "Bounded float text input control.", _BOUNDED_FLOAT_TEXT_PARAMS),
    (IntProgress, "Integer progress bar control.", _INT_PROGRESS_PARAMS),
    (FloatProgress, "Float progress bar control.", _FLOAT_PROGRESS_PARAMS),
    (Play, "Playback stepper control.", _PLAY_PARAMS),
    (DatePicker, "Date picker control.", _DATE_PARAMS),
    (TimePicker, "Time picker control.", _TIME_PARAMS),
    (DatetimePicker, "Datetime picker control.", _TIME_PARAMS),
    (ColorPicker, "Color picker control.", _COLOR_PICKER_PARAMS),
    (FileUpload, "File upload control.", _FILE_UPLOAD_PARAMS),
    (Image, "Image display widget.", _IMAGE_PARAMS),
    (Audio, "Audio display widget.", _AUDIO_PARAMS),
    (Video, "Video display widget.", _VIDEO_PARAMS),
    (Output, "Output capture and display widget.", [("layout", None)]),
    (HTML, "HTML display widget.", _TEXT_VALUE_PARAMS),
    (HTMLMath, "HTML and math display widget.", _TEXT_VALUE_PARAMS),
    (Label, "Plain text label widget.", _TEXT_VALUE_PARAMS),
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
