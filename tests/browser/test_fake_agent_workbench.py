from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_fake_agent_workbench_turn_fills_every_tab(notebook):
    nb = notebook(
        f"import sys\nsys.path.insert(0, {str(ROOT / 'notebooks')!r})",
        "import fake_agent\nworkbench = fake_agent.workbench()\nworkbench",
    )
    # The chat composer is a rich text editor, not a text field
    composer = nb.output(1).get_by_role("textbox", name="Message input")
    composer.wait_for()
    turns = nb.value("len(workbench.chat.messages)")

    composer.click()
    nb.page.keyboard.type("Build the sales explorer")
    nb.page.keyboard.press("Enter")
    nb.page.wait_for_function(
        "() => document.querySelector('.anylumino-AstryxWidgetHost') !== null", timeout=30_000
    )
    for _ in range(120):
        if nb.value("len(workbench.chat.messages)") >= turns + 2 and not nb.value("workbench.running"):
            break
        nb.page.wait_for_timeout(500)
    nb.page.wait_for_timeout(2000)

    assert nb.value("workbench.outcome") == "applied"
    assert nb.value("[bool(view.props['code']) for view in workbench.code_views.values()]") == [True, True, True]
    assert nb.value("workbench.status_text.text") == "Ready"
    assert nb.frontend_errors() == []
