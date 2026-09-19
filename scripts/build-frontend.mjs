import { readFile, writeFile } from "node:fs/promises";

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

for (const [entryPoint, outfile] of entries) {
  await build({
    ...shared,
    entryPoints: [entryPoint],
    outfile,
  });
  await scopeRootTokensToHost(outfile.replace(/\.js$/, ".css"));
}
