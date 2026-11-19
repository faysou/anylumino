import fonts from "katex-fonts";

/**
 * Register KaTeX's fonts once for the page. Faces built from bytes load at
 * once, so math never waits on a font load that restyles the document when it
 * finishes, and `document.fonts` also serves widgets inside shadow roots.
 */
export function addKatexFonts(fontSet = globalThis.document?.fonts) {
  for (const { family, style, weight, data } of fonts) {
    fontSet?.add(new FontFace(family, data, { style, weight, display: "block" }));
  }
}
