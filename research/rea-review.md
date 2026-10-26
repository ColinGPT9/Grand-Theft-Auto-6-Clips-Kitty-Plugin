# REA inspection and authorized use

Reviewed on 2026-10-24. This investigation used an owned, open-source Clips Kitty application; no competitor package, private endpoint, credential, DRM, or authenticated account was inspected.

## Provenance and host requirements

- Requested repository: <https://github.com/janblade/REA>, read from local clone `/tmp/gta-research-rea` at `c462a4ebd3a10e59253bcf38353a0914b176738b`. Its package identifies itself as `rea-agents` 6.4.0 and points to <https://github.com/morluto/rea>.
- Inspected that clone's `AGENTS.md`, `README.md`, `docs/installation.md`, `package.json`, `scripts/rea.mjs`, setup implementation references, and MIT `LICENSE` before installing anything. The license attributes REA-authored code to morluto, copyright 2026. Third-party components retain their own licenses.
- The npm registry returned current version **6.7.0**. Downloaded and inspected that published package's README, manifest, and third-party notices before using it. Repository snapshot 6.4.0 and npm release 6.7.0 are separate artifacts; matching source or behavior is not assumed. The published README identifies `morluto/rea`, `rea.tools`, and the `rea-agents` npm package as official sources.
- Package Node requirement: `^22.19.0 || ^24.11.0 || >=26.0.0`, plus npm. Available host: Linux x86_64, Node **v24.19.0**, npm **11.9.0**. This satisfies the published runtime requirement. The older source checkout pins Node 24.18.0 and npm 11.16.0 for developing REA itself; REA was not built from source here.
- Published Linux documentation requires a procps-compatible `ps` for static JavaScript process ownership checks. The host's `ps -eo pid,ppid,pgid,lstart,args` accepted those fields. Static JavaScript analysis needs no native engine. Native workflows require a separately supplied supported Hopper/Ghidra/IDA installation; website observation needs a supported Chrome-family browser.

The npm archive `rea-agents-6.7.0.tgz` had SHA-256 `20958a66dba1a011e50a486beb9463a343128ed368c984f94065362c13f51f90`. npm reported integrity `sha512-yhIx2ioJYYT1C/tONfYeitC6LhnKmCh+ZwRUOgYuhSc733lGhkkt73zhug9WmLgxoMdKuqIYGCoBfD4fXkOhFw==`.

## Reviewed setup plan

Installed the pinned package locally, with lifecycle scripts and optional dependencies disabled:

```bash
npm install --prefix /tmp/gta-rea-run --ignore-scripts --omit=optional --omit=dev --no-audit --no-fund --cache /tmp/gta-rea-npm-cache rea-agents@6.7.0
npx --prefix /tmp/gta-rea-run --offline --no-install rea-agents setup --client codex --skill=false --dry-run --json
```

The install added 147 packages under `/tmp/gta-rea-run`. No global installation or software upgrade was performed. `--ignore-scripts` prevented dependency lifecycle execution; `--omit=optional` excluded optional Frida installation.

The actual setup returned `status: planned` and **zero applied actions**. It proposed one action: create `/run/codex-environment/codex-home/config.toml` with a Codex MCP registration invoking `npx -y rea-agents@6.7.0 mcp`, preserving unrelated configuration. No provider environment values or skill files were proposed because this review explicitly selected `--skill=false`. The dry-run plan is retained locally at `/tmp/gta-rea-setup-plan.json`, SHA-256 `a12304a8a8977a56302703fb01a30d7c36aaa599745d3b1ca5b68c6786fae819`.

That live Codex configuration action was **not applied**: this task permits isolated temporary setup and excludes global or secret configuration changes. The file remained absent after the dry run. Setup reports the Codex registration and native providers missing; no restart or live REA MCP connection is claimed. CLI use works independently of MCP registration. The repository's setup instructions explicitly require review and approval before configuration writes, so future persistent setup should use a newly reviewed plan on the actual development machine.

## Actual REA use and findings

Ran the supported static analyzer against the existing application's marketplace and plugin UI helpers:

```bash
npx --prefix /tmp/gta-rea-run --offline --no-install rea-agents analyze-javascript-application /workspace/clips-studio/ui --source-path src/renderer/src/lib/marketplace.ts --source-path src/renderer/src/lib/plugins.ts --artifact-format directory --analysis-timeout-ms 20000 --max-heap-mb 512 --json
```

The command completed successfully and returned Evidence:

- Evidence ID: `ev_183795af3bcd59c1bc45bcab6651bab4664609995c4cf78ea34531cf8820e9da`.
- Provider: `rea-javascript-application`, analyzer version `1`; confidence classified by REA as `derived`.
- UI artifact SHA-256: `7e784740ab929ca07a641f3f81ae6c08068793939c6142fc6e2aab89744427ba`.
- Selected files: two; parsed files: two; parse failures: zero; text bytes read: 57,991; visited AST nodes: 8,033.
- Selected marketplace source SHA-256: `f2bc0bc37a859ce685de13fdb0a49a6ac4e7d0cd140f60f7e3a3e5d2e7fe17e2`.
- Selected plugin UI helper source SHA-256: `d824729d72bae918100850a57108f5d110f6a92c5f306a3bbea42077db3e1465`.

Observed static structure: the marketplace module exposes catalog, compatibility, source-link, and settings helpers. The plugin UI module exposes marketplace navigation and plugin/stage selection helpers. REA recovered a `fetch` endpoint built from a base and a path, with **partial** resolution. This supports keeping discovery, compatibility display, and plugin management in the existing host UI. It does not establish a backend route, installation success, network request, or end-to-end runtime behavior.

The result remains local at `/tmp/gta-rea-marketplace-evidence.json` (110,441,636 bytes), SHA-256 `61a0c6884a1201740a0e4077744d56743d248d4a7c0905d4d04e9b52755ff1ae`. The large size reflects inventory records for the existing UI and dependencies, not 110 MB of selected source analysis. It is intentionally not vendored into this MIT plugin. The working application was already dirty at HEAD `33fe54b45415e525910038a1571bf362f00db2b0`; the evidence identifies the inspected bytes instead of claiming an exact clean commit.

## Limits and independent requirements

REA inventoried 7,487 relevant files but analyzed only the two caller-selected files; 7,485 files remained outside source analysis. Its coverage is partial. It parsed inert text and did not execute the application, bundle bootstrap, plugin, or imported modules. Static relationships do not prove runtime execution. No native provider, browser observation, Twitch/Discord session, or video-quality benchmark was performed by REA.

Only these independently phrased requirements are passed to implementation:

1. Reuse host plugin installation, stage selection, compatibility presentation, and marketplace navigation.
2. Publish machine-readable compatibility information that the existing host can validate.
3. Verify installation and the supported SDK directly; static JavaScript analysis alone cannot establish either.

No REA runtime, model, binary, or dependency is included in the plugin distribution. REA is a research tool, separate from the plugin's dependency audit. This investigation does not establish that Eklipse exposes an inspectable GTA plugin. Competitor observations must remain limited to independently sourced public evidence.

## Repeatability and later persistent integration

The `/tmp` package, npm cache, setup plan, and Evidence are local working artifacts and may disappear. The versions, commands, digests, and limitations above preserve the audit trail. A later machine can repeat the commands in temporary storage; installed dependency resolution may differ unless its lock file is also retained. To connect a persistent Codex session, first run the scoped setup dry run on that machine, inspect its exact destinations and proposed launch command, then approve only the desired configuration and restart Codex. This task leaves that persistent configuration decision unapplied while completing the authorized CLI investigation.

## Windows continuation

See [the pinned isolated Windows run](rea-windows-run.md) for the 2026-10-25 installation, portable runtime checksum, setup dry-run and authorized partial static analysis. No global Codex configuration was applied.
