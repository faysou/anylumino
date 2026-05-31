# anylumino documentation site

This folder contains the Quarto website and quartodoc API reference for
`anylumino`.

Build from the repository root:

```sh
make docs
```

Preview locally with Quarto's watcher:

```sh
make docs-preview
```

This opens `http://127.0.0.1:4200/` automatically.

Serve the rendered static site without the Quarto watcher:

```sh
make docs-serve
```

Set another port with `DOCS_PORT=4300 make docs-preview` or
`DOCS_PORT=4300 make docs-serve`.

Set another opener with `OPEN="open -a Safari" make docs-preview`.
