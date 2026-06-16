from ai '''───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
• Deployed.

  Live now:

  https://aicp-docs.pages.dev/

  Wrangler project:

  aicp-docs

  Verified:

  https://aicp-docs.pages.dev/ -> 200 OK

  I also updated the repo for this local workflow:

  - mkdocs.yml now uses https://aicp.wuu73.org as site_url.
  - Added aicodeprep-gui/scripts/deploy-docs-cloudflare.ps1.
  - Updated aicodeprep-gui/DOCS_DEPLOYMENT.md.
  - Added .wrangler/ to .gitignore.

  Future deploy from this machine is now:

  .\scripts\deploy-docs-cloudflare.ps1

  The only unfinished piece is binding the custom domain aicp.wuu73.org. Wrangler 4.100.0 can create/deploy Pages projects, but it does not expose a custom-domain command. The clean options
  are:

  Cloudflare dashboard:
  Workers & Pages -> aicp-docs -> Custom domains -> Set up a custom domain -> aicp.wuu73.org

  or use the script’s API path after setting:

  $env:CLOUDFLARE_ACCOUNT_ID = "264453d841d689f1b6dcc8a5f4be8fdc"
  $env:CLOUDFLARE_API_TOKEN = "your-scoped-api-token"
  .\scripts\deploy-docs-cloudflare.ps1 -BindDomain

  I did not scrape Wrangler’s local OAuth credential to call the API. That would work against the grain of the tooling and risks leaking/breaking auth state.
'''

# Docs Deployment

AICodePrep uses MkDocs for the documentation site.

The source files are:

```text
docs/*.md
mkdocs.yml
requirements-docs.txt
```

The generated static site goes into:

```text
site/
```

`site/` should stay ignored. Do not commit generated HTML/CSS unless there is a specific reason to host from a static folder manually.

## Recommended Setup: Cloudflare Pages

Use Cloudflare Pages for `https://aicp.wuu73.org`.

Current Pages project:

```text
aicp-docs
```

Current default Cloudflare URL:

```text
https://aicp-docs.pages.dev/
```

There are two good ways to deploy.

## Option A: Cloudflare Git Integration

This is the simplest setup.

In Cloudflare Pages:

1. Create a Pages project.
2. Connect the GitHub repository.
3. Use `main` as the production branch.
4. Set the build command:

   ```text
   pip install -r requirements-docs.txt && mkdocs build --strict
   ```

5. Set the build output directory:

   ```text
   site
   ```

6. Add the custom domain:

   ```text
   aicp.wuu73.org
   ```

With this setup, Cloudflare watches GitHub. Every push to `main` that changes docs can rebuild and deploy the site. Pull requests can get preview deployments.

## Option B: GitHub Actions + Wrangler

This repo also includes:

```text
.github/workflows/deploy-docs-cloudflare.yml
```

That workflow:

1. Builds the MkDocs site.
2. Uploads `site/` as a workflow artifact.
3. Deploys `site/` to Cloudflare Pages with Wrangler.

Set these GitHub repository secrets:

```text
CLOUDFLARE_ACCOUNT_ID
CLOUDFLARE_API_TOKEN
```

Optional repository variable:

```text
CLOUDFLARE_PAGES_PROJECT
```

If the variable is not set, the workflow uses:

```text
aicp-docs
```

## Which Option To Use

Use Cloudflare Git Integration if you want the least maintenance.

Use GitHub Actions + Wrangler if you want deployment defined in the repo and easy to extend later with extra checks.

Do not use both for the same branch long-term, or each push may create duplicate deployments.

## Local Preview

Run:

```powershell
uv run --with mkdocs-material mkdocs serve -a 127.0.0.1:8001
```

Then open:

```text
http://127.0.0.1:8001/
```

`mkdocs serve` watches the docs source files and rebuilds automatically while it is running.

On Linux, this kind of file watching is usually backed by the kernel's `inotify` system, not a slow manual loop over every file. You normally do not need to build your own polling script.

## Manual Build

Run:

```powershell
uv run --with mkdocs-material mkdocs build --strict
```

The generated files will be in `site/`.

## Manual Cloudflare Deploy

If you want to deploy from this machine, use the helper script:

```powershell
.\scripts\deploy-docs-cloudflare.ps1
```

That builds the MkDocs site and deploys `site/` to:

```text
aicp-docs
```

The raw commands are:

```powershell
uv run --with-requirements requirements-docs.txt mkdocs build --strict
pnpm dlx wrangler pages deploy site --project-name aicp-docs --branch main --commit-dirty=true
```

Use this for manual deploys from the local machine.

## Binding The Custom Domain

The Pages deployment is live after upload, but `aicp.wuu73.org` also has to be associated with the Pages project as a custom domain.

Wrangler 4.100.0 can create/list/deploy Pages projects, but it does not expose a `pages domain` command in the CLI help. Cloudflare's API supports adding a Pages custom domain:

```text
POST /accounts/{account_id}/pages/projects/{project_name}/domains
```

The helper script can call that API if these environment variables are set:

```powershell
$env:CLOUDFLARE_ACCOUNT_ID = "your-account-id"
$env:CLOUDFLARE_API_TOKEN = "your-scoped-api-token"
```

Then run:

```powershell
.\scripts\deploy-docs-cloudflare.ps1 -BindDomain
```

If you do not want to use an API token locally, add the custom domain once in the Cloudflare dashboard:

```text
Workers & Pages -> aicp-docs -> Custom domains -> Set up a custom domain -> aicp.wuu73.org
```

After the custom domain is attached, normal docs updates only need redeploys.
