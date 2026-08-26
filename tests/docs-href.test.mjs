import assert from 'node:assert/strict';
import test from 'node:test';
import { normalizeDocsHref } from '../docs-site/lib/docs-href.mjs';

test('normalizes bare documentation paths', () => {
  assert.equal(normalizeDocsHref('guide.mdx'), './guide.mdx');
  assert.equal(normalizeDocsHref('api/'), './api/index.mdx');
  assert.equal(normalizeDocsHref('api/#classes'), './api/index.mdx#classes');
});

test('preserves hrefs that Fumadocs or the browser already resolves', () => {
  const hrefs = [
    './sibling.mdx',
    '../parent.mdx',
    '/docs/api',
    '#section',
    '?tab=python',
    'https://astryx.atmeta.com/components',
  ];

  for (const href of hrefs) {
    assert.equal(normalizeDocsHref(href), href);
  }
});
