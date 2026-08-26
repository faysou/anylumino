import { defineConfig, globalIgnores } from 'eslint/config';
import nextVitals from 'eslint-config-next/core-web-vitals';

const eslintConfig = defineConfig([
  ...nextVitals,
  globalIgnores([
    '.next/**',
    '.uv-cache/**',
    '.venv/**',
    'build/**',
    'dist/**',
    'node_modules/**',
    'src/anylumino/static/**',
    'next-env.d.ts',
  ]),
]);

export default eslintConfig;
