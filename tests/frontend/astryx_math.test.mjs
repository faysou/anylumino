import assert from "node:assert/strict";
import test from "node:test";

import katex from "katex";

import { mathHtml } from "../../src/anylumino/static/astryx/components/math.mjs";


test("protected inline math typesets the expression between the backticks", () => {
  assert.equal(mathHtml("`\\kappa(\\theta - v_t)`", "inline"), katex.renderToString("\\kappa(\\theta - v_t)"));
});

test("plain inline math and a lone backtick stay text", () => {
  assert.equal(mathHtml("x + y", "inline"), null);
  assert.equal(mathHtml("`", "inline"), null);
});

test("block math typesets in display mode", () => {
  assert.equal(mathHtml("\\frac{dF_t}{F_t}", "block"), katex.renderToString("\\frac{dF_t}{F_t}", { displayMode: true }));
  assert.match(mathHtml("\\frac{dF_t}{F_t}", "block"), /^<span class="katex-display">/);
});

test("invalid TeX renders KaTeX's error text instead of throwing", () => {
  assert.match(mathHtml("\\frac{", "block"), /class="katex-error"[^>]*>\\frac\{</);
  assert.match(mathHtml("`\\frac{`", "inline"), /class="katex-error"[^>]*>\\frac\{</);
});
