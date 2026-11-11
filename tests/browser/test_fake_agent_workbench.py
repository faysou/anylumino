from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


GRID_PROGRAM = """root = VBox([grid, bump])
grid = Tabulator([], [{title: "Region", field: "region"}, {title: "Revenue", field: "revenue", formatter: {"$js": "function(cell) { return cell.getValue().toFixed(2); }"}}], {height: 220})
bump = Button("Bump first row", @Callback("on_bump"))"""

GRID_CALLBACKS = """from anylumino.workbench import App


class GridApp(App):
    def setup(self):
        self.ui.grid.data = self.sales.to_dict("records")

    def on_bump(self, event):
        self.ui.grid.update_rows([{"id": 0, "revenue": 9.5}])
"""

GRID_REPLY = f"Here is a grid.\n\n```openui-lang\n{GRID_PROGRAM}\n```\n\n```python\n{GRID_CALLBACKS}```"


def send_turn(nb, text):
    # The chat composer is a rich text editor, not a text field
    composer = nb.output(1).get_by_role("textbox", name="Message input")
    composer.wait_for()
    turns = nb.value("len(workbench.chat.messages)")

    composer.click()
    nb.page.keyboard.type(text)
    nb.page.keyboard.press("Enter")
    for _ in range(120):
        if nb.value("len(workbench.chat.messages)") >= turns + 2 and not nb.value("workbench.running"):
            break
        nb.page.wait_for_timeout(500)


def test_fake_agent_workbench_turn_fills_every_tab(notebook):
    nb = notebook(
        f"import sys\nsys.path.insert(0, {str(ROOT / 'notebooks')!r})",
        "import fake_agent\nworkbench = fake_agent.workbench()\nworkbench",
    )

    send_turn(nb, "Build the sales explorer")
    nb.page.wait_for_function(
        "() => document.querySelector('.anylumino-AstryxWidgetHost') !== null", timeout=30_000
    )
    nb.page.wait_for_timeout(2000)

    assert nb.value("workbench.outcome") == "applied"
    assert nb.value("[bool(view.props['code']) for view in workbench.code_views.values()]") == [True, True, True]
    assert nb.value("workbench.status_text.text") == "Ready"
    assert nb.frontend_errors() == []


def test_fake_agent_program_places_a_tabulator_that_callbacks_update(notebook):
    nb = notebook(
        f"import sys\nsys.path.insert(0, {str(ROOT / 'notebooks')!r})",
        f"import fake_agent\nworkbench = fake_agent.workbench({GRID_REPLY!r})\nworkbench",
    )

    send_turn(nb, "Build a grid")
    revenue = ".anylumino-Tabulator .tabulator-row .tabulator-cell[tabulator-field='revenue']"
    nb.page.wait_for_function(f"() => document.querySelector(\"{revenue}\")?.textContent === '1.50'", timeout=30_000)
    nb.output(1).get_by_role("button", name="Bump first row").click()
    nb.page.wait_for_function(f"() => document.querySelector(\"{revenue}\").textContent === '9.50'")

    assert nb.value("workbench.outcome") == "applied"
    assert nb.page.evaluate(f"() => [...document.querySelectorAll(\"{revenue}\")].map((cell) => cell.textContent)") == [
        "9.50", "2.00", "3.20", "0.80", "1.10",
    ]
    assert nb.frontend_errors() == []
