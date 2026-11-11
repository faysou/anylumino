import { DateTime } from "luxon";

import { reviveFunctions } from "./functions.mjs";

/**
 * The Tabulator constructor options for a widget's synced `columns`, `options`,
 * and `index`, rendered into `root`.
 */
export function tableOptions({ columns = [], options = {}, index }, root) {
  const revivedColumns = reviveFunctions(columns, "columns");
  const revivedOptions = reviveFunctions(options, "options");
  // Popups go to `document.body` by default, where a shadow root's styles do not reach.
  const inShadowRoot = typeof ShadowRoot !== "undefined" && root.getRootNode() instanceof ShadowRoot;
  return {
    height: "100%",
    ...(inShadowRoot ? { popupContainer: root } : {}),
    ...revivedOptions,
    dependencies: { ...revivedOptions.dependencies, luxon: { DateTime } },
    index,
    ...(revivedColumns.length > 0 ? { columns: revivedColumns } : { autoColumns: true }),
  };
}
