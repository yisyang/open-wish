# Publishing OpenWish

The distribution name and Python module are `openwish`. The installed commands
are the exact aliases `ow` (canonical in documentation) and `openwish`. Users
install with `uv tool install openwish` and upgrade with
`uv tool upgrade openwish`, followed by `ow init` in each project whose installed
skills they want to update. Before v1.0.0, only the current artifact schema is
supported; releases do not include migrations or legacy compatibility.

## One-time human setup

1. Create a PyPI account and complete its account requirements.
2. In the account's **Publishing** settings, add a pending GitHub Trusted Publisher:

   | Field | Production value |
   | --- | --- |
   | PyPI project name | `openwish` |
   | Owner | `yisyang` |
   | Repository | `open-wish` |
   | Workflow filename | `release.yml` |
   | Environment | `pypi` |

3. In GitHub repository **Settings → Environments**, create `pypi`.
4. For a rehearsal, create a separate account/pending publisher on **TestPyPI**
   with the same project, owner, repository, and workflow, but environment
   `testpypi`. Create the corresponding GitHub environment `testpypi`.
5. Merge the workflow and packaging files into the repository's default branch.

Trusted Publishing uses GitHub's identity for short-lived upload credentials;
there is no PyPI token to add to GitHub secrets. A pending publisher creates the
project on its first successful upload; configuring it alone does not reserve
the package name. Both registries use `.github/workflows/release.yml` as the
publisher, even though it calls the reusable Check workflow to build artifacts.

References: [PyPI pending publishers](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
and [publishing with GitHub Actions](https://docs.pypi.org/trusted-publishers/using-a-publisher/).

## What runs automatically

`.github/workflows/check.yml` runs on pushes, pull requests, and calls from the
release workflow:

1. Install the package and run the test suite on Python 3.11, 3.12, 3.13, and 3.14.
2. Check that the distribution name is `openwish` and that the package and CLI
   versions agree. For a release, require an exact matching `vMAJOR.MINOR.PATCH` tag.
3. Build a wheel and source distribution using `uv build --no-sources`.
4. Validate their metadata and README using `twine check --strict`.
5. Install each artifact separately using `uv tool install` into temporary tool
   directories, outside the checkout. Check the actual `ow` and `openwish`
   executables, all four harness selections, packaged assets, project validation,
    no-op reinitialization, and the change/review/closure/disposal lifecycle.
6. Upload the tested distributions as the `python-dists` workflow artifact.

`.github/workflows/release.yml` publishes those same artifacts without rebuilding:

| Trigger | Destination | GitHub environment |
| --- | --- | --- |
| Publish a stable GitHub release | PyPI | `pypi` |
| Push a `vMAJOR.MINOR.PATCH` tag | TestPyPI | `testpypi` |
| Publish a GitHub prerelease | No publication | — |

Only the publishing job receives `id-token: write`. Pull requests and ordinary
branch pushes run the checks without publishing. Version tags publish to TestPyPI;
the production trigger remains publishing the stable GitHub release.

## TestPyPI rehearsal

1. Finish the TestPyPI setup above.
2. Create and push a version tag matching the package version, for example:

   ```sh
   git tag v0.5.0
   git push origin v0.5.0
   ```

   Version-tag pushes always target TestPyPI.
3. Confirm the build and publication jobs succeed, then exercise the package:

   ```sh
    uvx --index-url https://test.pypi.org/simple/ --from openwish==0.5.0 ow --version
   ```

TestPyPI and PyPI have independent version histories. Testing `0.5.0` on TestPyPI
does not prevent publishing `0.5.0` to PyPI. An already uploaded filename cannot
be overwritten; use a new version for revised artifacts on the same registry.

## Each production release

1. Update `pyproject.toml` and `src/openwish/__init__.py` to the same stable version.
   Update the README's displayed version and add the release's changes to the root
   [CHANGELOG.md](../CHANGELOG.md), newest first. Use version-only headings such as
   `## v0.5.0`, and use that entry for GitHub release notes.
   Bundled skill/adapter changes require a version bump for existing installations.
2. Merge the release commit after Check passes.
3. Create and push a tag such as `v0.5.0` pointing to that commit. Confirm the
   automatic TestPyPI publication succeeds and exercise the uploaded package.
4. Publish a GitHub release for that tag. Leave **Set as a pre-release** unchecked.
5. The Release workflow reruns Check for the tagged revision and publishes only
   after the tests, version checks, metadata validation, and install checks pass.
6. Confirm the version appears at <https://pypi.org/project/openwish/> and verify
   installation with `uv tool install openwish==0.5.0` in a clean tool environment.

If a build or check fails, no publication occurs. Fix the issue before creating
the next release. If an upload fails, inspect PyPI to see which artifacts arrived;
the workflow deliberately does not silently skip existing distribution files.

## Local release checks

Run from the repository root with Python 3.11+ and uv available:

```sh
python3 scripts/check_release.py --tag v0.5.0
PYTHONPATH=src python3 -m unittest discover -s tests -v
uv build --no-sources
uvx twine check --strict dist/*
python3 scripts/smoke_dist.py dist --expected-version 0.5.0
```

Use a fresh output directory or remove obsolete distribution files before building
a new version: the smoke test requires exactly the wheel and source archive for
the selected release. These local commands perform no publication.
