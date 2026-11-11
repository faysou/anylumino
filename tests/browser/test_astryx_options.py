def test_numeric_selector_options_render(notebook):
    nb = notebook("import anylumino.astryx as ax\nselector = ax.Selector([1, 5, 10], value=5, label='Size')\nselector")
    output = nb.output(0)
    output.get_by_text("Size").wait_for()
    nb.page.wait_for_timeout(1000)

    assert nb.frontend_errors() == []
    assert output.get_by_text("5").count() >= 1


def test_selection_slider_value_stays_a_string_after_a_move(notebook):
    nb = notebook("import anylumino.astryx as ax\nslider = ax.SelectionSlider([1, 2, 3], label='Level')\nslider")
    thumb = nb.output(0).get_by_role("slider")
    thumb.wait_for()

    initial = nb.value("slider.value")
    thumb.focus()
    nb.page.keyboard.press("ArrowRight")
    nb.page.wait_for_timeout(1000)

    assert initial == "1"
    assert nb.value("slider.value") == "2"
    assert nb.frontend_errors() == []


def test_unknown_component_name_renders_a_visible_error(notebook):
    nb = notebook("import anylumino.astryx as ax\nw = ax.Text('known')\nw")
    output = nb.output(0)
    output.get_by_text("known").wait_for()

    nb.execute("w.component_name = 'NoSuchComponent'")
    notice = output.locator(".anylumino-UnknownComponent")
    notice.wait_for()

    assert notice.inner_text().startswith('[anylumino] Unknown Astryx component "NoSuchComponent".')
