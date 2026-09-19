import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { RootProvider } from 'fumadocs-ui/provider/next';
import './global.css';

export const metadata: Metadata = {
  title: {
    default: 'AnyLumino Documentation',
    template: '%s | AnyLumino',
  },
  description: 'Documentation for composing notebook interfaces with AnyLumino.',
};

const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? '';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="flex min-h-screen flex-col">
        <RootProvider
          search={{ options: { type: 'static', api: `${basePath}/static.json` } }}
        >
          {children}
        </RootProvider>
      </body>
    </html>
  );
}
