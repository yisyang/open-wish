# Working on OpenWish

Develop this repository directly using ordinary code changes and verification.
Do not initialize OpenWish here, install its workflow into this checkout, or
create needs, epics, gate receipts, or acceptance prompts to manage contributions
unless the user explicitly requests an OW workflow for that work.

- Product requirements live in `docs/product.md`; architecture lives in `docs/design.md`.
- `src/openwish/assets/skills/` contains shipped product assets, not instructions
  governing development of this repository. Edit canonical assets there.
- Exercise OW initialization and workflows in temporary test projects.
- Keep the implementation dependency-free at runtime and follow existing patterns.
- For substantive changes run `PYTHONPATH=src python3 -m unittest discover -s tests -v`.
- Keep package and module versions synchronized when changing bundled integrations.
- Respect the user's scope, including requests not to commit or push.
