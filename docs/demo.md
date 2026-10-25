# Real demonstration checklist

Project: **Grand Theft Auto 6 Clips Kitty Plugin**. This is an unofficial
MIT plugin built on pre-existing Clips Kitty and its MIT SDK. Demonstrate
GTA V footage only when authorized, and label it clearly. GTA VI readiness
is a design goal; no GTA VI footage or accuracy was tested here.

## Prerequisites

- A running compatible Clips Kitty host, this plugin installed and enabled,
  FFmpeg/FFprobe, and an authorized local source with a usable transcript.
- A real Twitch developer application and a broadcaster account consenting
  to the required scopes. Use the host's account connection; do not paste
  tokens or client secrets into a recording or plugin setting.
- A playable Twitch VOD for that source, plus a checked local-source-to-VOD
  time mapping. Seek through a generated link and confirm the selected
  event actually plays at that offset.
- A consenting viewer/test account using an actual nomination command and
  the host's real chat/EventSub connection. Confirm the event reaches the
  source's timeline and changes priority or score compared with no nomination.
- An authorized Discord bot installed in a test server, a selected channel,
  and permission to send messages and embed links. Keep automatic delivery
  disabled until the creator explicitly opts in.
- Permission to show all footage, music, usernames, chat, marks, and assets
  in a public demo. Redact secrets and unnecessary viewer information.

No credentials, provider permissions, public video upload, or gameplay rights
are supplied by this repository. Unit mocks and synthetic media do not
complete the real service steps below.

## Under-three-minute recording outline

| Time | Show | Proof to retain |
| --- | --- | --- |
| 0:00–0:20 | A viewer missed a stream and needs a catch-up | Brief, original problem statement |
| 0:20–0:45 | Installed plugin, supported SDK, event preferences | Actual host installation and manifest validation |
| 0:45–1:15 | Real Twitch viewer uses `!chaos`, `!clip`, or `!funny` | Accepted nomination and before/after priority or score |
| 1:15–1:50 | Evidence-backed GTA event and generated clip | Source timestamp, factual category/reason, playable export |
| 1:50–2:20 | Manually approved catch-up reaches Discord | Real sent message; click timestamp/native clip and verify event |
| 2:20–2:40 | Codex development and meaningful checks | Actual tests/session history; no fabricated session ID |
| 2:40–2:55 | MIT source, installation, prepared marketplace listing | Accurate publication state and current repository URL |

Leave several seconds of margin: a video exactly three minutes may fail a
strict “under three minutes” requirement. The listed submission requirements
come from the supplied brief until current official rules are verified.
Check [public source research](../research/public-sources.md) for rule access
status; a blocked rules page is not confirmation of eligibility or deadline.

## Before calling the demo complete

- [ ] Run actual SDK validation and a real host plugin subprocess.
- [ ] Analyze rights-cleared source and visually inspect a playable export.
- [ ] Show missing evidence does not fabricate a game event.
- [ ] Receive a live viewer nomination; demonstrate its bounded effect.
- [ ] Observe stream/VOD discovery through the reused host workflow.
- [ ] Verify source-to-VOD mapping by seeking the generated timestamp link.
- [ ] Create a native Twitch clip only with the required authorization;
  retrieve its real status/URL, otherwise show the documented VOD fallback.
- [ ] Preview and explicitly approve a digest to a selected test channel.
- [ ] Check the real Discord message, links, duplicate protection, and disconnect.
- [ ] Review the current official hackathon rules and eligibility window.
- [ ] Disclose existing host/SDK work and new work using [provenance.md](provenance.md).
- [ ] Retrieve the real Codex session ID using the session's `/status` or
  currently documented UI; record it privately for submission.
- [ ] Publish an accessible source commit and public demo only after review.

## Failure cases worth showing briefly

An unavailable VOD leaves a clear unavailable/pending state. Unsupported
native clip permissions produce a timestamp link rather than an invented
clip URL. Missing local model/transcript produces an honest limitation.
Provider rate limits and reconnects do not cause duplicate analysis or
duplicate messages. A viewer's repeated command cannot unconditionally
force a highlight.
