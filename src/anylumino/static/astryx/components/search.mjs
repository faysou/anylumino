import { createStaticSource } from "@astryxdesign/core/Typeahead";
import { removeModelListener } from "../../layout/composition.js";
import { itemLabel } from "./items.mjs";
import { asArray } from "./model.mjs";

let searchRequestCounter = 0;

// Items a model has shown from a Python search or had picked, by id. The value
// syncs only ids, so a pick from search results that are gone needs its item here.
const knownItems = new WeakMap();

// One Python search source per model. Astryx treats a new source object as a new
// source and cancels its pending search, so a render must not replace it.
const pythonSources = new WeakMap();

export function searchableItems(items) {
  return asArray(items).map((item, index) => {
    if (item && typeof item === "object") {
      const id = String(item.id ?? item.value ?? item.label ?? index);
      return {
        ...item,
        id,
        label: itemLabel(item, `Item ${index + 1}`),
      };
    }
    return {
      id: String(item ?? index),
      label: String(item ?? `Item ${index + 1}`),
    };
  });
}

/**
 * Keep `items` as known items of `model`, so the controlled value can show them
 * after the search results that held them change.
 */
export function rememberItems(model, items) {
  let known = knownItems.get(model);
  if (known === undefined) {
    known = new Map();
    knownItems.set(model, known);
  }
  for (const item of asArray(items)) {
    if (item?.id != null) {
      known.set(String(item.id), item);
    }
  }
}

export function requestPythonSearch(model, query) {
  const requestId = `${model.model_id ?? "model"}-${Date.now()}-${++searchRequestCounter}`;
  return new Promise((resolve) => {
    let settled = false;
    const finish = (items) => {
      if (settled) {
        return;
      }
      settled = true;
      clearTimeout(timeout);
      removeModelListener(model, "msg:custom", onMessage);
      const results = searchableItems(items);
      rememberItems(model, results);
      resolve(results);
    };
    const onMessage = (content) => {
      if (content?.type !== "search-results" || String(content.request_id ?? "") !== requestId) {
        return;
      }
      finish(content.items ?? []);
    };
    const timeout = setTimeout(() => finish([]), 10000);
    model.on("msg:custom", onMessage);
    model.send({ type: "search", request_id: requestId, query: String(query ?? "") });
  });
}

export function searchSourceFor(model, items) {
  if (String(model.get("search_mode") || "static") !== "python") {
    return createStaticSource(items);
  }
  let source = pythonSources.get(model);
  if (source === undefined) {
    source = {
      search: (query) => requestPythonSearch(model, query),
      bootstrap: () => requestPythonSearch(model, ""),
    };
    pythonSources.set(model, source);
  }
  return source;
}

/**
 * The item for id `value`: from the component's items, from the items the model
 * has shown or had picked, or, in a view that has seen neither, the id itself.
 */
function knownItem(model, items, value) {
  const id = String(value);
  return items.find((item) => String(item.id) === id) ?? knownItems.get(model)?.get(id) ?? { id, label: id };
}

export function selectedSearchItem(model, items, value) {
  if (value == null || value === "") {
    return null;
  }
  return knownItem(model, items, value);
}

export function selectedSearchItems(model, items, value) {
  return asArray(value).map((id) => knownItem(model, items, id));
}
