SEARCH = '''
import time

import anylumino.astryx as ax

SYMBOLS = [{"id": "nvda-1", "label": "NVIDIA"}, {"id": "amd-1", "label": "AMD"}, {"id": "intc-1", "label": "Intel"}]


def search(query):
    return [item for item in SYMBOLS if query.lower() in item["label"].lower()]


def slow_search(query):
    time.sleep(1.5)
    return search(query)
'''


def pick(nb, output, query, label):
    field = output.get_by_role("combobox")
    field.click()
    field.fill(query)
    option = nb.page.get_by_role("option", name=label)
    option.wait_for()
    option.click()
    nb.page.wait_for_timeout(500)


def test_typeahead_shows_a_pick_from_python_search(notebook):
    nb = notebook(SEARCH, "box = ax.Typeahead([], label='Symbol', search=search, debounce_ms=0)\nbox")
    output = nb.output(1)
    output.get_by_role("combobox").wait_for()

    pick(nb, output, "nvi", "NVIDIA")

    # Astryx shows the selected item as a token beside the input, not as the input text.
    assert nb.value("box.value") == "nvda-1"
    assert output.inner_text().split("\n") == ["Symbol", "NVIDIA"]


def test_tokenizer_adds_each_pick_from_python_search(notebook):
    nb = notebook(SEARCH, "tokens = ax.Tokenizer([], label='Symbols', search=search, debounce_ms=0)\ntokens")
    output = nb.output(1)
    output.get_by_role("combobox").wait_for()

    pick(nb, output, "nvi", "NVIDIA")
    pick(nb, output, "am", "AMD")

    assert nb.value("tokens.value") == ["nvda-1", "amd-1"]
    assert output.get_by_text("NVIDIA").count() >= 1
    assert output.get_by_text("AMD").count() >= 1


def test_trait_change_during_a_python_search_keeps_its_results(notebook):
    nb = notebook(SEARCH, "box = ax.Typeahead([], label='Symbol', search=slow_search, debounce_ms=0)\nbox")
    output = nb.output(1)
    field = output.get_by_role("combobox")
    field.wait_for()
    model_id = nb.value("box.model_id")

    field.click()
    field.fill("in")
    nb.page.wait_for_timeout(500)
    # The kernel is still in slow_search, so only the frontend sees this change mid-request.
    nb.set_frontend_trait(model_id, "label", "Ticker")

    nb.page.get_by_role("option", name="Intel").wait_for(timeout=10_000)
