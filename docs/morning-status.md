# Release verification — 2026-10-25

Working release: plugin 0.2.0. No Microsoft Store packaging, upload,
application version bump or contest submission was performed.

## Verified

- Existing baseline: 147 plugin tests. Integrated release: **168 passed**.
- Actual SDK 1.3.0 validation passes with three development-only path warnings.
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
