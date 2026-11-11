import { readFile, writeFile } from "node:fs/promises";

import { build } from "esbuild";

import { loaderSource } from "./bundle-loader.mjs";
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
