import { defaultKeymap, history, historyKeymap, indentWithTab } from "@codemirror/commands";
import { markdown, markdownLanguage } from "@codemirror/lang-markdown";
import { pythonLanguage } from "@codemirror/lang-python";
import { HighlightStyle, forceParsing, syntaxHighlighting } from "@codemirror/language";
import { EditorState } from "@codemirror/state";
import { EditorView, drawSelection, highlightActiveLine, keymap, lineNumbers } from "@codemirror/view";
import { Markdown } from "@astryxdesign/core/Markdown";
import { markdownSourceLinesPlugin } from "@astryxdesign/core/Markdown/plugins";
import { ResizeHandle, useResizable } from "@astryxdesign/core/Resizable";
import { tags } from "@lezer/highlight";
import React from "react";
import { setStringValue } from "./model.mjs";
import { MARKDOWN_EXTENSIONS } from "./markdown.mjs";

// The kernel gets the text once typing pauses, and at once when the editor loses focus, so a
// Save click right after an edit still writes it.
const SYNC_DELAY_MS = 300;
const ALIGN_PASSES = 8;
const PANE_MIN_PX = 160;
// CodeMirror parses only 100k characters past the visible lines, and scrolling within that range
// does not parse further, so a code block whose end lies past it never gets its language. The
// whole document is parsed when the text is set, up to this many milliseconds.
const PARSE_BUDGET_MS = 500;
const DOLLAR = 36;
const BACKTICK = 96;
const MATH_STYLE = tags.special(tags.string);

// Highlight the math forms the preview typesets: $`...`$ inline and $$ blocks.
const mathSyntax = {
  defineNodes: [
    { name: "InlineMath", style: MATH_STYLE },
    { name: "BlockMath", block: true, style: MATH_STYLE },
  ],
  parseInline: [
    {
      name: "InlineMath",
      before: "InlineCode",
      parse(cx, next, pos) {
        if (next !== DOLLAR || cx.char(pos + 1) !== BACKTICK) {
          return -1;
        }
        const end = cx.slice(pos + 2, cx.end).indexOf("`$");
        return end < 0 ? -1 : cx.addElement(cx.elt("InlineMath", pos, pos + end + 4));
      },
    },
  ],
  parseBlock: [
    {
      name: "BlockMath",
      before: "FencedCode",
      parse(cx, line) {
        if (line.text.trim() !== "$$") {
          return false;
        }
        const start = cx.lineStart;
        while (cx.nextLine()) {
          if (line.text.trim() === "$$") {
            cx.nextLine();
            break;
          }
        }
        cx.addElement(cx.elt("BlockMath", start, cx.prevLineEnd()));
        return true;
      },
    },
  ],
};

// The Astryx text colors are near black in the light themes, so tokens take the vivid data colors.
// Fenced code is highlighted in its own language. The bundle loads in one piece, so each language
// is imported up front instead of on demand.
function codeLanguage(info) {
  return /^(python|py)$/i.test(info.trim()) ? pythonLanguage : null;
}

const highlightStyle = HighlightStyle.define([
  { tag: tags.heading, color: "var(--color-data-categorical-blue)", fontWeight: "600" },
  { tag: tags.strong, fontWeight: "700" },
  { tag: tags.emphasis, fontStyle: "italic" },
  { tag: tags.strikethrough, textDecoration: "line-through" },
  { tag: [tags.link, tags.url], color: "var(--color-data-categorical-teal)" },
  { tag: tags.monospace, color: "var(--color-data-categorical-purple)" },
  { tag: MATH_STYLE, color: "var(--color-data-categorical-green)" },
  { tag: tags.quote, color: "var(--color-text-secondary)", fontStyle: "italic" },
  { tag: [tags.processingInstruction, tags.contentSeparator], color: "var(--color-data-categorical-orange)" },
  { tag: tags.comment, color: "var(--color-syntax-comment)" },
  { tag: [tags.keyword, tags.controlKeyword, tags.definitionKeyword, tags.moduleKeyword], color: "var(--color-data-categorical-purple)" },
  { tag: [tags.string, tags.docString], color: "var(--color-data-categorical-green)" },
  { tag: [tags.number, tags.bool, tags.null], color: "var(--color-data-categorical-orange)" },
  { tag: [tags.function(tags.variableName), tags.function(tags.definition(tags.variableName))], color: "var(--color-data-categorical-blue)" },
  { tag: [tags.className, tags.definition(tags.className)], color: "var(--color-data-categorical-teal)" },
  { tag: [tags.self, tags.special(tags.variableName)], color: "var(--color-data-categorical-red)" },
  { tag: [tags.operator, tags.punctuation], color: "var(--color-text-secondary)" },
]);

const editorTheme = EditorView.theme({
  "&": { fontSize: "13px", color: "var(--color-text-primary)", backgroundColor: "var(--color-background-surface)" },
  "&.cm-focused": { outline: "none" },
  ".cm-scroller": { fontFamily: "var(--font-family-code)", lineHeight: "1.5" },
  ".cm-content": { caretColor: "var(--color-text-primary)" },
  ".cm-gutters": { backgroundColor: "var(--color-background-muted)", color: "var(--color-text-secondary)", border: "none" },
  ".cm-activeLine, .cm-activeLineGutter": { backgroundColor: "var(--color-background-muted)" },
  ".cm-selectionBackground, &.cm-focused .cm-selectionBackground": { backgroundColor: "var(--color-accent-muted)" },
});

const PREVIEW_PLUGINS = [...MARKDOWN_EXTENSIONS.plugins, markdownSourceLinesPlugin];

/**
 * The innermost rendered block whose source lines hold `line`, or the last
 * block that starts before it when `line` falls between blocks. Blocks come
 * in document order, so their start lines never decrease.
 */
export function sourceBlock(blocks, line) {
  let holding = null;
  let preceding = null;
  for (const block of blocks) {
    const start = Number(block.dataset.sourceLine);
    if (start > line) {
      break;
    }
    preceding = block;
    if (Number(block.dataset.sourceLineEnd) >= line) {
      holding = block;
    }
  }
  return holding ?? preceding;
}

// Scroll the preview so the block of the caret line sits at the caret's height in the editor, and
// report whether it moved.
// In a code block the line itself is placed; in other tall blocks, a place in proportion to the
// line's position in the block's source lines.
function alignPreview(view, preview) {
  const head = view.state.selection.main.head;
  const line = view.state.doc.lineAt(head).number;
  const block = sourceBlock(preview.querySelectorAll("[data-source-line]"), line);
  const caret = view.coordsAtPos(head);
  if (!block || !caret) {
    return;
  }
  const start = Number(block.dataset.sourceLine);
  const end = Math.max(Number(block.dataset.sourceLineEnd), start);
  const box = block.getBoundingClientRect();
  // Astryx numbers code lines from 1 after the opening fence, which is the block's first line.
  const codeLine = block.querySelector(`pre code [data-line="${line - start}"]`);
  const top = codeLine?.getBoundingClientRect().top ?? box.top + Math.min((line - start) / (end - start + 1), 1) * box.height;
  const target = caret.top - view.scrollDOM.getBoundingClientRect().top;
  const before = preview.scrollTop;
  preview.scrollTop += top - preview.getBoundingClientRect().top - target;
  return Math.abs(preview.scrollTop - before) > 1;
}

function MarkdownEditorPaneView({ model, props }) {
  const value = String(model.get("value") ?? "");
  const [text, setText] = React.useState(value);
  const rendered = React.useDeferredValue(text);
  const container = React.useRef(null);
  const [span, setSpan] = React.useState(0);
  // Letting go of the handle near the left edge hides the editor, and near the right edge the
  // editor takes the full span, which hides the preview.
  const editorWidth = useResizable({
    defaultSize: "50%",
    minSize: 0,
    maxSize: "100%",
    collapsible: true,
    collapsedSize: PANE_MIN_PX,
    containerRef: container,
  });
  // At the full span the handle sits on the pane's right edge; the half of its grab zone over the
  // editor keeps it draggable.
  const full = span;
  const releaseHandle = () => {
    if (span > 0 && editorWidth.size > full - PANE_MIN_PX) {
      editorWidth.resize(full);
    }
  };
  const editorHost = React.useRef(null);
  const previewHost = React.useRef(null);
  const viewRef = React.useRef(null);
  const sent = React.useRef(value);
  const timer = React.useRef(null);
  const frame = React.useRef(0);

  // Blocks scrolled into view render at their real height in place of an estimate a frame or two
  // later, which moves the target, so alignment repeats until the preview stays put for two frames.
  const requestAlign = React.useCallback(() => {
    cancelAnimationFrame(frame.current);
    const step = (passes, still) => {
      frame.current = requestAnimationFrame(() => {
        if (!viewRef.current || !previewHost.current) {
          return;
        }
        const settled = alignPreview(viewRef.current, previewHost.current) ? 0 : still + 1;
        if (settled < 2 && passes > 1) {
          step(passes - 1, settled);
        }
      });
    };
    step(ALIGN_PASSES, 0);
  }, []);

  React.useEffect(() => {
    const flush = () => {
      if (timer.current === null) {
        return;
      }
      clearTimeout(timer.current);
      timer.current = null;
      sent.current = view.state.doc.toString();
      setStringValue(model, sent.current);
    };
    const view = new EditorView({
      parent: editorHost.current,
      state: EditorState.create({
        doc: sent.current,
        extensions: [
          lineNumbers(),
          history(),
          drawSelection(),
          highlightActiveLine(),
          EditorView.lineWrapping,
          keymap.of([...defaultKeymap, ...historyKeymap, indentWithTab]),
          markdown({ base: markdownLanguage, codeLanguages: codeLanguage, extensions: [mathSyntax] }),
          syntaxHighlighting(highlightStyle),
          editorTheme,
          EditorView.domEventHandlers({ blur: flush }),
          EditorView.updateListener.of((update) => {
            if (update.docChanged) {
              setText(update.state.doc.toString());
              clearTimeout(timer.current);
              timer.current = setTimeout(flush, SYNC_DELAY_MS);
            } else if (update.transactions.some((transaction) => transaction.isUserEvent("select"))) {
              requestAlign();
            }
          }),
        ],
      }),
    });
    // A theme height loses to the editor's own sizing, so the pane height is set on the element.
    view.dom.style.height = "100%";
    forceParsing(view, view.state.doc.length, PARSE_BUDGET_MS);
    viewRef.current = view;
    return () => {
      flush();
      cancelAnimationFrame(frame.current);
      view.destroy();
      viewRef.current = null;
    };
  }, [model, requestAlign]);

  // Text assigned from Python replaces the editor content; text the editor sent comes back unchanged.
  React.useEffect(() => {
    const view = viewRef.current;
    if (!view || value === sent.current) {
      return;
    }
    sent.current = value;
    if (value !== view.state.doc.toString()) {
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: value } });
      forceParsing(view, view.state.doc.length, PARSE_BUDGET_MS);
    }
  }, [value]);

  React.useEffect(() => {
    if (viewRef.current?.hasFocus) {
      requestAlign();
    }
  }, [rendered, requestAlign]);

  // Off-screen blocks start skipping layout only after the first full layout has painted.
  React.useEffect(() => {
    const id = requestAnimationFrame(() => {
      previewHost.current?.setAttribute("data-measured", "");
    });
    return () => cancelAnimationFrame(id);
  }, []);

  React.useEffect(() => {
    const observer = new ResizeObserver(([entry]) => setSpan(entry.contentRect.width));
    observer.observe(container.current);
    return () => observer.disconnect();
  }, []);

  const editorShown = editorWidth.size > 0;
  const previewShown = span === 0 || editorWidth.size < full;
  const preview = { flex: "1 1 0", minWidth: 0, height: "100%", overflow: "auto", padding: "0 12px", display: previewShown ? "block" : "none" };
  return React.createElement(
    "div",
    { ...props, ref: container, className: "anylumino-MarkdownEditorPane", style: { display: "flex", height: "100%", overflow: "hidden", ...props.style } },
    React.createElement("div", {
      ref: editorHost,
      style: {
        width: editorWidth.size,
        flexShrink: 0,
        height: "100%",
        overflow: "hidden",
        borderRadius: 6,
        border: editorShown ? "1px solid var(--color-border)" : "none",
      },
    }),
    React.createElement(
      "div",
      { onPointerUp: releaseHandle, style: { display: "flex", flexShrink: 0 } },
      React.createElement(ResizeHandle, { resizable: editorWidth, direction: "horizontal", label: "Resize editor and preview" }),
    ),
    React.createElement(
      "div",
      { ref: previewHost, className: "anylumino-MarkdownEditorPane-preview", style: preview },
      // Prose takes the full preview width, the bound tables and equations already have.
      React.createElement(Markdown, { components: MARKDOWN_EXTENSIONS.components, plugins: PREVIEW_PLUGINS, contentWidth: "100%" }, rendered),
    ),
  );
}

export const SPECS = {
  MarkdownEditorPane: { view: MarkdownEditorPaneView },
};
