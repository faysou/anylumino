import marimo

__generated_with = "0.25.2"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    mo.md(
        """
        # OpenUI workbench in marimo

        Runs the fake-agent workbench of `fake_agent.py`, shared with
        `openui_workbench_fake_agent.py`, in marimo to check that anylumino
        widgets and the workbench work outside JupyterLab. A fake `codex` on
        `PATH` answers every turn with a sales explorer, so no agent tokens are
        spent.

        Start it with `uv run --no-sync marimo edit notebooks/marimo_workbench_fake_agent.py`,
        then type any message in the chat. Check that:

        - the tabs of the workbench and of the generated UI switch, and only the
          selected tab shows;
        - `setup` fills the table with all five `sales` rows;
        - choosing a region updates the heading, badge, and table, and the button
          writes the total under the table.

        The workbench builds a reply's UI in an asyncio task that a chat
        message starts after this cell has run. That needs a marimo version
        that runs widget messages as part of the cell that created the widget.
        marimo 0.25.2 does not, so the reply reports an `AssertionError`.
        """
    )
    return


@app.cell
def _():
    import fake_agent

    workbench = fake_agent.workbench()
    workbench
    return


if __name__ == "__main__":
    app.run()
