const schemePattern = /^[a-z][a-z\d+.-]*:/i;

export function normalizeDocsHref(href) {
  if (
    href.startsWith('/') ||
    href.startsWith('#') ||
    href.startsWith('?') ||
    schemePattern.test(href)
  ) {
    return href;
  }

  const suffixIndex = href.search(/[?#]/);
  const path = suffixIndex === -1 ? href : href.slice(0, suffixIndex);
  const suffix = suffixIndex === -1 ? '' : href.slice(suffixIndex);
  const pagePath = path.endsWith('/') ? `${path}index.mdx` : path;
  const prefix = pagePath.startsWith('./') || pagePath.startsWith('../') ? '' : './';

  return `${prefix}${pagePath}${suffix}`;
}
