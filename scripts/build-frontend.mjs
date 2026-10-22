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

// Astryx menus, such as Selector, DropdownMenu, and ContextMenu, find the option
// under a released pointer with `document.elementFromPoint`, which returns the
// shadow host for a point inside a shadow root. In a host such as marimo every
// option click then counts as outside the menu and only closes it, so the menu
// hit-tests in its own shadow root instead. The build fails when the Astryx
// code changes, so that the patch is checked again.
const menuPressCall = "element = doc.elementFromPoint(event.clientX, event.clientY);";
const menuPressInShadowRoot = {
  name: "astryx-menu-press-in-shadow-root",
  setup(build) {
    build.onLoad({ filter: /@astryxdesign[\\/]core[\\/]dist[\\/]hooks[\\/]useMenuPress\.js$/ }, async ({ path }) => {
      const source = await readFile(path, "utf8");
      if (!source.includes(menuPressCall)) {
        throw new Error(`${path} no longer contains ${menuPressCall}`);
      }
      return {
        contents: source.replace(
          menuPressCall,
          "element = (menu?.getRootNode() instanceof ShadowRoot ? menu.getRootNode() : doc).elementFromPoint(event.clientX, event.clientY);",
        ),
        loader: "js",
      };
    });
  },
};

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
  await build({ ...shared, ...options, entryPoints: [entryPoint], outfile, plugins: [menuPressInShadowRoot] });
  if (outfile.endsWith(".bundle.js")) {
    const code = await readFile(outfile, "utf8");
    await writeFile(outfile.replace(/\.bundle\.js$/, ".loader.js"), loaderSource(outfile, code));
  }
  if (outfile.endsWith(".js")) {
    await scopeRootTokensToHost(outfile.replace(/\.js$/, ".css"));
  }
}
