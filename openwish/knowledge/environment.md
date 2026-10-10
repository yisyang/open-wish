# Environment

- Runtime: Python 3.11+; verified locally with Python 3.12.3 on Linux.
- Runtime dependencies: none. Build backend: setuptools.
- Source execution: `PYTHONPATH=src python3 -m openwish ...`.
- Verification: `PYTHONPATH=src python3 -m unittest discover -s tests -v`.
- CLI installation: `pipx install .`, `uv tool install .`, or pip in a venv.
- Host adapters: OpenCode V2, Claude Code, Codex, and generic Agent Skills.
- Initial product scope: this single repository. No deployment secrets required.

The initial needs/specs were registered after bootstrap implementation. They are
in review and do not fabricate prior OW gate receipts or human-confirmation dates.
Future implementation uses the standard need-revision workflow. A need can be
reopened under its existing ID; there are no stored asks or change records.
