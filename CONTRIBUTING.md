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
- Favor cohesive source below 500 nonblank lines when practical; assess complexity
  rather than splitting mechanically. Product source hard limits are opt-in. Knowledge
  uses soft token targets; preserve readable formatting, constraints and exceptions.
- Test behaviors that protect intent, user data, local dependencies, safe disposal,
  or review freshness. Avoid tests that merely reproduce implementation text.
- Run the full suite after substantive changes; it should remain well under
  five minutes. Choose further checks based on actual unresolved risk.
- Start each module with a one-line docstring stating what it owns; `docs/design.md`
  points to these rather than repeating them.
- Keep canonical skills in `src/openwish/assets/skills/`. Test generated adapters
  without copying divergent workflow logic into them.
- Give each workflow rule one owner (the policy or one skill section) and refer to it
  by name elsewhere. Keep skills procedural and concise; every sentence costs agent
  context in every user's project. Use worked examples from domains that no eval
  scenario uses.
- Keep workflow overhead proportional to the work. Test routine changes without
  creating OW records to manage the contribution.
- For skill changes, run the executable scenarios with both arms
  (`python3 evals/run.py run ...`, see [evals](evals/README.md)) and compare against
  the previous skills on the same prompts.
- In the product, distinguish conversation authority from task readiness and
  human result acceptance from change-scoped fast-forward delegation.

## Compatibility

Existing projects must keep working across upgrades. The artifact schema version
lives in `openwish/config.json`. Any change to an artifact format (config, needs,
changes, tasks, reviews or the installation manifest) increments the schema and
ships a migration from every earlier schema since 4, applied by `ow init`:

- Preflight the whole project before writing, so a failed migration changes nothing.
- Preserve meaning, unknown files and project-owned policy; never drop a field's
  content silently.
- Project commands on an older schema stop and say to run `ow init`. A CLI that
  does not know a project's schema refuses it and asks for an upgrade.
- Test each migration on a fixture project of every earlier schema, including an
  idempotent rerun.

A change that breaks existing projects or documented CLI behavior, including
removing a migration path, needs a major version. Preserve unknown project files. Integration updates overwrite
older versions, preserve same-version edits, and require confirmation to downgrade.
Keep package and `__version__` values in sync; bump the version when bundled skills
or adapters change so installations can receive the update.

Publish from the source checkout only after tests and a wheel-install smoke test
pass. Check package data contains the project-policy starter, the schema-4 migration
digests and all eleven skills, including `ow-core` with its artifact reference.

## Releases

The canonical PyPI distribution is `openwish`; its executable is `ow`. The Check
workflow tests the supported Python matrix, checks version agreement, builds a
wheel and source distribution, validates metadata, and installs both with uv.
The Release workflow reuses those checks and publishes the exact tested artifacts.

Published stable GitHub releases go to PyPI; pushed version tags go to TestPyPI.
See [release setup and procedure](docs/releases.md) for the one-time Trusted
Publisher configuration and the steps for each release.
