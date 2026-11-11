CHILD_GAP_JS = """(output) => {
  const children = [...output.querySelectorAll(".anylumino-LayoutChild")];
  const [first, second] = children.map((child) => child.getBoundingClientRect());
  return Math.round(second.top - first.bottom);
}"""


def test_scroll_box_separates_children_by_spacing(notebook):
    nb = notebook(
        "import anylumino as al\n"
        "al.BoxPanel([al.TextWidget('one'), al.TextWidget('two')], direction='top-to-bottom', "
        "scroll=True, spacing=20, height=200)"
    )
    output = nb.output(0)
    output.get_by_text("two").wait_for()

    assert output.evaluate(CHILD_GAP_JS) == 20


def test_toolbar_renders_a_separator_between_buttons(notebook):
    nb = notebook(
        "import anylumino as al\n"
        "al.Toolbar([{'id': 'run', 'label': 'Run'}, {'separator': True}, {'id': 'stop', 'label': 'Stop'}])"
    )
    output = nb.output(0)
    output.get_by_text("Stop").wait_for()

    assert output.locator(".anylumino-ToolbarButton").all_inner_texts() == ["Run", "Stop"]
    assert output.locator(".anylumino-ToolbarSeparator").count() == 1


def test_menu_renders_both_separator_spellings(notebook):
    nb = notebook(
        "import anylumino as al\n"
        "al.MenuBar([{'label': 'File', 'items': [\n"
        "    {'id': 'open', 'label': 'Open'}, {'separator': True},\n"
        "    {'id': 'save', 'label': 'Save'}, {'type': 'separator'},\n"
        "    {'id': 'close', 'label': 'Close'},\n"
        "]}])"
    )
    output = nb.output(0)
    output.get_by_text("File").click()
    menu = nb.page.locator(".lm-Menu")
    menu.get_by_text("Close").wait_for()

    assert menu.locator(".lm-Menu-item[data-type='separator']").count() == 2
    assert menu.locator(".lm-Menu-item[data-type='command'] .lm-Menu-itemLabel").all_inner_texts() == [
        "Open",
        "Save",
        "Close",
    ]


ICON_PATH_JS = """(menu) => menu.querySelector(".lm-Menu-itemIcon svg path")?.getAttribute("d") ?? null"""


def test_menus_sharing_an_action_id_keep_their_own_icons(notebook):
    nb = notebook(
        "import anylumino as al",
        "al.MenuBar([{'label': 'First', 'items': [{'id': 'open', 'label': 'Open', 'icon': 'Star'}]}])",
        "al.MenuBar([{'label': 'Second', 'items': [{'id': 'open', 'label': 'Open', 'icon': 'Upload'}]}])",
    )
    paths = []
    for index, label in ((1, "First"), (2, "Second")):
        nb.output(index).get_by_text(label).click()
        menu = nb.page.locator(".lm-Menu")
        menu.get_by_text("Open").wait_for()
        nb.page.wait_for_timeout(300)
        paths.append(menu.evaluate(ICON_PATH_JS))
        nb.page.keyboard.press("Escape")
        menu.wait_for(state="detached")

    assert paths == ["m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8-6.2-3.2L5.8 21 7 14.2 2 9.3l6.9-1Z", "M12 16V3"]
