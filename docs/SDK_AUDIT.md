# SDK and host reuse audit

The plugin was scaffolded with the actual SDK command:

```text
python -m clipskitty_sdk new /tmp/gta-vi-highlights --template game-events \
  --publisher colingpt9 --game gta-vi --author ColinGPT9 --license MIT
```

Its original MIT template notice is retained as `TEMPLATE-LICENSE.txt`.
No AGPL-only application source is copied into this plugin.

| Need | Supported interface used | Owner |
| --- | --- | --- |
| Find ranges | `Job.add_range` and `run(main)` | MIT SDK |
| Transcription | `Job.transcript.segments()` | Host provides cached Whisper output |
| Low-level video evidence | `media.probe`, `media.frames`, `signals.difference`, `signals.brightness` | MIT SDK, host-provided FFmpeg |
| Audio evidence | `media.loudness`, `signals.spikes` | MIT SDK, host-provided FFmpeg |
| Explain and rate | `Job.understand`, `Job.rate`, handed `Moment.signals` | MIT SDK |
| Optional edits | `Job.suggest_edit(...).trim/title_overlay` | Host applies suggestions after approval |
| Optional local AI | `local_model.ask(..., json=True, timeout=15)` | Existing local model only; no cloud fallback |
| Audience context | Optional `job.accounts.twitch.audience_signals()` | Host account gateway and calibrated timeline |
| Account lifecycle and Twitch API | Connected Accounts | Main application; no tokens handed to plugin |
| New VOD discovery, restart/duplicates | Existing Watched Channels and queue | Main application |
| Video exports, framing, captions | Existing renderer/caption pipeline | Main application |
| Discord and social publishing | Existing/supported host services | No plugin publisher stage; Discord work separate |

The runtime imports only Python standard-library modules, the MIT SDK, and its
own modules beside `src/main.py`. It installs no Whisper, Gemma, YOLO, NumPy,
PyTorch, or other plugin-specific model/decoder stack. Pixel/audio changes are
supporting evidence and are not object recognition. The local model is optional
and cannot introduce an event without source evidence. Roleplay is source opt-in.

`inputs: [video, transcript, moments]` and
`outputs: [ranges, context, ratings, edits]` follow the SDK's combined finder /
rater / understander / editor contract. A finder returns ranges; moment runs
answer only about supplied moment IDs. Edits are suggestions with opt-in trim and
title overlay. Clips Kitty retains rendering, history, source acquisition and
publishing.

The development evaluation tools deliberately run outside the plugin process.
The SDK's conservative folder-wide linter currently reports two development-only
import-path warnings for `evaluation/run.py` and `scripts/evaluate.py`; the runtime
entry and its own modules use supported paths, and actual SDK subprocess tests
exercise them. These warnings are not represented as failed runtime checks.
