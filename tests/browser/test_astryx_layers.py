import pytest


@pytest.mark.parametrize(
    "code",
    [
        "ax.Popover(ax.Text('layer content'), ax.Button('Details'), label='Details', open=True)",
        "ax.Tooltip(ax.Text('layer content'), ax.Button('Validate'), open=True)",
        "ax.HoverCard(ax.Text('layer content'), ax.Button('Run state'), open=True)",
    ],
    ids=["Popover", "Tooltip", "HoverCard"],
)
def test_open_layer_shows_its_widget_content(notebook, code):
    nb = notebook(f"import anylumino.astryx as ax\n{code}")

    nb.output(0).get_by_text("layer content", exact=True).wait_for(timeout=15_000)

    assert nb.frontend_errors() == []
