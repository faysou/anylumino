import { readFile, rm, writeFile } from 'node:fs/promises';
import { convert, write } from 'fumadocs-python';

const inputPath = new URL('../build/docs/anylumino.json', import.meta.url);
const outputPath = new URL('../content/docs/api/', import.meta.url);
const api = JSON.parse(await readFile(inputPath, 'utf8'));

delete api.modules.common;
filterModule(api);

await rm(outputPath, { recursive: true, force: true });
await write(
  convert(api, {
    baseUrl: '/docs/api',
    groupBy: 'none',
  }),
  outputPath.pathname,
);
await writeFile(
  new URL('meta.json', outputPath),
  `${JSON.stringify(
    {
      title: 'API reference',
      pages: ['index', 'layout', 'controls', 'components', 'astryx'],
    },
    null,
    2,
  )}\n`,
);

function filterModule(module) {
  module.modules = Object.fromEntries(
    Object.entries(module.modules)
      .filter(([name]) => !name.startsWith('_'))
      .map(([name, child]) => [name, filterModule(child)]),
  );
  module.classes = Object.fromEntries(
    Object.entries(module.classes)
      .filter(([name]) => !name.startsWith('_'))
      .map(([name, cls]) => [name, filterClass(cls)]),
  );
  module.functions = filterFunctions(module.functions);
  module.attributes = module.attributes.filter((attribute) => !attribute.name.startsWith('_'));
  return module;
}

function filterClass(cls) {
  cls.functions = filterFunctions(cls.functions, true);
  cls.attributes = cls.attributes.filter((attribute) => !attribute.name.startsWith('_'));
  return cls;
}

function filterFunctions(functions, keepConstructor = false) {
  return Object.fromEntries(
    Object.entries(functions).filter(
      ([name]) => !name.startsWith('_') || (keepConstructor && name === '__init__'),
    ),
  );
}
