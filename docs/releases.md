# Publishing OpenWish

The distribution name is `openwish`, the Python module is `openwish`, and the
installed command is `ow`. Users install with `uv tool install openwish` and
upgrade with `uv tool upgrade openwish`, followed by `ow init` in each project
whose installed skills they want to update.

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

1. Install the package and run the test suite on Python 3.11, 3.12, and 3.13.
2. Check that the distribution name is `openwish` and that the package and CLI
   versions agree. For a release, require an exact matching `vMAJOR.MINOR.PATCH` tag.
3. Build a wheel and source distribution using `uv build --no-sources`.
4. Validate their metadata and README using `twine check --strict`.
5. Install each artifact separately using `uv tool install` into temporary tool
   directories, outside the checkout. Check the actual `ow` executable, all four
   harness selections, packaged assets, project validation, and no-op reinitialization.
6. Upload the tested distributions as the `python-dists` workflow artifact.

`.github/workflows/release.yml` publishes those same artifacts without rebuilding:

| Trigger | Destination | GitHub environment |
| --- | --- | --- |
| Publish a stable GitHub release | PyPI | `pypi` |
| Manually run the Release workflow | TestPyPI | `testpypi` |
| Publish a GitHub prerelease | No publication | — |

Only the publishing job receives `id-token: write`. Pull requests and ordinary
pushes run the checks without publishing. Pushing a tag by itself does not publish;
the production trigger is publishing the GitHub release.

## First-release rehearsal

1. Finish the TestPyPI setup above.
2. Open **GitHub Actions → Release → Run workflow** and select the branch to test.
   Manual runs always target TestPyPI.
3. Confirm the build and publication jobs succeed, then exercise the package:

   ```sh
   uvx --index-url https://test.pypi.org/simple/ --from openwish==0.3.1 ow --version
   ```

TestPyPI and PyPI have independent version histories. Testing `0.3.1` on TestPyPI
does not prevent publishing `0.3.1` to PyPI. An already uploaded filename cannot
be overwritten; use a new version for revised artifacts on the same registry.

## Each production release

1. Update `pyproject.toml` and `src/openwish/__init__.py` to the same stable version.
   Update the README's displayed version and prepare concise GitHub release notes.
   Bundled skill/adapter changes require a version bump for existing installations.
2. Merge the release commit after Check passes.
3. Create a tag such as `v0.3.1` pointing to that commit, then publish a GitHub
   release for that tag. Leave **Set as a pre-release** unchecked.
4. The Release workflow reruns Check for the tagged revision and publishes only
   after the tests, version checks, metadata validation, and install checks pass.
5. Confirm the version appears at <https://pypi.org/project/openwish/> and verify
   installation with `uv tool install openwish==0.3.1` in a clean tool environment.
6. After the first successful production release, remove the pending-publication
   wording from the README's installation section.

If a build or check fails, no publication occurs. Fix the issue before creating
the next release. If an upload fails, inspect PyPI to see which artifacts arrived;
the workflow deliberately does not silently skip existing distribution files.

## Local release checks

Run from the repository root with Python 3.11+ and uv available:

```sh
python3 scripts/check_release.py --tag v0.3.1
PYTHONPATH=src python3 -m unittest discover -s tests
uv build --no-sources
uvx twine check --strict dist/*
python3 scripts/smoke_dist.py dist --expected-version 0.3.1
```

Use a fresh output directory or remove obsolete distribution files before building
a new version: the smoke test requires exactly the wheel and source archive for
the selected release. These local commands perform no publication.
