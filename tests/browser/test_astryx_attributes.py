import pytest


def test_dropdown_menu_label_assigned_after_display_updates_the_button(notebook):
    nb = notebook("import anylumino.astryx as ax\nmenu = ax.DropdownMenu([{'label': 'Open'}], label='Actions')\nmenu")
    output = nb.output(0)
    output.get_by_role("button", name="Actions").wait_for()

    nb.execute("menu.label = 'More actions'")

    output.get_by_role("button", name="More actions").wait_for()
    assert output.get_by_role("button", name="Actions", exact=True).count() == 0


@pytest.mark.parametrize(
    ("code", "role"),
    [
        ("ax.Pagination(5, disabled=True)", "button"),
        ("ax.ButtonGroup([{'label': 'One'}, {'label': 'Two'}], label='Group', disabled=True)", "button"),
    ],
)
def test_disabled_container_disables_its_controls(notebook, code, role):
    nb = notebook(f"import anylumino.astryx as ax\n{code}")
    controls = nb.output(0).get_by_role(role)
    controls.first.wait_for()

    states = [control.is_disabled() for control in controls.all()]
    assert states and all(states)


@pytest.mark.parametrize(("disabled", "opens"), [(True, False), (False, True)])
def test_context_menu_opens_only_when_enabled(notebook, disabled, opens):
    nb = notebook(
        "import anylumino.astryx as ax\n"
        f"ax.ContextMenu([{{'label': 'Copy row'}}], ax.Text('Right-click here'), disabled={disabled})"
    )
    target = nb.output(0).get_by_text("Right-click here")
    target.wait_for()

    target.click(button="right")
    nb.page.wait_for_timeout(500)

    # JupyterLab answers a right-click the widget does not take with its own Lumino menu.
    astryx_items = nb.page.locator("[role=menuitem]:not(.lm-Menu-item)", has_text="Copy row")
    assert (astryx_items.count() > 0) is opens
