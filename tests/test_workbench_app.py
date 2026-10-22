import pytest

import dataclasses

import plotly.graph_objects as go

import anylumino.astryx as ax
from anylumino import TabPanel
from anylumino.workbench import App, Event, View


class CountingApp(App):
    def on_add(self, event):
        self.total += event.value

    def on_fail(self, event):
        raise KeyError(event.source)


def test_namespace_keywords_become_attributes_and_handlers_run_without_a_ui():
    app = CountingApp(total=1, label="sales")
    app.call("on_add", Event("add", 2))
    assert (app.total, app.label, app.ui) == (3, "sales", None)


@pytest.mark.parametrize("name", ["ui", "agent", "on_error", "set_ui", "setup", "call", "ask_agent", "on_add", "_private"])
def test_namespace_names_cannot_replace_app_members(name):
    with pytest.raises(ValueError, match=f"^{name!r} cannot be an App namespace name; it is not an identifier or the App uses it$"):
        CountingApp(**{name: 1})


def test_set_ui_keeps_the_ui_and_runs_setup():
    class SetupApp(App):
        def setup(self):
            self.ready = self.ui

    app = SetupApp()
    ui = object()
    app.set_ui(ui)
    assert (app.ui, app.ready) == (ui, ui)


def test_set_ui_copies_what_setup_adds_to_a_figure_into_its_synced_state():
    class ChartApp(App):
        def setup(self):
            self.ui.chart.add_trace(go.Bar(x=["FX", "Rates"], y=[4.0, 3.5]))
            self.ui.chart.layout.title.text = "Revenue"

    class ChartView(View):
        def __init__(self, app):
            self.app = app
            self.chart = go.FigureWidget()
            self.widget = ax.Stack([self.chart])
            app.set_ui(self)

    view = ChartView(ChartApp())

    assert [(trace["type"], trace["x"], trace["y"]) for trace in view.chart._widget_data] == [("bar", ["FX", "Rates"], [4.0, 3.5])]
    assert view.chart._widget_layout["title"] == {"text": "Revenue"}


def test_handler_errors_raise_without_on_error_and_go_to_it_when_set():
    app = CountingApp()
    with pytest.raises(KeyError, match="'fail'"):
        app.call("on_fail", Event("fail"))

    errors = []
    app.on_error = lambda handler, error: errors.append((handler, repr(error)))
    app.call("on_fail", Event("fail"))
    assert errors == [("on_fail", "KeyError('fail')")]


def test_ask_agent_uses_the_attached_agent_or_warns():
    app = CountingApp()
    with pytest.warns(UserWarning, match="^No workbench is attached, so ask_agent ignored 'Sum'.$"):
        app.ask_agent("Sum")

    asked = []
    app.agent = lambda message, context: asked.append((message, context))
    app.ask_agent("Sum", {"rows": 2})
    assert asked == [("Sum", {"rows": 2})]


def test_an_app_drives_one_ui():
    app = CountingApp()
    first = object()
    app.set_ui(first)
    app.set_ui(first)

    with pytest.raises(RuntimeError, match="^This CountingApp already drives a UI; create a new app for each UI.$"):
        app.set_ui(object())

    assert app.ui is first


def test_event_fields_are_read_only_and_default_to_none():
    event = Event("go")

    with pytest.raises(dataclasses.FrozenInstanceError):
        event.value = 1

    assert (event.source, event.value, event.context) == ("go", None, None)


def test_a_view_shows_and_composes_as_its_widget():
    class LabelView(View):
        def __init__(self, app):
            self.app = app
            self.label = ax.Text("Sales")
            self.widget = ax.Stack([self.label])
            app.set_ui(self)

    view = LabelView(CountingApp())
    tabs = TabPanel([view], titles=["Sales"])

    assert view._repr_mimebundle_() == view.widget._repr_mimebundle_()
    assert (tabs.widgets, tabs.get_owner(0), view.label.text) == ([view.widget], view, "Sales")
