# Building This Docs Site

This documentation site is built with VitePress and outputs a plain static folder.

That means you can generate it locally and copy the built files to almost any ordinary web server, including your Ubuntu box on Oracle Cloud.

## Commands

From the repo root:

```bash
pnpm install
pnpm docs:dev
```

That starts the local docs site.

To build the static site:

```bash
pnpm docs:build
```

The built files end up here:

```text
docs/.vitepress/dist/
```

To preview the already-built site locally:

```bash
pnpm docs:preview
```

Do not judge the generated output by double-clicking files inside `docs/.vitepress/dist/` from the file system. VitePress should be previewed through `pnpm docs:preview`, another local web server, or your real deployed server.

## Copying the site to your server

Any static web server can host the output folder.

Examples:

```bash
scp -r docs/.vitepress/dist/* user@your-server:/var/www/your-domain/
```

or, if you want a cleaner sync:

```bash
rsync -av --delete docs/.vitepress/dist/ user@your-server:/var/www/your-domain/
```

## Suggested web server setup

For a normal domain on Ubuntu, the usual pattern is:

- build the docs locally or in CI
- copy `docs/.vitepress/dist/` to the directory served by Nginx or Apache
- point your domain at that directory

Because this site is a static site, it works well when served from a normal domain such as `https://docs.example.com/` or `https://example.com/`.

If you later want to serve it from a subfolder instead of a server root, update the VitePress `base` setting in `docs/.vitepress/config.mts` before building.

This repo now reads the base from the `DOCS_BASE` environment variable when present.

Examples:

```powershell
$env:DOCS_BASE = "/333/dist/"
npm run docs:build
```

```bash
DOCS_BASE=/333/dist/ npm run docs:build
```

If `DOCS_BASE` is not set, the docs build defaults to `/`, which is correct when the site is hosted at the domain root.

## Keeping docs current

The repository instructions now require feature changes to update the corresponding files in `docs/`.

In practice that means:

- new user-visible features should get documented when they land
- removed features should be removed from the docs the same day
- placeholder or partial features should be described honestly

This keeps the site aligned with the real app instead of turning into marketing copy.
