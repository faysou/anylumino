import katex from "katex";
import React from "react";

/**
 * Typeset Markdown math in the portable forms: inline math as $`...`$ and
 * display math as a $$ block. Astryx keeps the backticks in an inline
 * expression; one without them, a plain $...$, returns null so it shows as the
 * text it was written as. Invalid TeX renders as KaTeX's error text instead of
 * throwing, so one bad expression never blanks the whole document.
 */
export function mathHtml(value, display) {
  if (display === "block") {
    return katex.renderToString(value, { displayMode: true, throwOnError: false });
  }
  if (value.length > 1 && value.startsWith("`") && value.endsWith("`")) {
    return katex.renderToString(value.slice(1, -1), { throwOnError: false });
  }
  return null;
}

export function MathExpression({ value, display, sourceLines }) {
  const html = React.useMemo(() => mathHtml(value, display), [value, display]);
  if (html === null) {
    return `$${value}$`;
  }
  if (display === "block") {
    // Block math carries its source lines like Astryx's own blocks, so the editor pane can find it.
    const lines = sourceLines ? { "data-source-line": sourceLines.start, "data-source-line-end": sourceLines.end } : {};
    return React.createElement("div", { ...lines, style: { overflowX: "auto" }, dangerouslySetInnerHTML: { __html: html } });
  }
  return React.createElement("span", { dangerouslySetInnerHTML: { __html: html } });
}
