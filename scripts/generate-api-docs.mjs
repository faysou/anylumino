import { readFile, rm, writeFile } from 'node:fs/promises';
import { convert, write } from 'fumadocs-python';

const inputPath = new URL('../build/docs/anylumino.json', import.meta.url);
const outputPath = new URL('../content/docs/api/', import.meta.url);
const api = JSON.parse(await readFile(inputPath, 'utf8'));
// Astryx submodules in reading order: the shared base, then composition, then
// the component families.
const ASTRYX_MODULE_ORDER = ['base', 'layout', 'surfaces', 'inputs', 'data'];

delete api.modules.common;
filterModule(api);
orderAstryxModules(api.modules.astryx);

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

function orderAstryxModules(astryx) {
  const order = (name) => {
    const index = ASTRYX_MODULE_ORDER.indexOf(name);
    return index === -1 ? ASTRYX_MODULE_ORDER.length : index;
  };
  astryx.modules = Object.fromEntries(
    Object.entries(astryx.modules).sort(([left], [right]) => order(left) - order(right)),
  );
}

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
