import { tableFromIPC } from "@uwdata/flechette";

export const SNAPSHOT = "tabulator-snapshot";
export const DELTA = "tabulator-delta";
export const EDIT = "tabulator-edit";
export const SELECT = "tabulator-select";
export const ROW_CLICK = "tabulator-row-click";

export const DeltaOp = Object.freeze({
  UPDATE: "update",
  ADD: "add",
  UPSERT: "upsert",
  DELETE: "delete",
});

export const Step = Object.freeze({
  // Replace every row with the snapshot's rows.
  REPLACE: "replace",
  // Apply the delta to the table.
  APPLY: "apply",
  // Take the delta's revision without applying it: this view made the change.
  ADVANCE: "advance",
  // The view missed a revision and needs a snapshot.
  RESYNC: "resync",
  IGNORE: "ignore",
});

/**
 * What a view at `revision` does with a row message. `revision` is `null` until
 * the view has applied its first snapshot, which already holds every earlier
 * delta.
 */
export function nextStep(revision, content, viewId) {
  if (content.type === SNAPSHOT) {
    return revision === null || content.revision > revision ? Step.REPLACE : Step.IGNORE;
  }
  if (revision === null || content.revision <= revision) {
    return Step.IGNORE;
  }
  if (content.revision !== revision + 1) {
    return Step.RESYNC;
  }
  return content.origin === viewId ? Step.ADVANCE : Step.APPLY;
}

/**
 * The rows a snapshot or delta carries: JSON rows, or an Arrow IPC stream in its
 * first binary buffer.
 */
export function messageRows(content, buffers) {
  if (content.format !== "arrow") {
    return content.rows ?? [];
  }
  const buffer = buffers?.[0];
  if (!buffer) {
    throw new Error("an Arrow row message arrived without its buffer");
  }
  const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer.buffer ?? buffer, buffer.byteOffset ?? 0, buffer.byteLength);
  return tableFromIPC(bytes).toArray();
}

/**
 * Whether a snapshot must rebuild a table's automatic columns. Tabulator builds
 * them from the first row on `setData` only; `replaceData`, which keeps scroll
 * and sort, leaves the columns as they are.
 */
export function rebuildsColumns(autoColumns, rows, fields) {
  if (!autoColumns || rows.length === 0) {
    return false;
  }
  const next = Object.keys(rows[0]);
  return next.length !== fields.length || next.some((field, index) => field !== fields[index]);
}

/**
 * Apply one delta to a Tabulator table and return the promise of the change.
 */
export function applyDelta(table, content, rows) {
  switch (content.op) {
    case DeltaOp.UPDATE:
      return table.updateData(rows);
    case DeltaOp.ADD:
      return table.addData(rows, Boolean(content.top));
    case DeltaOp.UPSERT:
      return table.updateOrAddData(rows);
    case DeltaOp.DELETE:
      return table.deleteRow(content.ids ?? []);
    default:
      throw new Error(`unknown row change ${content.op}`);
  }
}
