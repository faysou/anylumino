def test_text_widget_renders_and_kernel_answers(notebook):
    nb = notebook("import anylumino as al\nw = al.TextWidget('hello browser')\nw")

    nb.output(0).get_by_text("hello browser").wait_for()
    nb.execute("w.value = 'changed'")
    nb.output(0).get_by_text("changed").wait_for()

    assert nb.value("w.value") == "changed"
    assert nb.frontend_errors() == []
