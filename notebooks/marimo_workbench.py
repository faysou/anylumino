import marimo

__generated_with = "0.25.2"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    mo.md(
        """
        # OpenUI workbench in marimo

        Chat with `claude` or `codex` on the left to build a UI on the right.
        The `sales` data frame is in the namespace, so callbacks can read it.
        Set `AGENT` to the CLI you have signed in to. Every turn spends agent
        tokens.

        Start it with `uv run --no-sync marimo edit notebooks/marimo_workbench.py`.
        Try: "Show the sales table, a region selector, and a button that writes
        the total revenue of the selected region under the table."

        Rerunning the workbench cell stops its turn thread, which cancels a
        reply in progress.
        """
    )
    return


@app.cell
def _():
    import pandas as pd

    from anylumino.workbench import Workbench

    AGENT = "claude"

    sales = pd.DataFrame(
        {
            "region": ["EMEA", "APAC", "AMER", "EMEA", "APAC"],
            "product": ["Rates", "Rates", "FX", "FX", "Credit"],
            "revenue": [1.5, 2.0, 3.2, 0.8, 1.1],
        }
    )

    workbench = Workbench(agent=AGENT, session="marimo-sales-demo", namespace={"sales": sales})
    workbench
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
