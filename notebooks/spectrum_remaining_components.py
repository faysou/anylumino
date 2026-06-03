# %% [markdown]
# # Spectrum component wrappers

# %%
from anylumino import Badge
from anylumino import Button
from anylumino import Checkbox
from anylumino import ClearButton
from anylumino import CloseButton
from anylumino import ColorHandle
from anylumino import ColorLoupe
from anylumino import DialogBox
from anylumino import FieldGroup
from anylumino import GridPanel
from anylumino import HBox
from anylumino import HelpText
from anylumino import Icon
from anylumino import InfieldButton
from anylumino import Label
from anylumino import OpacityCheckerboard
from anylumino import Overlay
from anylumino import PickerButton
from anylumino import Popover
from anylumino import ProgressCircle
from anylumino import SpectrumElement
from anylumino import Switch
from anylumino import Text
from anylumino import Tooltip
from anylumino import Tray
from anylumino import UIIcon
from anylumino import VBox


# %%
status = Label("Ready")


def mark(name):
    def callback(_widget):
        status.value = f"{name} clicked"

    return callback


dialog = DialogBox(
    {
        "body": VBox(
            {
                "text": Label("This dialog is a composable anywidget."),
                "field": Text(value="Notebook component", description="Name"),
                "enabled": Switch(value=True, description="Enabled"),
                "close": Button(description="Close", callbacks=[lambda _widget: dialog.hide()]),
            },
            spacing=8,
            height=180,
        )
    },
    title="Spectrum dialog",
    open=False,
)

open_dialog = Button(
    description="Open dialog",
    icon="AddContent",
    callbacks=[lambda _widget: dialog.show()],
)

buttons = HBox(
    {
        "open": open_dialog,
        "clear": ClearButton(callbacks=[mark("Clear")]),
        "close": CloseButton(callbacks=[mark("Close")]),
        "infield": InfieldButton("More", icon="ArrowDown", callbacks=[mark("Infield")]),
        "picker": PickerButton("Pick", icon="ArrowDown", callbacks=[mark("Picker")]),
    },
    spacing=8,
    scroll=True,
    child_min_width=130,
    height=56,
    fit_content=True,
)

field_group = FieldGroup(
    {
        "dataset": Text(value="Greenhouse", description="Dataset"),
        "live": Checkbox(value=True, description="Live"),
        "quality": Badge(value="Good", variant="positive"),
    },
    orientation="horizontal",
)

surfaces = GridPanel(
    {
        "popover": Popover(
            {"content": Label("Popover content can contain anywidget children.")},
            open=True,
            placement="bottom",
        ),
        "tooltip": Tooltip(
            "Tooltip content",
            {"trigger": Button(description="Tooltip trigger")},
            open=True,
            placement="top",
        ),
        "tray": Tray(
            {"content": Label("Tray content rendered as a composed child.")},
            open=False,
        ),
        "overlay": Overlay(
            {"content": Label("Overlay wrapper content.")},
            open=True,
            placement="bottom",
        ),
    },
    columns="1fr 1fr",
    gap=12,
    height=260,
)

visuals = HBox(
    {
        "icon": Icon("HelpCircle", icon_size="l", label="Help"),
        "ui": UIIcon("checkmark100", label="Checkmark"),
        "progress": ProgressCircle(value=58, label="Progress"),
        "handle": ColorHandle("#1473e6"),
        "loupe": ColorLoupe("#1473e6", open=True),
        "checker": OpacityCheckerboard(width=90, height=40),
        "element": SpectrumElement("div", text="Generic element", attributes={"class": "custom-spectrum-element"}),
    },
    spacing=12,
    scroll=True,
    child_min_width=110,
    height=96,
    fit_content=True,
)

app = VBox(
    {
        "buttons": buttons,
        "status": status,
        "field-group": field_group,
        "help": HelpText("These wrappers are standalone anywidgets and can compose child anywidgets."),
        "visuals": visuals,
        "surfaces": surfaces,
        "dialog": dialog,
    },
    spacing=10,
    stretches=[0, 0, 0, 0, 0, 1, 0],
    height=680,
    fit_content=True,
)

app

# %%
