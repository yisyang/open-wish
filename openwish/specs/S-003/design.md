+++
id = "S-003"
needs = ["N-001", "N-002", "N-004", "N-005", "N-006"]
+++

# CLI and harness integration design

`cli.py` uses argparse and exposes concise text plus JSON for automation.
Commands operate on need IDs, including `reopen`, `ready`, `gate`, and `approve`.
`views.py` derives final summaries and task lineage from spec design references.
`scaffold.py` creates small editable artifacts and supports repeatable initialization.
`integrations.py` installs canonical skill bodies into all selected harnesses.
`terminal.py` provides arrow/Space multi-selection, a numbered fallback, and
explicit downgrade confirmation; scripts select harnesses through repeatable flags.
OpenCode command files are thin adapters; Claude Code uses skill commands; Codex
and generic hosts use `.agents/skills` discovery. Explicit-only fast-forward
metadata supplements its portable policy instructions.

`versions.py` compares SemVer and reads generated `metadata.openwish-version`
stamps or adapter comments. A bounded installation manifest tracks per-file
versions and harness choices. Known unversioned v0.2 templates are detected using
bundled hashes. The entire selection is preflighted before writes: older versions
are overwritten, equal versions preserved byte-for-byte, and newer versions
downgraded only after confirmation. Shared Codex/generic paths are deduplicated.
Reinitialization preserves existing needs, designs, configuration, and knowledge.

The runtime has no third-party dependencies or provider SDK. Model reasoning and
implementation happen inside the user's existing harness. The package includes
the shared policy, artifact reference, legacy hashes, and eight canonical skill files.

Behavior tests exercise workflow transitions and public CLI paths. Installed-wheel
smoke testing verifies packaged assets and generated commands. Semantic dry runs
exercise intent preservation, final fast-forward acceptance, and manual blockers.
Pseudo-terminal tests exercise multi-selection, cancellation and terminal cleanup,
and both downgrade choices through the real CLI. Version tests cover upgrades,
equal-version no-op behavior, legacy recognition, and shared output paths.

PyPI metadata identifies the canonical `openwish` distribution and links its
GitHub repository, documentation, issues, and releases. The Check workflow tests
the Python matrix, verifies version agreement, builds both distributions, and
installs them separately with uv outside the checkout. The Release workflow reuses
Check and publishes its artifacts with Trusted Publishing: stable GitHub releases
go to PyPI; manual rehearsals go to TestPyPI. Registry publishers and GitHub
environments require human account setup, documented in `docs/releases.md`.
