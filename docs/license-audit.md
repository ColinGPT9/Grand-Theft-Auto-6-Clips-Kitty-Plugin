# Dependency, model, and media audit

Reviewed 2026-10-24. The plugin's original source is MIT, copyright 2026
ColinGPT9. This audit covers the standalone repository; it is not a license
change to the Clips Kitty application.

| Component | License / source | Distribution decision |
| --- | --- | --- |
| Original plugin code and configuration | MIT, [LICENSE](../LICENSE) | Included |
| Game-events scaffold and SDK interfaces | MIT, Clips Kitty `sdk/python/LICENSE`, copyright 2026 ColinGPT9 | Preserve `TEMPLATE-LICENSE.txt`; SDK provided by host, not copied into plugin |
| Python standard library | Python Software Foundation license / Python installation | Host-provided; no Python runtime bundled |
| Clips Kitty application | AGPL-3.0-or-later, separate `clips-studio/LICENSE` | Not vendored; host changes retain AGPL licensing |
| FFmpeg / FFprobe | Build-dependent LGPL/GPL and optional components; inspect the actual host build | Host tools only, not redistributed here |
| PyYAML (SDK manifest validation), pytest (development tests) | MIT | Development environment only; not imported by plugin runtime |
| REA research CLI | MIT primary project, with separately licensed bundled components | Separate temporary research tool, not a runtime dependency; see [REA review](../research/rea-review.md) |
| Whisper / faster-whisper / Ollama / Gemma | Host-dependent code and model terms | No separate install, code, weights, or blanket redistribution permission included |
| Gameplay, captions from public examples, logos, music, datasets | Rights vary by owner and source | No assets included; rights-cleared demonstration footage must be supplied separately |

Source evidence: `clips-studio` checkout at
`33fe54b45415e525910038a1571bf362f00db2b0`, specifically
`sdk/python/pyproject.toml`, `sdk/python/LICENSE`, SDK `__version__` 1.3.0,
and `docs/developers/first-game-pipeline.md`. The SDK declares no required
runtime dependencies. Its optional `yaml` and `test` extras are development
tools. The plugin runtime must import only Python's standard library and
`clipskitty_sdk`; no NumPy, OpenCV, Torch, or private host module is assumed.

Optional local model access uses the creator's existing host configuration.
The plugin ships no model and does not require any particular model family.
Model availability is a capability check, not a promise of unrestricted
license rights or measured detection accuracy. A creator must accept the
selected model's terms through their existing installation. Missing model
support must leave deterministic evidence-based detection usable.

Before release, confirm the manifest still declares only the permissions
the implementation uses, inspect all imports, and review any new package or
model before adding it. If a dependency is later redistributed, add its
exact version, upstream source, SPDX license, relevant notices, and any
model or dataset restrictions here. Do not copy AGPL-only host code or
competitor implementation code into this MIT repository.

The standalone plugin may be installed alongside Clips Kitty under its
documented SDK boundary. This inventory records that boundary and does not
offer legal advice on every possible combined distribution.
