# Release verification — 2026-10-25

Published release: [plugin v0.2.0](https://github.com/ColinGPT9/Grand-Theft-Auto-6-Clips-Kitty-Plugin/tree/v0.2.0),
commit `0ce46132e7d8b8b34950f9c46953a4ee80448302`.
The [Awesome Clips Kitty listing](https://github.com/ColinGPT9/awesome-clips-kitty/blob/main/registry/pipelines/colingpt9/gta-vi-highlights.yaml)
is merged and its generated README/index rebuilt successfully.
No Microsoft Store packaging, upload,
application version bump or contest submission was performed.

## Verified

- Existing baseline: 147 plugin tests. Integrated release: **168 passed**.
- Actual SDK 1.3.0 validation passes with three development-only path warnings.
- Linux and Windows release CI pass. The pinned public source installs into
  an isolated task profile through the actual host plugin manager.
- SDK subprocess find + understand selects source 11–32 seconds from original
  generated media; generic SDK sample returns zero GTA events.
- Rate + understand and edit use separate SDK jobs over supplied moments.
- The host exporter produces horizontal and 1080×1920 vertical H.264 MP4s:
  each 21 seconds with audio, authored captions and isolated history.
- The generic host fixture verifies decoding, caption timing and history
  without importing the GTA plugin.
- An independent implementation context received only clean requirements,
  original plugin source and SDK interfaces.
- Frozen comparisons: [quality report](QUALITY_IMPROVEMENTS.md).

Local media/logs remain outside the installable repository under
`D:\clips_research\gta-release\artifacts`. They contain geometric test
media and tones, not gameplay. Reproduction: [demo.md](demo.md).

## Pending public demonstration

Rights-cleared GTA V footage and visual review; live Twitch connection,
viewer nomination and VOD alignment; an authorized native clip or mapped
timestamp link; approved delivery through Clips Studio to a selected Discord
test destination; actual Codex session ID, public YouTube video and Devpost form.

The plugin contains no Discord transport. Host tests use fake network responses.
Public engagement metadata is research, not a gameplay benchmark.
Generic host integration is tracked in
[Clips Studio #188](https://github.com/ColinGPT9/clips-studio/pull/188), with
244 focused host tests passing locally. The host's full Python CI also passes;
local full-suite collection is limited by the existing Windows Python/pytest
temporary-file test objects, and one tutorial execution needs Bash.
