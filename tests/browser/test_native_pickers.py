# Tracks the click listeners on `document`, including ones an abort signal removes.
COUNT_DOCUMENT_CLICKS = """
(() => {
  const add = EventTarget.prototype.addEventListener;
  const remove = EventTarget.prototype.removeEventListener;
  const active = new Set();
  window.__documentClicks = () => active.size;
  EventTarget.prototype.addEventListener = function (type, listener, options) {
    if (this === document && type === "click" && listener) {
      active.add(listener);
      options?.signal?.addEventListener("abort", () => active.delete(listener), { once: true });
    }
    return add.call(this, type, listener, options);
  };
  EventTarget.prototype.removeEventListener = function (type, listener, options) {
    if (this === document && type === "click") active.delete(listener);
    return remove.call(this, type, listener, options);
  };
})();
"""


def test_time_popup_starts_from_a_value_assigned_in_python(notebook):
    nb = notebook("import anylumino as al\npicker = al.TimePicker('14:30')\npicker")
    output = nb.output(0)
    output.locator(".anylumino-NativeTimeInput").wait_for()

    nb.execute("picker.value = '09:45'")
    nb.page.wait_for_function("() => document.querySelector('.anylumino-NativeTimeInput').value === '09:45'")
    output.get_by_role("button", name="Pick").click()
    output.locator(".anylumino-NativeTimeSelect").first.select_option("10")
    nb.page.wait_for_timeout(500)

    assert nb.value("picker.value") == "10:45"


def test_time_picker_releases_document_and_model_listeners(notebook):
    nb = notebook("import anylumino as al\npicker = al.TimePicker('14:30')\npicker", init_script=COUNT_DOCUMENT_CLICKS)
    nb.output(0).locator(".anylumino-NativeTimeInput").wait_for()
    model_id = nb.value("picker.model_id")
    rendered = nb.page.evaluate("() => window.__documentClicks()")
    listening = nb.model_listeners(model_id, "change:value")

    for index in range(20):
        nb.execute(f"picker.disabled = {index % 2 == 0}")
    nb.page.wait_for_timeout(500)
    toggled = nb.page.evaluate("() => window.__documentClicks()")
    nb.page.evaluate("() => window.jupyterapp.commands.execute('notebook:clear-all-cell-outputs')")
    nb.page.wait_for_timeout(1000)
    cleared = nb.page.evaluate("() => window.__documentClicks()")

    assert listening == 1
    assert toggled == rendered
    assert cleared == rendered - 1
    assert [nb.model_listeners(model_id, f"change:{name}") for name in ("value", "disabled", "continuous_update")] == [0, 0, 0]


def test_continuous_update_change_after_display_takes_effect(notebook):
    nb = notebook("import anylumino as al\npicker = al.DatePicker('2026-10-21')\npicker")
    nb.output(0).locator(".anylumino-NativeDateInput").wait_for()

    nb.execute("picker.continuous_update = False")
    nb.page.wait_for_timeout(300)
    edit = """(eventName) => {
      const field = document.querySelector('.anylumino-NativeDateInput');
      field.value = '2026-10-25';
      field.dispatchEvent(new Event(eventName));
    }"""
    nb.page.evaluate(edit, "input")
    nb.page.wait_for_timeout(500)
    while_editing = nb.value("picker.value")
    nb.page.evaluate(edit, "change")
    nb.page.wait_for_timeout(500)

    assert while_editing == "2026-10-21"
    assert nb.value("picker.value") == "2026-10-25"
