ROW_CHECKBOXES_JS = """(output) => [...output.querySelectorAll("tr")].slice(1).map((row) =>
  row.querySelectorAll("input[type=checkbox]").length)"""


def test_row_flag_outside_the_columns_blocks_selection(notebook):
    nb = notebook(
        "import anylumino.astryx as ax\n"
        "table = ax.Table([{'id': 'x', 'a': 1, 'selectable': False}, {'id': 'y', 'a': 2}], "
        "columns=['a'], selects='multiple')\n"
        "table"
    )
    output = nb.output(0)
    output.get_by_text("Select all rows").wait_for(state="attached")

    assert output.evaluate(ROW_CHECKBOXES_JS) == [0, 1]
    assert nb.frontend_errors() == []


def test_select_all_label_names_the_select_all_checkbox(notebook):
    nb = notebook(
        "import anylumino.astryx as ax\n"
        "ax.Table([{'id': 'x', 'a': 1}], columns=['a'], selects='multiple', select_all_label='Pick every row')"
    )
    output = nb.output(0)

    output.get_by_text("Pick every row").wait_for(state="attached")
    assert output.get_by_text("Select all rows").count() == 0
