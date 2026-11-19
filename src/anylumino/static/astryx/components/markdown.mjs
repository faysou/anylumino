import { CodeBlock } from "@astryxdesign/core/CodeBlock";
import { createMarkdownFenceTransform, createMarkdownPlugin } from "@astryxdesign/core/Markdown/plugins";
import { useTheme } from "@astryxdesign/core/theme";
import mermaid from "mermaid";
import React from "react";
import { MathExpression } from "./math.mjs";

const MERMAID_PLUGIN = "anylumino-mermaid";

// mermaid.render needs an element ID that is unique on the page.
let diagramCount = 0;

function MermaidDiagram({ code }) {
  const { mode } = useTheme();
  const [result, setResult] = React.useState(null);
  React.useEffect(() => {
    let cancelled = false;
    diagramCount += 1;
    mermaid.initialize({ startOnLoad: false, securityLevel: "strict", theme: mode === "dark" ? "dark" : "default" });
    mermaid.render(`anylumino-mermaid-${diagramCount}`, code).then(
      ({ svg }) => !cancelled && setResult({ svg }),
      (e) => !cancelled && setResult({ error: String(e?.message ?? e) }),
    );
    return () => {
      cancelled = true;
    };
  }, [code, mode]);
  if (result?.error) {
    return React.createElement(CodeBlock, { code: `%% ${result.error}\n${code}`, language: "mermaid" });
  }
  return React.createElement("div", {
    style: { display: "flex", justifyContent: "center", overflowX: "auto" },
    dangerouslySetInnerHTML: result ? { __html: result.svg } : undefined,
  });
}

const mermaidPlugin = createMarkdownPlugin({
  name: MERMAID_PLUGIN,
  apiVersion: 1,
  transform: createMarkdownFenceTransform({
    languages: ["mermaid"],
    createNode: ({ code }) => ({ type: "extension", plugin: MERMAID_PLUGIN, name: "diagram", display: "block", data: { code } }),
  }),
  renderers: {
    diagram: {
      render: ({ node }) => React.createElement(MermaidDiagram, { code: node.data.code }),
      toText: (node) => node.data.code,
    },
  },
});

/** Props every anylumino Markdown gets: KaTeX math and Mermaid diagrams. */
export const MARKDOWN_EXTENSIONS = { components: { math: MathExpression }, plugins: [mermaidPlugin] };
