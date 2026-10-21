import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { basename } from "node:path";

import { build } from "esbuild";

import { entries, shared } from "./bundle-entries.mjs";

// Astryx declares its design tokens on `:root`, which never matches inside a
// shadow root. Hosts such as marimo adopt the widget CSS into one, so the
// tokens also need to land on the shadow host for the rules to resolve.
async function scopeRootTokensToHost(cssFile) {
  let css;
  try {
    css = await readFile(cssFile, "utf8");
  } catch (error) {
    if (error.code === "ENOENT") {
      return;
    }
    throw error;
  }
  await writeFile(cssFile, css.replaceAll(/:root(?=[\s,{])/g, ":root,:host"));
}

// anywidget imports a widget's `_esm` as its own module for every widget model,
// so each widget would hold its own copy of the bundle and its libraries. The
// widgets load a small loader instead: the first one on a page asks Python for
// the bundle with an `anylumino-bundle` message (`SharedBundleWidget`) and
// imports it once, and the module is kept on `globalThis` under a key that
// changes with the bundle content, so every later widget reuses it.
function loaderSource(outfile, code) {
  const hash = createHash("sha256").update(code).digest("hex").slice(0, 16);
  const key = JSON.stringify(`anylumino:${basename(outfile)}:${hash}`);
  return `const key = Symbol.for(${key});

function load(model) {
  globalThis[key] ??= new Promise((resolve, reject) => {
    const onMessage = (content) => {
      if (content?.type !== "anylumino-bundle") {
        return;
      }
      try {
        model.off("msg:custom", onMessage);
      } catch {
        model.off("msg:custom", onMessage, null);
      }
      const url = URL.createObjectURL(new Blob([content.code], { type: "text/javascript" }));
      import(url).then((module) => resolve(module.default), reject).finally(() => URL.revokeObjectURL(url));
    };
    model.on("msg:custom", onMessage);
    model.send({ type: "anylumino-bundle" });
  }).catch((error) => {
    delete globalThis[key];
    throw error;
  });
  return globalThis[key];
}

// anywidget fails a model whose initialize takes over two seconds, so initialize
// only starts the request and render waits for the bundle.
export default {
  initialize({ model }) {
    load(model).catch(() => {});
  },
  async render(context) {
    return (await load(context.model)).render(context);
  },
};
`;
}

for (const [entryPoint, outfile, options] of entries) {
  await build({ ...shared, ...options, entryPoints: [entryPoint], outfile });
  if (outfile.endsWith(".bundle.js")) {
    const code = await readFile(outfile, "utf8");
    await writeFile(outfile.replace(/\.bundle\.js$/, ".loader.js"), loaderSource(outfile, code));
  }
  if (outfile.endsWith(".js")) {
    await scopeRootTokensToHost(outfile.replace(/\.js$/, ".css"));
  }
}
