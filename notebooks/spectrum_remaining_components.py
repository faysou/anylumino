import anylumino.spectrum as sx
# %% [markdown]
# # Spectrum component wrappers

# %%
from anylumino import GridPanel
from anylumino import HBox
from anylumino import VBox


# %%
status = sx.Label("Ready")


def mark(name):
    def callback(_widget):
        status.value = f"{name} clicked"

    return callback


dialog = sx.DialogBox(
    {
        "body": VBox(
            {
                "text": sx.Label("This dialog is a composable anywidget."),
                "field": sx.Text(value="Notebook component", description="Name"),
                "enabled": sx.Switch(value=True, description="Enabled"),
                "close": sx.Button(description="Close", callbacks=[lambda _widget: dialog.hide()]),
            },
            spacing=8,
            height=180,
        )
    },
    title="Spectrum dialog",
    open=False,
)

open_dialog = sx.Button(
    description="Open dialog",
    icon="AddContent",
    callbacks=[lambda _widget: dialog.show()],
)

buttons = HBox(
    {
        "open": open_dialog,
        "clear": sx.ClearButton(callbacks=[mark("Clear")]),
        "close": sx.CloseButton(callbacks=[mark("Close")]),
        "infield": sx.InfieldButton("More", icon="ArrowDown", callbacks=[mark("Infield")]),
        "picker": sx.PickerButton("Pick", icon="ArrowDown", callbacks=[mark("Picker")]),
    },
    spacing=8,
    scroll=True,
    child_min_width=130,
    height=56,
    fit_content=True,
)

field_group = sx.FieldGroup(
    {
        "dataset": sx.Text(value="Greenhouse", description="Dataset"),
        "live": sx.Checkbox(value=True, description="Live"),
        "quality": sx.Badge(value="Good", variant="positive"),
    },
    orientation="horizontal",
)

surfaces = GridPanel(
    {
        "popover": sx.Popover(
            {"content": sx.Label("sx.Popover content can contain anywidget children.")},
            open=True,
            placement="bottom",
        ),
        "tooltip": sx.Tooltip(
            "sx.Tooltip content",
            {"trigger": sx.Button(description="sx.Tooltip trigger")},
            open=True,
            placement="top",
        ),
        "tray": sx.Tray(
            {"content": sx.Label("sx.Tray content rendered as a composed child.")},
            open=False,
        ),
        "overlay": sx.Overlay(
            {"content": sx.Label("sx.Overlay wrapper content.")},
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
        "icon": sx.Icon("HelpCircle", icon_size="l", label="Help"),
        "ui": sx.UIIcon("checkmark100", label="Checkmark"),
        "progress": sx.ProgressCircle(value=58, label="Progress"),
        "handle": sx.ColorHandle("#1473e6"),
        "loupe": sx.ColorLoupe("#1473e6", open=True),
        "checker": sx.OpacityCheckerboard(width=90, height=40),
        "element": sx.SpectrumElement("div", text="Generic element", attributes={"class": "custom-spectrum-element"}),
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
        "help": sx.HelpText("These wrappers are standalone anywidgets and can compose child anywidgets."),
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
