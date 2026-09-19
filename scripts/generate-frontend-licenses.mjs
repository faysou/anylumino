import { readdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";

import { build } from "esbuild";

import { entries, shared } from "./bundle-entries.mjs";

const OUTPUT = "THIRD_PARTY_LICENSES.md";
const NOTICE_NAMES = /^(licen[cs]e|copying|notice)/i;

// Some packages publish no license file. Their upstream notices are kept in
// `licenses/` and matched by package name prefix.
const CURATED_NOTICES = [
  ["@astryxdesign/", "licenses/astryx.txt"],
  ["@lumino/", "licenses/lumino.txt"],
  ["@stylexjs/", "licenses/stylex.txt"],
];

// Bundle inputs are esbuild paths such as
// `node_modules/@lumino/widgets/dist/index.es6.js`. Only the segment after the
// last `node_modules` identifies the package that owns the code.
function packageDirectory(input) {
  const marker = input.lastIndexOf("node_modules/");
  if (marker === -1) {
    return null;
  }
  const rest = input.slice(marker + "node_modules/".length).split("/");
  const segments = rest[0].startsWith("@") ? rest.slice(0, 2) : rest.slice(0, 1);
  return join(input.slice(0, marker), "node_modules", ...segments);
}

async function readManifest(directory) {
  const manifest = JSON.parse(await readFile(join(directory, "package.json"), "utf8"));
  const license = typeof manifest.license === "object" ? manifest.license?.type : manifest.license;
  return {
    name: manifest.name,
    version: manifest.version,
    license: license ?? "See notice",
  };
}

async function readNotices(name, directory) {
  const files = (await readdir(directory)).filter((file) => NOTICE_NAMES.test(file)).sort();
  const notices = [];
  for (const file of files) {
    notices.push({ source: file, text: (await readFile(join(directory, file), "utf8")).trim() });
  }
  if (notices.length > 0) {
    return notices;
  }

  const curated = CURATED_NOTICES.find(([prefix]) => name.startsWith(prefix));
  if (!curated) {
    throw new Error(`${name} publishes no license file. Add its notice to licenses/ and to CURATED_NOTICES.`);
  }
  return [{ source: curated[1], text: (await readFile(curated[1], "utf8")).trim() }];
}

async function bundledPackages() {
  const directories = new Set();
  for (const [entryPoint] of entries) {
    const result = await build({
      ...shared,
      entryPoints: [entryPoint],
      outdir: dirname(entryPoint),
      write: false,
      metafile: true,
    });
    for (const input of Object.keys(result.metafile.inputs)) {
      const directory = packageDirectory(input);
      if (directory) {
        directories.add(directory);
      }
    }
  }

  const packages = [];
  for (const directory of directories) {
    const manifest = await readManifest(directory);
    packages.push({ ...manifest, notices: await readNotices(manifest.name, directory) });
  }
  return packages.sort((left, right) => left.name.localeCompare(right.name));
}

function render(packages) {
  const lines = [
    "# Third-party frontend licenses",
    "",
    "<!-- markdownlint-disable MD013 MD024 -->",
    "",
    "The widget bundles under `src/anylumino/static` compile the packages below into",
    "the distributed wheel. Their license texts follow the table.",
    "",
    "Run `npm run licenses` to regenerate this file from the bundle inputs after a",
    "frontend dependency change.",
    "",
    "| Package | Version | License |",
    "| ------- | ------- | ------- |",
  ];
  for (const entry of packages) {
    lines.push(`| ${entry.name} | ${entry.version} | ${entry.license} |`);
  }
  for (const entry of packages) {
    lines.push("", `## ${entry.name} ${entry.version}`);
    for (const notice of entry.notices) {
      lines.push("", `Notice from \`${notice.source}\`:`, "", "```text", notice.text, "```");
    }
  }
  return `${lines.join("\n")}\n`;
}

const packages = await bundledPackages();
await writeFile(OUTPUT, render(packages));
console.log(`${OUTPUT}: ${packages.length} bundled packages`);
