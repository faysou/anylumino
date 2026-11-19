import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";

const require = createRequire(import.meta.url);
const KATEX_CSS = require.resolve("katex/dist/katex.min.css");
const FONT_FACE = /@font-face\{([^}]*)\}/g;

function declaration(rule, name) {
  return rule.match(new RegExp(`(?:^|;)${name}:([^;]+)`))[1];
}

/**
 * anywidget injects a widget class's `_css` once per class, so @font-face
 * rules in the widget CSS repeat once per class on the page, and Chrome
 * restyles the whole document as it swaps between the copies while math
 * re-renders. This plugin takes KaTeX's @font-face rules out of its CSS and
 * turns them into the `katex-fonts` module: the woff2 bytes of every face,
 * which the bundle registers once per page through `document.fonts`.
 */
export const katexFonts = {
  name: "katex-fonts",
  setup(build) {
    build.onResolve({ filter: /^katex-fonts$/ }, () => ({ path: "katex-fonts", namespace: "katex-fonts" }));
    build.onLoad({ filter: /.*/, namespace: "katex-fonts" }, async () => {
      const css = await readFile(KATEX_CSS, "utf8");
      const faces = [...css.matchAll(FONT_FACE)].map(([, rule]) => ({
        family: declaration(rule, "font-family"),
        style: declaration(rule, "font-style"),
        weight: declaration(rule, "font-weight"),
        file: join(dirname(KATEX_CSS), declaration(rule, "src").match(/url\(([^)]+\.woff2)\)/)[1]),
      }));
      const imports = faces.map((face, index) => `import font${index} from ${JSON.stringify(face.file)};`);
      const entries = faces.map(
        ({ family, style, weight }, index) => `{ family: ${JSON.stringify(family)}, style: "${style}", weight: "${weight}", data: font${index} }`,
      );
      return {
        contents: `${imports.join("\n")}\nexport default [${entries.join(", ")}];\n`,
        loader: "js",
        resolveDir: dirname(KATEX_CSS),
      };
    });
    build.onLoad({ filter: /katex[\\/]dist[\\/]katex\.min\.css$/ }, async (args) => ({
      contents: (await readFile(args.path, "utf8")).replace(FONT_FACE, ""),
      loader: "css",
    }));
  },
};
