"""Enums for the fixed option values of the Astryx widgets.

Each enum is a `StrEnum`, so a member compares equal to its string value and
syncs as that string. Keywords that take one accept the member or its value,
such as ``Size.SM`` or ``"sm"``, and reject any other value. `Orientation`
comes from `anylumino.enums`, since layout panels share it.
"""

from __future__ import annotations

from enum import StrEnum

from anylumino.enums import Orientation

__all__ = ["Orientation", "Align", "Axis", "BadgeVariant", "BannerStatus", "BreadcrumbsVariant", "ButtonVariant", "CalendarMode", "CardVariant", "CitationStyle", "ClickableCardVariant", "CollapseFrom", "ColorMode", "CompactDensity", "CompactSize", "Container", "ContentAlign", "Density", "DialogPurpose", "DialogVariant", "Display", "DisplayType", "DividerVariant", "FileInputMode", "FieldStatusType", "FontWeight", "FormDirection", "FrameHeight", "FrameVariant", "HourFormat", "IconColor", "IconSize", "IndicatorKind", "IndicatorState", "InputType", "ItemLayout", "Justify", "LabelPosition", "LabelSpacing", "LayerAlignment", "LayerPlacement", "ListStyle", "MediaType", "OverlayPosition", "OverlayTrigger", "ScrollAxis", "SectionVariant", "SelectionMode", "SelectorVariant", "Selects", "Size", "SortDirection", "SpinnerShade", "StatusPlacement", "StatusVariant", "SwitchLabelPosition", "TableDividers", "TextColor", "TextJustify", "TextOverflow", "TextSize", "TextType", "TextWrap", "TimerFormat", "TimestampFormat", "ToastPosition", "ToastType", "TokenColor", "TriggerDisplay", "ValueDisplay", "VerticalAlign", "Wrap"]


class Size(StrEnum):
    """The size of a control."""

    SM = "sm"
    MD = "md"
    LG = "lg"


class CompactSize(StrEnum):
    """The size of a control that has no large size."""

    SM = "sm"
    MD = "md"


class IconSize(StrEnum):
    """The size of an icon."""

    XSM = "xsm"
    SM = "sm"
    MD = "md"
    LG = "lg"


class TextSize(StrEnum):
    """The type scale step of a text."""

    XS4 = "4xs"
    XS3 = "3xs"
    XS2 = "2xs"
    XSM = "xsm"
    SM = "sm"
    BASE = "base"
    LG = "lg"
    XL = "xl"
    XL2 = "2xl"
    XL3 = "3xl"
    XL4 = "4xl"


class Density(StrEnum):
    """How tightly rows are spaced."""

    COMPACT = "compact"
    BALANCED = "balanced"
    SPACIOUS = "spacious"


class CompactDensity(StrEnum):
    """Whether content uses the default or the compact spacing."""

    DEFAULT = "default"
    COMPACT = "compact"


class Align(StrEnum):
    """Cross-axis alignment of a stack's children."""

    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"


class Justify(StrEnum):
    """Main-axis distribution of a stack's children."""

    START = "start"
    CENTER = "center"
    END = "end"
    BETWEEN = "between"
    AROUND = "around"
    EVENLY = "evenly"


class TextJustify(StrEnum):
    """The logical alignment of text."""

    START = "start"
    CENTER = "center"
    END = "end"


class ContentAlign(StrEnum):
    """The alignment of block content."""

    START = "start"
    CENTER = "center"


class Wrap(StrEnum):
    """Whether a stack's children wrap onto new lines."""

    NOWRAP = "nowrap"
    WRAP = "wrap"
    WRAP_REVERSE = "wrap-reverse"


class TextWrap(StrEnum):
    """How text wraps."""

    WRAP = "wrap"
    NOWRAP = "nowrap"
    BALANCE = "balance"
    PRETTY = "pretty"


class TextOverflow(StrEnum):
    """How long cell text is shown."""

    WRAP = "wrap"
    TRUNCATE = "truncate"


class TextType(StrEnum):
    """The typographic role of a text."""

    BODY = "body"
    LARGE = "large"
    LABEL = "label"
    SUPPORTING = "supporting"
    CODE = "code"
    DISPLAY_1 = "display-1"
    DISPLAY_2 = "display-2"
    DISPLAY_3 = "display-3"


class DisplayType(StrEnum):
    """The display scale of a heading."""

    DISPLAY_1 = "display-1"
    DISPLAY_2 = "display-2"
    DISPLAY_3 = "display-3"


class TextColor(StrEnum):
    """The theme color of a text."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    DISABLED = "disabled"
    PLACEHOLDER = "placeholder"
    ACCENT = "accent"
    INHERIT = "inherit"


class IconColor(StrEnum):
    """The theme color of an icon."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    DISABLED = "disabled"
    ACCENT = "accent"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INHERIT = "inherit"


class TokenColor(StrEnum):
    """The color of a token."""

    DEFAULT = "default"
    BLUE = "blue"
    CYAN = "cyan"
    GRAY = "gray"
    GREEN = "green"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    RED = "red"
    TEAL = "teal"
    YELLOW = "yellow"


class FontWeight(StrEnum):
    """The weight of a text."""

    NORMAL = "normal"
    MEDIUM = "medium"
    SEMIBOLD = "semibold"
    BOLD = "bold"


class Display(StrEnum):
    """Whether an element flows inline or as a block."""

    BLOCK = "block"
    INLINE = "inline"


class ButtonVariant(StrEnum):
    """The visual style of a button."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    GHOST = "ghost"
    DESTRUCTIVE = "destructive"


class BadgeVariant(StrEnum):
    """The color of a badge."""

    NEUTRAL = "neutral"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    BLUE = "blue"
    CYAN = "cyan"
    GREEN = "green"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    RED = "red"
    TEAL = "teal"
    YELLOW = "yellow"


class CardVariant(StrEnum):
    """The surface style of a card."""

    DEFAULT = "default"
    MUTED = "muted"
    BLUE = "blue"
    CYAN = "cyan"
    GRAY = "gray"
    GREEN = "green"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    RED = "red"
    TEAL = "teal"
    YELLOW = "yellow"


class ClickableCardVariant(StrEnum):
    """The surface style of a clickable or selectable card."""

    DEFAULT = "default"
    TRANSPARENT = "transparent"
    MUTED = "muted"
    BLUE = "blue"
    CYAN = "cyan"
    GRAY = "gray"
    GREEN = "green"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    RED = "red"
    TEAL = "teal"
    YELLOW = "yellow"


class SectionVariant(StrEnum):
    """The surface style of a section."""

    SECTION = "section"
    TRANSPARENT = "transparent"
    MUTED = "muted"


class StatusVariant(StrEnum):
    """The color of a status dot or progress bar."""

    ACCENT = "accent"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    NEUTRAL = "neutral"


class BannerStatus(StrEnum):
    """The status of a banner."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class BreadcrumbsVariant(StrEnum):
    """The text style of breadcrumbs."""

    DEFAULT = "default"
    SUPPORTING = "supporting"


class DividerVariant(StrEnum):
    """The weight of a divider."""

    SUBTLE = "subtle"
    STRONG = "strong"


class DialogVariant(StrEnum):
    """The size of a dialog."""

    STANDARD = "standard"
    FULLSCREEN = "fullscreen"


class DialogPurpose(StrEnum):
    """What a dialog asks for."""

    REQUIRED = "required"
    FORM = "form"
    INFO = "info"


class CitationStyle(StrEnum):
    """How a citation marker is shown."""

    LABEL = "label"
    NUMBER = "number"


class FieldStatusType(StrEnum):
    """The kind of message a field status shows."""

    ERROR = "error"
    WARNING = "warning"
    SUCCESS = "success"


class StatusPlacement(StrEnum):
    """Whether a field status is attached to its field or set apart."""

    ATTACHED = "attached"
    DETACHED = "detached"


class Container(StrEnum):
    """Whether a block shows as a card or a section."""

    CARD = "card"
    SECTION = "section"


class LabelPosition(StrEnum):
    """Where a field label sits."""

    TOP = "top"
    LEFT = "left"


class SwitchLabelPosition(StrEnum):
    """Which side of a switch its label sits on."""

    START = "start"
    END = "end"


class LabelSpacing(StrEnum):
    """How a switch label is spaced from the switch."""

    DEFAULT = "default"
    SPREAD = "spread"


class ItemLayout(StrEnum):
    """Whether items hug their content or fill the row."""

    HUG = "hug"
    FILL = "fill"


class FormDirection(StrEnum):
    """How a form lays out its fields."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    HORIZONTAL_LABELS = "horizontal-labels"


class ListStyle(StrEnum):
    """The marker of list items."""

    NONE = "none"
    DISC = "disc"
    DECIMAL = "decimal"
    CIRCLE = "circle"


class HourFormat(StrEnum):
    """The clock of a time input."""

    H12 = "12h"
    H24 = "24h"


class InputType(StrEnum):
    """The kind of text a text input takes."""

    TEXT = "text"
    PASSWORD = "password"
    EMAIL = "email"


class CalendarMode(StrEnum):
    """Whether a calendar picks a date or a range."""

    SINGLE = "single"
    RANGE = "range"


class FileInputMode(StrEnum):
    """Whether a file input shows a button or a drop zone."""

    INPUT = "input"
    DROPZONE = "dropzone"


class SelectionMode(StrEnum):
    """Whether one or several items can be chosen."""

    SINGLE = "single"
    MULTIPLE = "multiple"


class Selects(StrEnum):
    """Whether table rows can be selected, and how many."""

    NONE = ""
    SINGLE = "single"
    MULTIPLE = "multiple"


class SortDirection(StrEnum):
    """The sort order of a table column."""

    NONE = ""
    ASC = "asc"
    DESC = "desc"


class TableDividers(StrEnum):
    """Which lines separate table cells."""

    ROWS = "rows"
    COLUMNS = "columns"
    GRID = "grid"
    NONE = "none"


class VerticalAlign(StrEnum):
    """The vertical alignment of table cells."""

    MIDDLE = "middle"
    TOP = "top"
    BOTTOM = "bottom"


class TimestampFormat(StrEnum):
    """How a timestamp is written."""

    RELATIVE = "relative"
    AUTO = "auto"
    DATE = "date"
    DATE_TIME = "date_time"
    TIME = "time"
    SYSTEM_DATE = "system_date"
    SYSTEM_DATE_TIME = "system_date_time"
    SYSTEM_TIME = "system_time"


class TriggerDisplay(StrEnum):
    """How a multi-selector shows its chosen items."""

    COUNT = "count"
    LABELS = "labels"
    BADGES = "badges"


class ValueDisplay(StrEnum):
    """How a slider shows its value."""

    TOOLTIP = "tooltip"
    TEXT = "text"
    NONE = "none"


class SpinnerShade(StrEnum):
    """The color treatment of a spinner."""

    DEFAULT = "default"
    ON_MEDIA = "onMedia"
    SUBTLE = "subtle"
    INHERIT = "inherit"


class Axis(StrEnum):
    """Which axes a box centers on."""

    BOTH = "both"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class ScrollAxis(StrEnum):
    """Which axes a scroll box scrolls along."""

    BLOCK = "block"
    INLINE = "inline"
    BOTH = "both"


class LayerPlacement(StrEnum):
    """Where a tooltip, card, or menu opens relative to its anchor."""

    ABOVE = "above"
    BELOW = "below"
    START = "start"
    END = "end"


class LayerAlignment(StrEnum):
    """How a layer aligns along its placement side."""

    START = "start"
    CENTER = "center"
    END = "end"


class OverlayTrigger(StrEnum):
    """When an overlay shows."""

    ALWAYS = "always"
    HOVER = "hover"
    FOCUS = "focus"
    HOVER_OR_FOCUS = "hover-or-focus"


class OverlayPosition(StrEnum):
    """Where an overlay covers its media."""

    FILL = "fill"
    BOTTOM = "bottom"
    TOP = "top"


class MediaType(StrEnum):
    """The kind of media a lightbox shows."""

    IMAGE = "image"
    VIDEO = "video"


class ColorMode(StrEnum):
    """The color scheme of a theme."""

    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
    JUPYTERLAB = "jupyterlab"


class TimerFormat(StrEnum):
    """How a timer writes its elapsed time."""

    ELAPSED = "elapsed"
    CLOCK = "clock"


class ToastType(StrEnum):
    """The kind of message a toast shows."""

    INFO = "info"
    ERROR = "error"


class ToastPosition(StrEnum):
    """The viewport corner toasts stack in."""

    TOP_END = "topEnd"
    TOP_START = "topStart"
    BOTTOM_END = "bottomEnd"
    BOTTOM_START = "bottomStart"


class IndicatorKind(StrEnum):
    """The mark an indicator draws."""

    CHECK = "check"
    CHECKBOX = "checkbox"
    RADIO = "radio"


class IndicatorState(StrEnum):
    """The state an indicator shows."""

    UNCHECKED = "unchecked"
    CHECKED = "checked"
    INDETERMINATE = "indeterminate"


class FrameHeight(StrEnum):
    """Whether an app shell or layout fills its container or fits its content."""

    FILL = "fill"
    AUTO = "auto"


class FrameVariant(StrEnum):
    """The surface treatment of an app shell."""

    WASH = "wash"
    SURFACE = "surface"
    SECTION = "section"
    ELEVATED = "elevated"


class SelectorVariant(StrEnum):
    """The trigger style of a complex selector."""

    INPUT = "input"
    SECONDARY = "secondary"
    GHOST = "ghost"


class CollapseFrom(StrEnum):
    """Which end of an overflow list collapses first."""

    START = "start"
    END = "end"
