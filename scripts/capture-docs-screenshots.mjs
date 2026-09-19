// Capture one screenshot per documentation example.
//
// Run `scripts/docs_examples.py notebook` first, start JupyterLab, then run this
// script with ego-browser:
//
//   uv run --no-sync jupyter lab --no-browser --port 8912 --ServerApp.token=docsshots
//   ego-browser nodejs < scripts/capture-docs-screenshots.mjs
//
// Each code cell in `notebooks/docs_examples.py` starts with a
// `# docs-example(<slug>)` marker; the rendered output of that cell is written
// to `content/docs/assets/examples/<slug>.png`. Finish with
// `scripts/docs_examples.py images` to reference the new screenshots.

const { mkdir, writeFile } = await import("node:fs/promises");
const { homedir } = await import("node:os");
const { resolve } = await import("node:path");

const PORT = process.env.DOCS_SHOT_PORT ?? "8912";
const TOKEN = process.env.DOCS_SHOT_TOKEN ?? "docsshots";
const NOTEBOOK = "notebooks/docs_examples.py";
const VIEWPORT = { width: 1180, height: 900, deviceScaleFactor: 2, mobile: false };

const task = await taskSpace("anylumino documentation screenshots");
const page = task.page("p1");
console.log(JSON.stringify({ taskSpace: task.spaceId }));

// A notebook-sized viewport keeps the examples from stretching across a desktop
// window; the device pixel ratio already gives the screenshots retina detail.
await page.cdp("Emulation.setDeviceMetricsOverride", VIEWPORT);

await page.goto(`http://127.0.0.1:${PORT}/lab/tree/${NOTEBOOK}?token=${TOKEN}`);
await page.waitForFunction(
  () => !!document.querySelector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-CodeCell"),
  undefined,
  { timeout: 60_000 },
);
await page.waitForTimeout(3000);

await page.click("loc=css:.lm-MenuBar-itemLabel >> nth=3", { label: "open Run menu" });
await page.waitForFunction(
  () => !!document.querySelector('.lm-Menu-item[data-command="runmenu:restart-and-run-all"]'),
  undefined,
  { timeout: 10_000 },
);
await page.click('loc=css:.lm-Menu-item[data-command="runmenu:restart-and-run-all"]', {
  label: "restart kernel and run all",
});
try {
  await page.waitForSelector("loc=css:.jp-Dialog button.jp-mod-accept", {
    state: "visible",
    timeout: 8000,
  });
  await page.click("loc=css:.jp-Dialog button.jp-mod-accept", { label: "confirm kernel restart" });
} catch {
  console.log("no restart dialog");
}

// Execution is done once no cell is queued and the kernel has been idle a while.
await page.waitForFunction(
  () => {
    const panel = document.querySelector(".jp-NotebookPanel:not(.lm-mod-hidden)");
    if (!panel) return false;
    const prompts = [...panel.querySelectorAll(".jp-CodeCell .jp-InputPrompt")].map((node) =>
      node.textContent.trim(),
    );
    const status = panel
      .querySelector(".jp-Notebook-ExecutionIndicator")
      ?.getAttribute("data-status");
    const ran = prompts.some((prompt) => /^\[\d+\]:$/.test(prompt));
    if (prompts.some((prompt) => prompt.includes("*")) || !ran || status === "busy") {
      window.__idleSince = 0;
      return false;
    }
    window.__idleSince = window.__idleSince || Date.now();
    return Date.now() - window.__idleSince > 5000;
  },
  undefined,
  { timeout: 600_000, polling: 1000 },
);

const errors = await page.evaluate(() =>
  [...document.querySelectorAll(".jp-OutputArea-output.jp-mod-error")].map((node) =>
    node.textContent.trim().slice(0, 200),
  ),
);
if (errors.length > 0) {
  console.log(JSON.stringify({ errors }, null, 1));
  throw new Error(`${errors.length} cells failed`);
}

const slugs = await page.evaluate(() => {
  const panel = document.querySelector(".jp-NotebookPanel:not(.lm-mod-hidden)");
  return [...panel.querySelectorAll(".jp-CodeCell")]
    .map((cell) => cell.querySelector(".jp-InputArea-editor")?.textContent ?? "")
    .map((source) => source.match(/# docs-example\(([\w-]+)\)/)?.[1])
    .filter(Boolean);
});
console.log(JSON.stringify({ examples: slugs.length }));

// ego-browser runs this script from its own working directory, so the checkout
// comes from the JupyterLab server that serves the notebook.
const serverRoot = await page.evaluate(
  () => JSON.parse(document.getElementById("jupyter-config-data").textContent).serverRoot,
);
const outputDir = resolve(serverRoot.replace(/^~/, homedir()), "content/docs/assets/examples");
await mkdir(outputDir, { recursive: true });
const captured = [];
const skipped = [];

async function outputBox(slug) {
  return page.evaluate((target) => {
    const panel = document.querySelector(".jp-NotebookPanel:not(.lm-mod-hidden)");
    const cell = [...panel.querySelectorAll(".jp-CodeCell")].find((node) =>
      (node.querySelector(".jp-InputArea-editor")?.textContent ?? "").includes(
        `# docs-example(${target})`,
      ),
    );
    if (!cell) return null;
    const output = cell.querySelector(".jp-OutputArea-output");
    if (!output) return null;
    output.scrollIntoView({ block: "start" });
    const rect = output.getBoundingClientRect();
    if (rect.width < 8 || rect.height < 8) return null;
    return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
  }, slug);
}

for (const slug of slugs) {
  // JupyterLab renders cells as they scroll into view, and widgets such as
  // Plotly figures finish their first paint after that.
  await outputBox(slug);
  await page.waitForTimeout(2000);
  let box = await outputBox(slug);
  if (!box) {
    skipped.push(slug);
    continue;
  }

  // The capture stays inside the viewport, so a tall example grows it instead
  // of spilling into the surrounding JupyterLab chrome.
  const needed = Math.ceil(box.height) + 160;
  if (needed > VIEWPORT.height) {
    await page.cdp("Emulation.setDeviceMetricsOverride", { ...VIEWPORT, height: needed });
    await page.waitForTimeout(1500);
    box = await outputBox(slug);
    await page.waitForTimeout(800);
    box = await outputBox(slug);
  }

  if (!box) {
    skipped.push(slug);
    await page.cdp("Emulation.setDeviceMetricsOverride", VIEWPORT);
    continue;
  }

  const shot = await page.cdp("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: false,
    clip: { ...box, scale: 1 },
  });
  await writeFile(`${outputDir}/${slug}.png`, Buffer.from(shot.data, "base64"));
  captured.push(slug);

  if (needed > VIEWPORT.height) {
    await page.cdp("Emulation.setDeviceMetricsOverride", VIEWPORT);
    await page.waitForTimeout(500);
  }
}

await page.cdp("Emulation.clearDeviceMetricsOverride", {});

console.log(JSON.stringify({ captured: captured.length, skipped }, null, 1));
