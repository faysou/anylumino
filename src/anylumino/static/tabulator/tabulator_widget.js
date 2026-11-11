import "tabulator-tables/dist/css/tabulator_simple.css";
import "./tabulator_widget.css";

import { TabulatorFull } from "tabulator-tables";

import { combineSignals, cssSize, modelListeners, removeModelListener, whenConnected } from "../layout/composition.js";
import { reviveFunctions } from "./functions.mjs";
import { tableOptions } from "./options.mjs";
import { EDIT, ROW_CLICK, SELECT, SNAPSHOT, Step, applyDelta, messageRows, nextStep, rebuildsColumns } from "./rows.mjs";

/**
 * Whether the grid fills the layout slot it renders in. A scroll box and a
 * `fit_content` panel size each slot to its child, so the grid keeps its own
 * height there.
 */
function fillsSlot(root) {
  const slot = root.parentElement;
  if (!slot?.matches(".anylumino-LayoutChild, .anylumino-TabPanelChild")) {
    return false;
  }
  if (slot.parentElement?.classList.contains("anylumino-scrollBox")) {
    return false;
  }
  return !slot.closest(".anylumino-LayoutHost, .anylumino-TabPanelHost")?.classList.contains("anylumino-mod-fitContent");
}

function showError(root, error) {
  const message = document.createElement("div");
  message.className = "anylumino-TabulatorError";
  message.textContent = `[anylumino] Tabulator could not be built: ${String(error?.message ?? error)}`;
  root.replaceChildren(message);
}

function sameValues(left, right) {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

/**
 * One Tabulator instance and the row messages it has applied. The view
 * replaces it when an option that Tabulator reads only at construction changes.
 */
class TableView {
  constructor(model, root, viewId) {
    this.model = model;
    this.root = root;
    this.viewId = viewId;
    this.revision = null;
    this.resyncing = false;
    this.queue = [];
    this.frame = 0;
    // Set while rows or the selection change from Python, so Tabulator's own
    // selection events are not reported back.
    this.syncingSelection = false;
    this.destroyed = false;

    this.autoColumns = (model.get("columns") ?? []).length === 0;

    const element = document.createElement("div");
    element.className = "anylumino-TabulatorTable";
    root.replaceChildren(element);
    this.table = new TabulatorFull(
      element,
      tableOptions({ columns: model.get("columns"), options: model.get("options"), index: model.get("index") }, root),
    );
    this.work = new Promise((resolve) => this.table.on("tableBuilt", resolve));
    this.table.on("rowSelectionChanged", (_data, rows) => this.selectionChanged(rows));
    this.table.on("cellEdited", (cell) => this.cellEdited(cell));
    this.table.on("rowClick", (_event, row) => model.send({ type: ROW_CLICK, row_id: row.getIndex() }));
    this.requestSnapshot();
  }

  requestSnapshot() {
    this.model.send({ type: SNAPSHOT });
  }

  receive(content, buffers) {
    this.queue.push([content, buffers]);
    if (!this.frame) {
      this.frame = requestAnimationFrame(() => {
        this.frame = 0;
        const batch = this.queue.splice(0);
        this.work = this.work.then(() => this.flush(batch)).catch((error) => console.error("[anylumino] Tabulator rows:", error));
      });
    }
  }

  // Applies one frame of row messages in a single repaint.
  async flush(batch) {
    if (this.destroyed) {
      return;
    }
    this.table.blockRedraw();
    this.syncingSelection = true;
    try {
      for (const [content, buffers] of batch) {
        const step = nextStep(this.revision, content, this.viewId);
        if (step === Step.REPLACE) {
          const rows = messageRows(content, buffers);
          const fields = this.table.getColumns().map((column) => column.getField());
          await (rebuildsColumns(this.autoColumns, rows, fields) ? this.table.setData(rows) : this.table.replaceData(rows));
          this.revision = content.revision;
          this.resyncing = false;
          this.applySelection();
        } else if (step === Step.APPLY) {
          await applyDelta(this.table, content, messageRows(content, buffers));
          this.revision = content.revision;
        } else if (step === Step.ADVANCE) {
          this.revision = content.revision;
        } else if (step === Step.RESYNC && !this.resyncing) {
          this.resyncing = true;
          this.requestSnapshot();
        }
      }
    } finally {
      this.syncingSelection = false;
      if (!this.destroyed) {
        this.table.restoreRedraw();
      }
    }
  }

  syncSelection() {
    this.work = this.work.then(() => {
      if (!this.destroyed && this.revision !== null) {
        this.applySelection();
      }
    });
  }

  applySelection() {
    const selected = this.model.get("selected") ?? [];
    const current = this.table.getSelectedRows().map((row) => row.getIndex());
    if (sameValues(selected, current)) {
      return;
    }
    const syncing = this.syncingSelection;
    this.syncingSelection = true;
    try {
      this.table.deselectRow();
      if (selected.length > 0) {
        this.table.selectRow(selected);
      }
    } finally {
      this.syncingSelection = syncing;
    }
  }

  selectionChanged(rows) {
    if (this.syncingSelection || this.revision === null) {
      return;
    }
    this.model.send({ type: SELECT, selected: rows.map((row) => row.getIndex()) });
  }

  cellEdited(cell) {
    this.model.send({
      type: EDIT,
      view: this.viewId,
      row_id: cell.getRow().getIndex(),
      field: cell.getField(),
      value: cell.getValue(),
      old_value: cell.getOldValue(),
    });
  }

  setColumns() {
    this.work = this.work.then(() => {
      if (!this.destroyed) {
        this.table.setColumns(reviveFunctions(this.model.get("columns"), "columns"));
      }
    });
    return this.work;
  }

  destroy() {
    this.destroyed = true;
    cancelAnimationFrame(this.frame);
    this.table.destroy();
  }
}

export default {
  async render({ model, el, signal }) {
    const root = document.createElement("div");
    root.className = "anylumino-Tabulator";
    const size = () => {
      const fill = fillsSlot(root);
      root.style.width = fill ? "100%" : cssSize(model.get("width"), "100%");
      root.style.height = fill ? "100%" : cssSize(model.get("height"), "320px");
    };
    size();
    el.replaceChildren(root);

    const controller = new AbortController();
    const viewSignal = signal ? combineSignals(signal, controller.signal) : controller.signal;
    if (!(await whenConnected(root, viewSignal))) {
      return;
    }
    // The slot a layout panel renders the grid in is known only once it is attached.
    size();

    // `crypto.randomUUID` exists only in secure contexts, which a notebook on plain HTTP is not.
    const viewId = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
    let view = null;
    const build = () => {
      view?.destroy();
      view = null;
      try {
        view = new TableView(model, root, viewId);
      } catch (error) {
        showError(root, error);
      }
    };
    const onMessage = (content, buffers) => {
      if (content?.type?.startsWith("tabulator-")) {
        view?.receive(content, buffers);
      }
    };
    const onColumns = () => {
      const columns = model.get("columns") ?? [];
      const previous = model.previous("columns") ?? [];
      // An empty column list means `autoColumns`, which Tabulator reads only at construction.
      if (!view || columns.length === 0 || previous.length === 0) {
        build();
        return;
      }
      view.setColumns().catch((error) => showError(root, error));
    };

    build();
    model.on("msg:custom", onMessage);
    const unbind = modelListeners(model, [
      ["options", build],
      ["index", build],
      ["columns", onColumns],
      ["selected", () => view?.syncSelection()],
      ["width", size],
      ["height", size],
    ]);
    viewSignal.addEventListener(
      "abort",
      () => {
        removeModelListener(model, "msg:custom", onMessage);
        unbind();
        view?.destroy();
      },
      { once: true },
    );
  },
};
