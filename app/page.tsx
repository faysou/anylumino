const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? '';
const docsHref = `${basePath}/docs/`;

// A static export cannot redirect on the server, so the exported index page
// forwards to the documentation root instead.
export default function HomePage() {
  return (
    <>
      <meta httpEquiv="refresh" content={`0; url=${docsHref}`} />
      <main className="m-auto p-8">
        <a href={docsHref}>AnyLumino documentation</a>
      </main>
    </>
  );
}
