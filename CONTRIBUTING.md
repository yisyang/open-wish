# Contributing to OpenWish

Develop this repository directly with ordinary code changes and verification.
Keep the smallest coherent scope and preserve [product requirements](docs/product.md).
Shipped OW skills are product assets, not the development process for this repo.
Test adoption and workflows in disposable projects; do not initialize OW in this
checkout unless explicitly asked to use it for a contribution.

## Local development

Python 3.11+ is sufficient to run the code and tests without installation:

```sh
PYTHONPATH=src python3 -m openwish --help
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

For an installed executable, use a virtual environment and `python -m pip install
-e .`, or `uv tool install .`. Setuptools is a build-time dependency only.

## Engineering rules

- Keep pure model/validation functions separate from filesystem operations.
- Prefer standard-library functionality and established packages where needed.
- Keep source below 500 nonblank lines when practical; 1000 is the hard maximum
  without a justified low-complexity exception. All Markdown/OW artifacts stay
  below 500 lines. Data-file exceptions never bypass OW knowledge limits.
- Test behaviors that protect intent, user data, ordering, approval freshness,
  or review correctness. Avoid tests that merely reproduce implementation text.
- Run the full suite after substantive changes; it should remain well under
  five minutes. Choose further checks based on actual unresolved risk.
- Keep canonical skills in `src/openwish/assets/skills/`. Test generated adapters
  without copying divergent workflow logic into them.
- Keep workflow overhead proportional to the work. Test routine changes without
  creating OW records to manage the contribution. See `evals/` for skill scenarios.
- In the product, distinguish execution authority from regression coverage and
  human decisions from fast-forward delegation or an agent's own assessment.

## Compatibility

Artifact schema version is stored in `openwish/config.json`. Reject unsupported
versions clearly. Preserve unknown project files. Integration updates overwrite
older versions, preserve same-version edits, and require confirmation to downgrade.
Keep package and `__version__` values in sync; bump the version when bundled skills
or adapters change so existing installations can receive the update. Preserve
known legacy template hashes when adding compatibility for unversioned releases.
Make schema migrations explicit before introducing incompatible formats.

Publish from the source checkout only after tests and a wheel-install smoke test
pass. Check package data contains policy, artifact reference, legacy template
hashes, and all eight skills.

## Releases

The canonical PyPI distribution is `openwish`; its executable is `ow`. The Check
workflow tests the supported Python matrix, checks version agreement, builds a
wheel and source distribution, validates metadata, and installs both with uv.
The Release workflow reuses those checks and publishes the exact tested artifacts.

Published stable GitHub releases go to PyPI; a manual Release workflow run goes
to TestPyPI. See [release setup and procedure](docs/releases.md) for the one-time
Trusted Publisher configuration and the steps for each release.
