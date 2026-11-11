"""Browser tests for `al.Tabulator`: rendering, the row channel, events, and hosting."""

from __future__ import annotations


ROWS = """rows = [
    {"id": 1, "symbol": "ESZ6", "last": 5012.25, "qty": 3},
    {"id": 2, "symbol": "NQZ6", "last": 18011.5, "qty": -1},
    {"id": 3, "symbol": "RTYZ6", "last": 2310.1, "qty": 10},
]
"""
COLUMNS = """columns = [
    {"title": "Symbol", "field": "symbol"},
    {"title": "Last", "field": "last"},
    {"title": "Qty", "field": "qty", "editor": "number"},
]
"""


def cell_texts(output, field):
    return output.locator(f".tabulator-row .tabulator-cell[tabulator-field='{field}']").all_inner_texts()


def wait_for_cell(nb, field, text, index=0):
    nb.page.wait_for_function(
        """([field, text, index]) => {
          const grid = document.querySelectorAll('.anylumino-Tabulator')[index];
          const cells = grid?.querySelectorAll(`.tabulator-row .tabulator-cell[tabulator-field='${field}']`) ?? [];
          return [...cells].some((cell) => cell.textContent === text);
        }""",
        arg=[field, text, index],
    )


def wait_for_symbols(nb, symbols, index=0):
    nb.page.wait_for_function(
        """([symbols, index]) => {
          const grid = document.querySelectorAll('.anylumino-Tabulator')[index];
          const cells = grid?.querySelectorAll(".tabulator-row .tabulator-cell[tabulator-field='symbol']") ?? [];
          return JSON.stringify([...cells].map((cell) => cell.textContent)) === JSON.stringify(symbols);
        }""",
        arg=[symbols, index],
    )


def test_rows_and_columns_render(notebook):
    nb = notebook("import anylumino as al\n" + ROWS + COLUMNS + "table = al.Tabulator(rows, columns)\ntable")
    output = nb.output(0)
    wait_for_cell(nb, "symbol", "NQZ6")

    assert output.locator(".tabulator-col-title").all_inner_texts() == ["Symbol", "Last", "Qty"]
    assert cell_texts(output, "symbol") == ["ESZ6", "NQZ6", "RTYZ6"]
    assert nb.frontend_errors() == []


def test_deltas_reach_the_view(notebook):
    nb = notebook("import anylumino as al\n" + ROWS + COLUMNS + "table = al.Tabulator(rows, columns)\ntable")
    output = nb.output(0)
    wait_for_cell(nb, "symbol", "NQZ6")

    nb.execute("table.update_rows([{'id': 2, 'last': 18100.75}])")
    nb.execute("table.add_rows([{'id': 4, 'symbol': 'CLZ6', 'last': 71.2, 'qty': 1}], top=True)")
    nb.execute("table.upsert_rows([{'id': 1, 'qty': 5}, {'id': 5, 'symbol': 'GCZ6', 'last': 2650.0, 'qty': 2}])")
    nb.execute("table.delete_rows([3])")
    wait_for_symbols(nb, ["CLZ6", "ESZ6", "NQZ6", "GCZ6"])

    assert cell_texts(output, "last") == ["71.2", "5012.25", "18100.75", "2650"]
    assert cell_texts(output, "qty") == ["1", "5", "-1", "2"]
    assert nb.frontend_errors() == []


def test_second_view_and_rerun_show_current_rows(notebook):
    nb = notebook(
        "import anylumino as al\n" + ROWS + COLUMNS + "table = al.Tabulator(rows, columns)\ntable",
        "table.update_rows([{'id': 1, 'symbol': 'ESH7'}])\ntable",
    )
    wait_for_cell(nb, "symbol", "ESH7", index=1)
    wait_for_cell(nb, "symbol", "ESH7", index=0)

    assert cell_texts(nb.output(0), "symbol") == ["ESH7", "NQZ6", "RTYZ6"]
    assert cell_texts(nb.output(1), "symbol") == ["ESH7", "NQZ6", "RTYZ6"]


def test_revision_gap_resyncs_from_a_snapshot(notebook):
    nb = notebook("import anylumino as al\n" + ROWS + COLUMNS + "table = al.Tabulator(rows, columns)\ntable")
    wait_for_cell(nb, "symbol", "NQZ6")

    # A lost message: the view never sees revision 1.
    nb.execute("table._revision += 1\ntable.update_rows([{'id': 3, 'symbol': 'RTYH7'}])")
    wait_for_cell(nb, "symbol", "RTYH7")

    assert cell_texts(nb.output(0), "symbol") == ["ESZ6", "NQZ6", "RTYH7"]


def test_data_assignment_keeps_sort(notebook):
    nb = notebook("import anylumino as al\n" + ROWS + COLUMNS + "table = al.Tabulator(rows, columns)\ntable")
    output = nb.output(0)
    wait_for_cell(nb, "symbol", "NQZ6")
    header = output.locator(".tabulator-col[tabulator-field='last'] .tabulator-col-title")
    header.click()
    nb.page.wait_for_function(
        "() => document.querySelector(\".tabulator-col[tabulator-field='last']\").getAttribute('aria-sort') === 'ascending'"
    )

    nb.execute("table.data = [{'id': 7, 'symbol': 'B', 'last': 2.0}, {'id': 8, 'symbol': 'A', 'last': 1.0}, {'id': 9, 'symbol': 'C', 'last': 3.0}]")
    wait_for_cell(nb, "symbol", "C")

    assert cell_texts(output, "symbol") == ["A", "B", "C"]


def test_selection_syncs_both_ways(notebook):
    nb = notebook(
        "import anylumino as al\n" + ROWS + COLUMNS
        + "table = al.Tabulator(rows, columns, options={'selectableRows': True})\n"
        + "calls = []\ntable.on_select(lambda item: calls.append(list(item.selected)))\ntable"
    )
    output = nb.output(0)
    wait_for_cell(nb, "symbol", "NQZ6")

    output.locator(".tabulator-row", has_text="RTYZ6").locator("[tabulator-field='symbol']").click()
    nb.page.wait_for_timeout(500)
    from_view = nb.value("[table.selected, calls]")
    nb.execute("table.selected = [1, 2, 99]")
    nb.page.wait_for_function("() => document.querySelectorAll('.tabulator-row.tabulator-selected').length === 2")
    selected_texts = output.locator(".tabulator-row.tabulator-selected [tabulator-field='symbol']").all_inner_texts()

    assert from_view == [[3], [[3]]]
    assert selected_texts == ["ESZ6", "NQZ6"]
    assert nb.value("[table.selected, calls]") == [[1, 2], [[3]]]


def test_cell_edit_reaches_python_and_a_second_view(notebook):
    nb = notebook(
        "import anylumino as al\n" + ROWS + COLUMNS
        + "table = al.Tabulator(rows, columns)\nedits = []\n"
        + "table.on_edit(lambda item, edit: edits.append([edit.row_id, edit.field, edit.value, edit.old_value]))\ntable",
        "table",
    )
    wait_for_cell(nb, "symbol", "NQZ6", index=1)
    cell = nb.output(0).locator(".tabulator-row", has_text="ESZ6").locator("[tabulator-field='qty']")
    cell.click()
    editor = cell.locator("input")
    editor.fill("12")
    editor.press("Enter")
    wait_for_cell(nb, "qty", "12", index=1)

    assert nb.value("edits") == [[1, "qty", 12, 3]]
    assert nb.value("table.data[0]['qty']") == 12
    assert cell_texts(nb.output(1), "qty") == ["12", "-1", "10"]


def test_row_click_runs_action_callbacks(notebook):
    nb = notebook(
        "import anylumino as al\n" + ROWS + COLUMNS
        + "table = al.Tabulator(rows, columns)\nclicked = []\n"
        + "table.on_action(lambda item, row: clicked.append(row['symbol']))\ntable"
    )
    wait_for_cell(nb, "symbol", "NQZ6")

    nb.output(0).locator(".tabulator-row", has_text="NQZ6").locator("[tabulator-field='symbol']").click()
    nb.page.wait_for_timeout(500)

    assert nb.value("clicked") == ["NQZ6"]


def test_hidden_tab_revealed_fills_its_panel(notebook):
    nb = notebook(
        "import anylumino as al\n" + ROWS + COLUMNS
        + "table = al.Tabulator(rows, columns, options={'layout': 'fitColumns'})\n"
        + "tabs = al.TabPanel([al.TextWidget('first'), table], titles=['Text', 'Grid'], height=360)\ntabs"
    )
    output = nb.output(0)
    output.locator(".lm-TabBar-tab", has_text="Text").wait_for()

    output.locator(".lm-TabBar-tab", has_text="Grid").click()
    wait_for_cell(nb, "symbol", "NQZ6")
    nb.page.wait_for_timeout(300)
    sizes = nb.page.evaluate(
        """() => {
          const grid = document.querySelector('.anylumino-Tabulator');
          const header = grid.querySelector('.tabulator-header');
          const row = grid.querySelector('.tabulator-row');
          return { grid: grid.getBoundingClientRect().width, header: header.getBoundingClientRect().width,
                   row: row.getBoundingClientRect().height };
        }"""
    )

    assert sizes["grid"] > 600
    assert abs(sizes["header"] - sizes["grid"]) <= 2
    assert sizes["row"] > 10
    assert nb.frontend_errors() == []


def test_split_panel_resize_refits_columns(notebook):
    nb = notebook(
        "import anylumino as al\n" + ROWS + COLUMNS
        + "table = al.Tabulator(rows, columns, options={'layout': 'fitColumns'})\n"
        + "split = al.SplitPanel([al.TextWidget('left'), table], sizes=[0.5, 0.5], height=300)\nsplit"
    )
    wait_for_cell(nb, "symbol", "NQZ6")
    width = "() => document.querySelector('.anylumino-Tabulator .tabulator-header').getBoundingClientRect().width"
    before = nb.page.evaluate(width)

    columns = "() => [...document.querySelectorAll('.anylumino-Tabulator .tabulator-col')].reduce((sum, col) => sum + col.getBoundingClientRect().width, 0)"

    nb.execute("split.sizes = [0.2, 0.8]")
    # The header widens first; Tabulator refits the columns on its next resize observation.
    nb.page.wait_for_function(f"() => ({width})() > {before} + 100 && Math.abs(({columns})() - ({width})()) <= 3")

    assert nb.page.evaluate(width) > before + 100


def luminance(color):
    red, green, blue = (int(part) for part in color[color.index("(") + 1 : color.index(")")].split(",")[:3])

    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def test_theme_follows_jupyterlab(notebook):
    nb = notebook("import anylumino as al\n" + ROWS + COLUMNS + "table = al.Tabulator(rows, columns)\ntable")
    wait_for_cell(nb, "symbol", "NQZ6")
    colors = """() => {
      const row = document.querySelector('.anylumino-Tabulator .tabulator-row');
      const style = getComputedStyle(row);
      return [style.backgroundColor, getComputedStyle(row.querySelector('.tabulator-cell')).color];
    }"""
    light = nb.page.evaluate(colors)

    nb.page.evaluate("() => window.jupyterapp.commands.execute('apputils:change-theme', { theme: 'JupyterLab Dark' })")
    nb.page.wait_for_function("() => document.body.dataset.jpThemeLight === 'false'")
    nb.page.wait_for_function(f"(light) => JSON.stringify(({colors})()) !== JSON.stringify(light)", arg=light)
    dark = nb.page.evaluate(colors)
    nb.page.evaluate("() => window.jupyterapp.commands.execute('apputils:change-theme', { theme: 'JupyterLab Light' })")

    assert luminance(light[0]) > 200
    assert luminance(light[1]) < 100
    assert luminance(dark[0]) < 80
    assert luminance(dark[1]) > 150


def test_arrow_and_json_transports_give_equal_rows(notebook):
    nb = notebook(
        "import anylumino as al\nimport pandas as pd\nfrom datetime import datetime\n"
        "frame = pd.DataFrame({'symbol': ['ESZ6', 'NQZ6'], 'last': [5012.25, float('nan')], 'qty': [3, -1],"
        " 'live': [True, False], 'ts': [datetime(2026, 11, 11, 9, 30), None], 'note': [None, 'halt']})\n"
        "typed = {'columnDefaults': {'formatter': al.JsCode('function(cell) { const v = cell.getValue(); return typeof v + \":\" + JSON.stringify(v); }')}}\n"
        "arrow = al.Tabulator(frame, transport='arrow', options=typed)\n"
        "plain = al.Tabulator(frame, transport='json', options=typed)\n"
        "al.VBox([arrow, plain], height=520)"
    )
    wait_for_cell(nb, "symbol", 'string:"NQZ6"', index=0)
    wait_for_cell(nb, "symbol", 'string:"NQZ6"', index=1)
    rows = """(index) => [...document.querySelectorAll('.anylumino-Tabulator')[index].querySelectorAll('.tabulator-row')]
      .map((row) => Object.fromEntries([...row.querySelectorAll('.tabulator-cell')]
        .map((cell) => [cell.getAttribute('tabulator-field'), cell.textContent])))"""

    arrow_rows = nb.page.evaluate(rows, 0)

    assert arrow_rows == nb.page.evaluate(rows, 1)
    assert arrow_rows == [
        {"symbol": 'string:"ESZ6"', "last": "number:5012.25", "qty": "number:3", "live": "boolean:true",
         "ts": 'string:"2026-11-11T09:30:00"', "note": "object:null", "id": "number:0"},
        {"symbol": 'string:"NQZ6"', "last": "object:null", "qty": "number:-1", "live": "boolean:false",
         "ts": "object:null", "note": 'string:"halt"', "id": "number:1"},
    ]


def test_grid_fills_a_layout_slot_and_keeps_its_height_in_a_scroll_box(notebook):
    nb = notebook(
        "import anylumino as al\n"
        "a = al.Tabulator([{'id': 1, 's': 'x'}], height=320)\nb = al.Tabulator([{'id': 1, 's': 'y'}], height=320)\n"
        "al.VBox([a, b], height=500)",
        "c = al.Tabulator([{'id': 1, 's': 'z'}], height=200)\nal.BoxPanel([c], scroll=True, height=150)",
    )
    wait_for_cell(nb, "s", "y", index=1)
    wait_for_cell(nb, "s", "z", index=2)
    sizes = nb.page.evaluate(
        """() => [...document.querySelectorAll('.anylumino-Tabulator')].map((grid) =>
          [Math.round(grid.getBoundingClientRect().height), Math.round(grid.parentElement.getBoundingClientRect().height)])"""
    )

    assert sizes[0][0] == sizes[0][1] and sizes[1][0] == sizes[1][1]
    assert 200 < sizes[0][0] < 320
    assert sizes[2][0] == 200


def test_columns_derived_from_data_follow_new_fields(notebook):
    nb = notebook("import anylumino as al\ntable = al.Tabulator([{'id': 1, 'symbol': 'ESZ6'}])\ntable")
    output = nb.output(0)
    wait_for_cell(nb, "symbol", "ESZ6")
    first = output.locator(".tabulator-col-title").all_inner_texts()

    nb.execute("table.data = [{'id': 1, 'symbol': 'ESZ6', 'last': 5012.25}]")
    wait_for_cell(nb, "last", "5012.25")

    assert first == ["id", "symbol"]
    assert output.locator(".tabulator-col-title").all_inner_texts() == ["id", "symbol", "last"]


def test_js_code_formatter_sorter_and_menu_action(notebook):
    nb = notebook(
        "import anylumino as al\n" + ROWS
        + "columns = [\n"
        "    {'title': 'Symbol', 'field': 'symbol', 'headerMenu': [{'label': 'Hide', 'action': al.JsCode('(event, column) => column.hide()')}]},\n"
        "    {'title': 'Last', 'field': 'last', 'formatter': al.JsCode('function(cell) { return cell.getValue().toFixed(1) + \" pts\"; }')},\n"
        "    {'title': 'Qty', 'field': 'qty', 'sorter': al.JsCode('(a, b) => Math.abs(a) - Math.abs(b)')},\n"
        "]\n"
        "table = al.Tabulator(rows, columns)\ntable"
    )
    output = nb.output(0)
    wait_for_cell(nb, "last", "5012.3 pts")
    formatted = cell_texts(output, "last")

    output.locator(".tabulator-col[tabulator-field='qty'] .tabulator-col-title").click()
    wait_for_symbols(nb, ["NQZ6", "ESZ6", "RTYZ6"])
    output.locator(".tabulator-col[tabulator-field='symbol'] .tabulator-header-popup-button").click()
    # Outside a shadow root, Tabulator places menus on the document body.
    nb.page.locator(".tabulator-menu-item", has_text="Hide").click()
    nb.page.wait_for_function(
        "() => getComputedStyle(document.querySelector(\".tabulator-col[tabulator-field='symbol']\")).display === 'none'"
    )

    assert formatted == ["5012.3 pts", "18011.5 pts", "2310.1 pts"]
    assert nb.frontend_errors() == []


def test_invalid_js_code_shows_an_error_naming_the_option(notebook):
    nb = notebook(
        "import anylumino as al\n"
        "table = al.Tabulator([{'id': 1}], [{'field': 'id', 'formatter': al.JsCode('not a function (')}])\ntable"
    )
    error = nb.output(0).locator(".anylumino-TabulatorError")
    error.wait_for()

    assert error.inner_text().startswith("[anylumino] Tabulator could not be built: columns[0].formatter: ")
    assert nb.output(0).locator(".tabulator").count() == 0


def test_datetime_formatter_and_sorter_by_name(notebook):
    nb = notebook(
        "import anylumino as al\nfrom datetime import datetime\n"
        "rows = [{'id': 1, 'ts': datetime(2026, 11, 11, 9, 30)}, {'id': 2, 'ts': datetime(2026, 1, 5, 16, 0)}, {'id': 3, 'ts': datetime(2026, 6, 1, 12, 0)}]\n"
        "columns = [{'title': 'Time', 'field': 'ts', 'formatter': 'datetime',"
        " 'formatterParams': {'inputFormat': 'iso', 'outputFormat': 'dd/MM/yyyy'},"
        " 'sorter': 'datetime', 'sorterParams': {'format': 'iso'}}]\n"
        "table = al.Tabulator(rows, columns)\ntable"
    )
    output = nb.output(0)
    wait_for_cell(nb, "ts", "11/11/2026")
    formatted = cell_texts(output, "ts")

    output.locator(".tabulator-col[tabulator-field='ts'] .tabulator-col-title").click()
    nb.page.wait_for_function(
        "() => document.querySelector(\".tabulator-row .tabulator-cell[tabulator-field='ts']\").textContent === '05/01/2026'"
    )

    assert formatted == ["11/11/2026", "05/01/2026", "01/06/2026"]
    assert cell_texts(output, "ts") == ["05/01/2026", "01/06/2026", "11/11/2026"]
    assert not [text for text in nb.console_errors if "dependency" in text.lower()]


def test_ten_hertz_stream_ends_on_the_last_values(notebook):
    nb = notebook(
        "import anylumino as al\n"
        "table = al.Tabulator([{'id': n, 'symbol': f'S{n}', 'last': 0.0} for n in range(20)], [{'field': 'symbol'}, {'field': 'last'}])\ntable"
    )
    wait_for_cell(nb, "symbol", "S1")

    nb.execute(
        "import time\n"
        "for tick in range(1, 51):\n"
        "    table.upsert_rows([{'id': n, 'last': float(tick * 100 + n)} for n in range(0, 20, 3)])\n"
        "    time.sleep(0.1)"
    )
    wait_for_cell(nb, "last", "5018")

    expected = [str(5000 + n) if n % 3 == 0 else "0" for n in range(20)]
    assert cell_texts(nb.output(0), "last")[:20] == expected
    assert nb.value("table.revision") == 50
    assert nb.frontend_errors() == []
