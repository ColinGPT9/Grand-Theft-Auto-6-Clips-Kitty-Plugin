# REA local research result

2026-10-25. The requested [janblade/REA fork](https://github.com/janblade/REA) was inspected at commit `c462a4ebd3a10e59253bcf38353a0914b176738b`. Its README, setup docs/source, package manifest, MIT license and third-party notices were reviewed before installation. The published npm runtime identifies upstream morluto/rea; published 6.4.0 and the fork's later main commit are not claimed byte-identical.

Installation succeeded under `dirty-room/rea-cli`, pinned to `rea-agents@6.4.0`, using `--ignore-scripts --omit=optional --no-audit --no-fund --save-exact`. 143 packages were installed. Lockfile and npm cache stay in dirty-room. Frida and lifecycle scripts were omitted. Existing Node v22.11.0 is below REA's supported runtime range, so official portable Node v22.19.0 was downloaded from [nodejs.org](https://nodejs.org/dist/v22.19.0/) and verified against that release's SHA256 listing. Archive SHA256: `ea3fad0e67a991d8477d8c01344b56e69c676ccb733f065b22436994b1253f86`. The host's Node/npm installations, PowerShell execution policy and persistent PATH were not changed.

REA package integrity from the registry: `sha512-Vj1zWfSlna5bphGoaoI/TcVBuYvze9u+OyPC3Shz8YkBqaCTqB4COnnRoX7XDwMpwI24ZlFEel2yEj0k8LTWEQ==`. The [package's MIT license](https://github.com/morluto/rea/blob/main/LICENSE) covers REA-authored code; third-party notices remain applicable. Nothing from the tool or target is a product dependency/code donor.

The first npm attempt used portable npm while its archive was still extracting and failed because npm/package.json was not yet present. The successful retry used the existing system npm CLI script with portable Node; no security setting was changed. The portable extraction subsequently completed and checksum verification passed.

Executed by `run-isolated-rea.mjs`, with child-process USERPROFILE/TEMP/TMP set to a task-owned profile and no modifications to HOME/CODEX_HOME:

1. `rea --version`: 6.4.0.
2. `rea setup --client codex --skill=false --dry-run --json`: exit 0; status `planned`; one proposed creation at `dirty-room/isolated-profile/.codex/config.toml`; appliedActions empty. That configuration file does not exist afterward. The plan was reviewed; registration was unnecessary for CLI research and was never applied. Doctor's `healthy:false` is expected because selected agent registration and optional native engines were absent. CLI analysis is separate from MCP integration readiness. Read-only setup discovery also reported unrelated host app configuration paths through existing APPDATA; no changes were applied to those paths.
3. `rea analyze-javascript-application <dirty-room/open-source-stream-clipper> --json`: exit 0; 4,542,180 bytes of JSON evidence, 5,740 bytes of progress logging.

Authorized analysis target: [nirvagold/stream-clipper](https://github.com/nirvagold/stream-clipper), MIT license checked before clone, detached at `31868b99001d08a91d9f24eacaf3234bcb956b2b`. No target install/build or executable was run. REA reports directory digest `73df9c4dc7c8fdb3f32191711c3de33eba415d6ab9ce3129ca03f318ff3a5a64` for its inventoried source view.

REA's statistics: 23 relevant files, 93,403 text bytes read, 16 parsed JavaScript files, 3,850 AST nodes visited, 162 findings, zero invalid-UTF8 files, one parse failure. `statistics.modules` reports zero while the evidence graph includes source-module nodes; do not equate that field with source coverage. Graph coverage is explicitly `partial`, not truncated. Evidence identifies source module/import relationships, including unresolved Svelte imports and external Tauri call targets. These results support source inventory/relationship observations only. No detector implementation, runtime event accuracy or usable GUI behavior was proven. Rust/Svelte/runtime behavior is outside the demonstrated JavaScript coverage.

Evidence retained only in dirty-room:

- `rea-run-summary.json`
- `setup-plan.stdout.json` and `.stderr.log`
- `stream-clipper-static-analysis.stdout.json` and `.stderr.log`
- `run-isolated-rea.mjs`
- local pinned target checkout, package-lock.json, runtime ZIP and checksums

No native disassembler, browser capture, proprietary package analysis, competitor authentication or global Codex integration was used. No host/plugin repository was modified. Keep all these materials away from the independent implementation context; pass only the clean functional specification.
