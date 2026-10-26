# Demo and contest checklist

Use a compatible Clips Studio source checkout and its normal video dependencies.
The plugin uses only the MIT SDK; rendering stays in the host.

## Reproducible synthetic export

Generate the original media and run all SDK stages using the commands in
[README](../README.md). Finder and moment-rating jobs are separate; edits
are a third job. Missing semantic evidence returns zero highlights.

From the host checkout, run the generic exporter:

```powershell
python scripts/demo_plugin_export.py --plugin "<plugin checkout>" `
  --video "<scratch>/demo.mp4" --transcript "<scratch>/demo.transcript.json" `
  --synthetic-demo --max-clips 1 --output "<scratch>/horizontal"
python scripts/demo_plugin_export.py --plugin "<plugin checkout>" `
  --video "<scratch>/demo.mp4" --transcript "<scratch>/demo.transcript.json" `
  --synthetic-demo --max-clips 1 --vertical --output "<scratch>/vertical"
```

Keep output outside both source folders. Each checked export is 21 seconds
(source 11–32), with audio, burned authored captions, a provenance manifest
and isolated history. Decoded frames were inspected for caption placement
in horizontal and vertical layouts. This is an integration demonstration,
not actual gameplay, speech transcription or a clip-quality benchmark.

## Live demonstration still required

Use footage you can show, a real consenting Twitch account, permitted viewer
nominations and checked source/VOD calibration. Credentials stay in the
host's Connected Accounts. Use a saved authorized Discord webhook destination
in Clips Studio; approve the frozen destination/items before sending.
The plugin never sends the message. No live service result is claimed by
the synthetic checks.

| Time | Show |
|---|---|
| 0:00–0:20 | Missed-stream catch-up problem and the standalone GTA plugin |
| 0:20–0:45 | Installed plugin, event preferences and source transcript |
| 0:45–1:15 | Actual Twitch viewer nomination and bounded supporting evidence |
| 1:15–1:50 | Selected GTA V event, factual reason and playable export |
| 1:50–2:20 | Approved host digest reaches Discord; click and verify the link |
| 2:20–2:40 | Actual Codex development and meaningful test evidence |
| 2:40–2:55 | Source, setup, license and accurate release status |

The [official rules](https://twitchcon-codex.devpost.com/rules), verified
2026-10-25, require a public YouTube demo under three minutes showing Twitch
operation and Codex development. [Provenance](provenance.md) records the
submission window, reused foundations and required session ID.

## Before submission

- [x] SDK validation and actual plugin subprocess.
- [x] Generated-media exports, captions and isolated history.
- [x] Missing evidence produces no invented GTA event.
- [ ] Rights-cleared GTA V source and human review.
- [ ] Live nomination and verified source/VOD link.
- [ ] Authorized native clip/public URL, or correctly mapped timestamp fallback.
- [ ] Actual approved Discord message through Clips Studio.
- [ ] Actual Codex session ID and public YouTube demo URL.
- [ ] Final Devpost entry and organizer eligibility check.

Do not replace unavailable native clips with invented URLs, equate request
acceptance with publication, or label mock-provider tests as live Twitch proof.
