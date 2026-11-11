import { defineConfig, globalIgnores } from 'eslint/config';
import nextVitals from 'eslint-config-next/core-web-vitals';
import globals from 'globals';

// The widget sources run in the notebook page, outside Next.js, so only the undefined-name check
// applies to them.
const widgetSources = 'src/anylumino/static/**';

const eslintConfig = defineConfig([
  ...nextVitals.map((config) => (config.name ? { ...config, ignores: [widgetSources] } : config)),
  {
    files: [`${widgetSources}/*.{js,mjs}`],
    languageOptions: { globals: globals.browser },
    rules: { 'no-undef': 'error' },
  },
  globalIgnores([
    '.next/**',
    '.uv-cache/**',
    '.venv/**',
    'build/**',
    'dist/**',
    'node_modules/**',
    'src/anylumino/static/**/*.bundle.*',
    'src/anylumino/static/**/*.loader.js',
    'next-env.d.ts',
  ]),
]);

export default eslintConfig;
