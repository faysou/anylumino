import assert from "node:assert/strict";
import test from "node:test";

import { sourceBlock } from "../../src/anylumino/static/astryx/components/markdown_editor.mjs";


// Blocks in document order, a list holding two items, as the preview tags them.
const blocks = [
  ["heading", 1, 1],
  ["list", 3, 6],
  ["first item", 3, 4],
  ["second item", 5, 6],
  ["paragraph", 9, 12],
].map(([name, start, end]) => ({ name, dataset: { sourceLine: String(start), sourceLineEnd: String(end) } }));

test("a line inside nested blocks maps to the innermost one", () => {
  assert.equal(sourceBlock(blocks, 4).name, "first item");
  assert.equal(sourceBlock(blocks, 5).name, "second item");
  assert.equal(sourceBlock(blocks, 11).name, "paragraph");
});

test("a line between blocks maps to the last block before it", () => {
  assert.equal(sourceBlock(blocks, 2).name, "heading");
  assert.equal(sourceBlock(blocks, 8).name, "second item");
  assert.equal(sourceBlock(blocks, 40).name, "paragraph");
});

test("no block starts at or before the line", () => {
  assert.equal(sourceBlock(blocks.slice(1), 2), null);
});
