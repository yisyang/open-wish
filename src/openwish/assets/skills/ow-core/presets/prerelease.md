# Preset: prerelease

Overrides: `stage`

For a product nobody depends on yet: before its first release its data can be
discarded and its features still change. The project policy says what release means
and names the qualities that wait for it, typically recovery from crashes and
retries, behavior under concurrent use, upgrades of stored data, abuse and scale.

- **Rigor follows what a failure would cost today.** A waiting quality comes from
  shared mechanisms or not yet at all: no change builds, checks or reviews it feature
  by feature, and a finding about it is an observation, not a blocker.
- **Release-only criteria say so.** An acceptance criterion that binds only from
  release starts `From release: …`. Until then it constrains only a choice that would
  be costly to reverse afterwards (Commit progressively in `ow-plan`).
- **Every other quality binds now:** credible failures (Strategic verification in
  `ow-plan`) narrow to wrong results in ordinary use and actions without authority.
- **At release,** remove this preset from `openwish/config.json`; every quality then
  binds.
