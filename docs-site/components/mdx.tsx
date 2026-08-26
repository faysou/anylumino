import type { MDXComponents } from 'mdx/types';
import type { ComponentProps } from 'react';
import * as Python from 'fumadocs-python/components';
import defaultMdxComponents from 'fumadocs-ui/mdx';
import { normalizeDocsHref } from '@/lib/docs-href.mjs';
import { source } from '@/lib/source';

type DocsPage = (typeof source)['$inferPage'];

export function getMDXComponents(components?: MDXComponents) {
  return {
    ...defaultMdxComponents,
    ...Python,
    ...components,
  } satisfies MDXComponents;
}

export const useMDXComponents = getMDXComponents;

export function createDocsLink(page: DocsPage) {
  const Link = defaultMdxComponents.a;

  return async function DocsLink({ href, ...props }: ComponentProps<'a'>) {
    const normalizedHref = href ? normalizeDocsHref(href) : href;
    const resolvedHref = normalizedHref
      ? source.resolveHref(normalizedHref, page)
      : normalizedHref;

    return <Link href={resolvedHref} {...props} />;
  };
}

declare global {
  type MDXProvidedComponents = ReturnType<typeof getMDXComponents>;
}
