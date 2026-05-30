import pytest
import traitlets as t

from anylumino import TabPanel, TextWidget


def test_tab_panel_serializes_child_widgets_as_anywidget_refs() -> None:
    first = TextWidget("First")
    second = TextWidget("Second")

    panel = TabPanel([first, second], titles=["One", "Two"], selected_index=1)

    assert panel.get_state(key=["widgets", "titles", "selected_index"]) == {
        "widgets": [f"anywidget:{first.model_id}", f"anywidget:{second.model_id}"],
        "titles": ["One", "Two"],
        "selected_index": 1,
    }


def test_tab_panel_size_inputs_are_normalized_to_css_values() -> None:
    panel = TabPanel([TextWidget("Only")], width=0.5, height=240)

    assert panel.width == "50.0%"
    assert panel.height == "240px"


def test_tab_panel_requires_matching_titles() -> None:
    with pytest.raises(ValueError, match="titles must be empty"):
        TabPanel([TextWidget("Only")], titles=["One", "Two"])


def test_tab_panel_rejects_non_widget_children() -> None:
    panel = TabPanel()

    with pytest.raises(t.TraitError):
        panel.widgets = ["not a widget"]


def test_add_tab_appends_widget_and_title() -> None:
    panel = TabPanel()
    child = TextWidget("Added")

    panel.add_tab(child, "Added tab")

    assert panel.widgets == [child]
    assert panel.titles == ["Added tab"]


def test_add_tab_can_select_appended_widget() -> None:
    first = TextWidget("First")
    panel = TabPanel([first], titles=["First"])
    child = TextWidget("Added")

    panel.add_tab(child, "Added tab", select=True)

    assert panel.widgets == [first, child]
    assert panel.titles == ["First", "Added tab"]
    assert panel.selected_index == 1
