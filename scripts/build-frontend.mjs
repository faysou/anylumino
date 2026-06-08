import { readFile, writeFile } from "node:fs/promises";

import { build } from "esbuild";

const shared = {
  banner: {
    js: `if (!globalThis.__anyluminoSpectrumDefineGuard) {
  const define = globalThis.customElements?.define.bind(globalThis.customElements);
  if (define) {
    globalThis.customElements.define = (name, constructor, options) => {
      if (String(name).startsWith("sp-") && globalThis.customElements.get(name)) return;
      return define(name, constructor, options);
    };
    globalThis.__anyluminoSpectrumDefineGuard = true;
  }
}`,
  },
  bundle: true,
  format: "esm",
  minify: true,
  sourcemap: false,
  target: "es2022",
};

const entries = [
  ["src/anylumino/static/tab_panel.js", "src/anylumino/static/tab_panel.bundle.js"],
  ["src/anylumino/static/layout_panel.js", "src/anylumino/static/layout_panel.bundle.js"],
  ["src/anylumino/static/action_panel.js", "src/anylumino/static/action_panel.bundle.js"],
  ["src/anylumino/static/control_widget.js", "src/anylumino/static/control_widget.bundle.js"],
  ["src/anylumino/static/native_control_widget.js", "src/anylumino/static/native_control_widget.bundle.js"],
  ["src/anylumino/static/spectrum_widget.js", "src/anylumino/static/spectrum_widget.bundle.js"],
];

for (const [entryPoint, outfile] of entries) {
  await build({
    ...shared,
    entryPoints: [entryPoint],
    outfile,
  });
  if (outfile.endsWith("spectrum_widget.bundle.js")) {
    await normalizeGeneratedWhitespace(outfile);
  }
}

async function normalizeGeneratedWhitespace(outfile) {
  let text = await readFile(outfile, "utf8");
  text = text
    .replaceAll("Gs=`[ \t\n\\f\\r]`", 'Gs="[\\\\s]"')
    .replaceAll("[^ \t\n\\f\\r", "[^\\\\s");
  await writeFile(outfile, text);
}
