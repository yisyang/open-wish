+++
id = "S-001"
needs = ["N-001", "N-003", "N-006"]
+++

# Needs and bounded knowledge design

Markdown records use TOML headers parsed by the Python standard library. JSON
holds bounded configuration, need-owned authority, and review. Stable IDs connect artifacts.

`storage.py` owns safe path resolution, loading, and bounded atomic replacement.
`model.py` derives a complete needs view and dependency impact without duplicating
stored state. `budgets.py` checks artifact lines, global context estimates, and
Git-aware source LOC. The estimate is UTF-8 bytes/3; LOC is nonblank physical lines.

Templates and consolidation guidance keep summaries replaceable. Git stores
history. Semantic compaction remains an agent operation because mechanical text
compression cannot establish that all current acceptance conditions survive.
