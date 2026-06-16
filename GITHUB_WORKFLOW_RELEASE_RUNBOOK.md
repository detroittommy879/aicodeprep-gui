# GitHub Workflow Release Runbook

Use this when you want GitHub Actions to build the Rust worker binaries and Python package instead of doing manual builds.

The safe path is:

1. Run the workflow on the feature branch as a dry run.
2. Merge the feature branch to `main`.
3. Tag `main`.
4. Let the tag workflow create the GitHub Release artifacts.
5. Only publish to PyPI after inspecting those artifacts.

## What The Workflow Does

`.github/workflows/build-release.yml` builds the Rust worker for:

```text
windows-x86_64
linux-x86_64
linux-aarch64
darwin-x86_64
darwin-aarch64
```

Then it copies those workers into:

```text
aicodeprep_gui/rust/bin/<platform>/
```

Then it builds:

```text
dist/*.whl
dist/*.tar.gz
```

Then it verifies the wheel and sdist contain all five worker binaries.

## Safe Dry Run On The Feature Branch

This does not publish to PyPI and does not create a GitHub Release.

1. Commit and push your feature branch.

   ```powershell
   git status
   git add pyproject.toml
   git commit -m "Upgrade requests for security release"
   git push origin feature/aichatdocked
   ```

2. Go to GitHub.

   ```text
   Actions -> Build and Package -> Run workflow
   ```

3. Select the branch.

   ```text
   Branch: feature/aichatdocked
   publish_to_pypi: false
   ```

4. Click `Run workflow`.

5. Wait for these jobs to pass:

   ```text
   Build Rust worker (windows-x86_64)
   Build Rust worker (linux-x86_64)
   Build Rust worker (linux-aarch64)
   Build Rust worker (darwin-x86_64)
   Build Rust worker (darwin-aarch64)
   Build Python package with workers
   ```

6. Open the workflow run and download the `python-package` artifact.

7. Confirm it contains:

   ```text
   aicodeprep_gui-1.5.0-py3-none-any.whl
   aicodeprep_gui-1.5.0.tar.gz
   ```

If this dry run passes, the automation is doing the hard part correctly.

## Merge To Main

After the dry run passes:

```powershell
git checkout main
git pull origin main
git merge --no-ff feature/aichatdocked
git push origin main
```

If you prefer GitHub's web UI, open a PR from `feature/aichatdocked` into `main`, wait for checks, then merge it there.

## Create The Release Tag

Only tag after `main` contains the release changes.

```powershell
git checkout main
git pull origin main
git tag v1.5.0
git push origin v1.5.0
```

Pushing `v1.5.0` starts the workflow automatically.

For tag runs, the workflow also creates or updates a GitHub Release and attaches the built `dist/*` files.

## Inspect The GitHub Release

Go to:

```text
GitHub -> Releases -> v1.5.0
```

Download the wheel and inspect it locally if you want:

```powershell
python - <<'PY'
import zipfile
from pathlib import Path

wheel = next(Path(".").glob("aicodeprep_gui-1.5.0-*.whl"))
with zipfile.ZipFile(wheel) as zf:
    for name in sorted(zf.namelist()):
        if "aicodeprep_gui/rust/bin/" in name:
            print(name)
PY
```

Expected worker files:

```text
aicodeprep_gui/rust/bin/darwin-aarch64/aicp-rust-worker
aicodeprep_gui/rust/bin/darwin-x86_64/aicp-rust-worker
aicodeprep_gui/rust/bin/linux-aarch64/aicp-rust-worker
aicodeprep_gui/rust/bin/linux-x86_64/aicp-rust-worker
aicodeprep_gui/rust/bin/windows-x86_64/aicp-rust-worker.exe
```

## Publish To PyPI Manually

If you are not using Trusted Publishing yet, download the release artifacts and publish them yourself:

```powershell
python -m pip install --upgrade twine
twine check dist/*
twine upload dist/*
```

Or with `uv`:

```powershell
uv publish
```

Do not rebuild locally for PyPI if the whole point is to ship GitHub-built Rust workers. Publish the artifacts from the GitHub Release.

## Publish To PyPI With The Workflow

Only use this after PyPI Trusted Publishing is configured for this repository.

Run the workflow manually from the tag:

```text
Actions -> Build and Package -> Run workflow
Branch/tag: v1.5.0
publish_to_pypi: true
```

If Trusted Publishing is not configured, this job should fail without uploading anything.

## If Something Fails

If a worker build fails, do not publish. Check the failed platform job first.

If `Verify package includes worker binaries` fails, do not publish. That means the wheel did not contain every platform binary.

If the GitHub Release exists but PyPI upload fails, do not reuse the same PyPI version after a partial upload. PyPI does not allow overwriting files for the same version. Bump the version before retrying if anything reached PyPI.

