PROBE = '''
import anywidget


class Probe(anywidget.AnyWidget):
    """A child that counts its renders and its live views in the page."""

    _esm = """
    export default {
      render({ el, signal }) {
        const counts = (globalThis.__probe ??= { renders: 0, live: 0 });
        counts.renders += 1;
        counts.live += 1;
        el.textContent = `probe ${counts.renders}`;
        let released = false;
        const release = () => {
          if (!released) {
            released = true;
            counts.live -= 1;
          }
        };
        signal?.addEventListener("abort", release, { once: true });
        return release;
      },
    };
    """
'''

COUNTS_JS = "() => globalThis.__probe ?? { renders: 0, live: 0 }"


def test_split_panel_child_inside_an_unselected_tab_keeps_its_view(notebook):
    nb = notebook(
        PROBE,
        "import anylumino.astryx as ax\n"
        "tabs = ax.TabPanel({'split': ax.SplitPanel({'left': Probe(), 'right': ax.Text('right pane')}, height=120), "
        "'other': ax.Text('other tab')})\n"
        "tabs",
    )
    output = nb.output(1)
    output.get_by_text("probe 1").wait_for()

    for _ in range(3):
        output.locator("[data-tab-value=other]").click()
        output.get_by_text("other tab").wait_for()
        output.locator("[data-tab-value=split]").click()
        output.get_by_text("right pane").wait_for()
        nb.page.wait_for_timeout(300)

    assert nb.page.evaluate(COUNTS_JS) == {"renders": 1, "live": 1}
    assert output.get_by_text("probe 1").is_visible()


def test_inline_dialog_reopened_keeps_one_live_child_view(notebook):
    nb = notebook(PROBE, "import anylumino.astryx as ax\ndialog = ax.Dialog(Probe(), open=True, width=320)\ndialog")
    output = nb.output(1)
    output.get_by_text("probe 1").wait_for()

    for _ in range(10):
        nb.execute("dialog.hide()")
        nb.page.wait_for_timeout(150)
        nb.execute("dialog.show()")
        nb.page.wait_for_timeout(150)
    output.get_by_text("probe").wait_for()

    assert nb.page.evaluate(COUNTS_JS)["live"] == 1
