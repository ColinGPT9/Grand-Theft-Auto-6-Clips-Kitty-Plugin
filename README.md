# Grand Theft Auto 6 Clips Kitty Plugin

An unofficial **MIT** Grand Theft Auto highlight detector for **Clips Kitty**,
targeting **GTA V (GTA 5)** gameplay and **GTA VI (GTA 6)** support. It finds explicit
event cues in the host transcript, adds measured audio/picture evidence and
permitted viewer nominations, and returns explainable clip suggestions.

**Version:** `0.3.0` · **ID:** `colingpt9/gta-vi-highlights`
**Compatibility:** Python 3.11, plugin API 1, SDK 1.3.0, Clips Kitty `>=2.1.0`.
Use [Clips Studio main](https://github.com/ColinGPT9/clips-studio);
Connected Accounts/Twitch support is merged. Store packaging is outside this release.

## What it does

- In the app choose **Gaming / Reaction → Gaming detector**. GTA specializes
  highlight finding and scoring while sharing Gaming's webcam layouts,
  captions, editor and publishing. The generic Gaming finder is not also run.
  Detector defaults are used without extra settings fields. Sports does not
  offer gaming detectors or accept their rate/understand/edit stages.
- Finds chase, crash, stunt, combat, NPC chaos, dialogue, reaction and opt-in
  roleplay cues. Mission/heist status and survival-wave progress have their own
  event category. Rejects historical stories, hypothetical plans and retractions
  conservatively.
- Preserves supported transcript utterances and nearby setup/reaction within
  duration limits. Distinct events survive overlapping windows.
- Produces factual titles, score components, observed modalities,
  duplicate-suppression reasons and review warnings.
- Withholds a find range when its supporting utterance would be truncated;
  retains that candidate as review-only in the local explanation report.
- Supports **find**, **understand**, **rate**, and opt-in **edit** suggestions.
  Scores rank evidence; they are not probabilities or predicted views.

The detector needs explicit semantic transcript evidence. Motion and loudness
do not identify police, vehicles, collisions or faces from pixels. It misses
untranscribed incidents. No GTA VI gameplay or real-world accuracy claim is supported.

## GTA highlights for Twitch, YouTube Shorts, TikTok and Reels

Use GTA-specific event finding for Grand Theft Auto V, GTA Online and GTA-style
roleplay streams, including mixed gameplay and chatting. It does not require a
correct platform category. Chases, vehicle incidents, combat, mission progress,
reactions and optional RP cues are reviewable suggestions backed by source evidence.
GTA VI is a development target; GTA VI gameplay accuracy has not been tested.

Clips Kitty supplies the shared facecam/game layout, captions, clip editor and
publishing workflows for Twitch clips, YouTube Shorts, TikTok and Instagram Reels.
Install the plugin from its [Awesome Clips Kitty listing](https://github.com/ColinGPT9/awesome-clips-kitty/blob/main/registry/pipelines/colingpt9/gta-vi-highlights.yaml),
then choose it under Gaming. Discord and Twitch credentials stay in the host.

## Repository boundary

**This plugin owns GTA detection and suggestions. Clips Studio owns Twitch
connections, VOD calibration, viewer nominations, Discord delivery,
publishing, captions, rendering and history.** The plugin receives permissioned
read-only Twitch context through the MIT SDK. It contains no Discord client,
webhook, credential storage, OAuth flow or publisher. Manifest `network` and
`sends` permissions are empty.

Runtime imports are its own code, Python's standard library and the MIT SDK.
No additional model, downloader, decoder stack or renderer is installed.
Local-model corroboration is on by default and cannot create an
unsupported event.

## Install and test

Clone the host and plugin as siblings. Keep the environment outside the plugin
because the host copies the installation folder.

```bash
git clone https://github.com/ColinGPT9/clips-studio.git
git clone https://github.com/ColinGPT9/Grand-Theft-Auto-6-Clips-Kitty-Plugin.git
python3.11 -m venv .venv-gta
source .venv-gta/bin/activate
python -m pip install -e './clips-studio/sdk/python[yaml,test]'
cd Grand-Theft-Auto-6-Clips-Kitty-Plugin
python -m clipskitty_sdk validate .
python -m pytest
```

On Windows use `py -3.11 -m venv .venv-gta` and activate
`.venv-gta\Scripts\Activate.ps1`. Validation passes with three development
import-path warnings; actual SDK subprocess tests pass.
See [SDK audit](docs/SDK_AUDIT.md).

Start a compatible host, install the folder, review permissions and enable
the desired pipeline stage:

```bash
python -m clipskitty_sdk install .
```

An older installed app may lack the required plugin APIs; this release does
not update or package the application.

## Reproduce the technical demo

Use absolute scratch paths outside both repositories and your actual FFmpeg path:

```bash
python scripts/generate_demo.py /tmp/gta-demo.mp4 --ffmpeg /usr/bin/ffmpeg
python -m clipskitty_sdk run . --video /tmp/gta-demo.mp4 --transcript /tmp/gta-demo.transcript.json --steps find understand --job-dir /tmp/gta-find
python -m clipskitty_sdk run . --video /tmp/gta-demo.mp4 --transcript /tmp/gta-demo.transcript.json --steps rate understand --moments /tmp/gta-find/result.json --job-dir /tmp/gta-rate
python -m clipskitty_sdk run . --video /tmp/gta-demo.mp4 --transcript /tmp/gta-demo.transcript.json --steps edit --moments /tmp/gta-find/result.json --set trim_to_event=true --set title_overlay=true --job-dir /tmp/gta-edit
python scripts/evaluate.py
```

The generated 48-second geometric video has tones and authored fictional
commentary, not gameplay or speech. The plugin selects source **11–32 seconds**.
The generic SDK `--sample` returns zero GTA moments.
[Demo instructions](docs/demo.md) cover captioned MP4 and vertical export
through the host renderer.

## Settings

| Setting | Default | Purpose |
|---|---|---|
| `min_score` / `min_confidence` | 42 / 35 | Evidence thresholds, 0–100 |
| `lead_in` / `payoff` | 8 / 10 seconds | Setup and reaction allowance |
| `max_highlights` | 10 | Maximum outputs, also bounded by host |
| `enabled_categories` | empty | All categories, or comma-separated IDs |
| `roleplay_enabled` | false | Explicitly enable for RP sources |
| `use_media` / `use_nominations` | true / true | Available supporting measurements/context |
| `use_local_model` | true | Existing local-model corroboration |
| `trim_to_event` / `title_overlay` | false / false | Optional edit suggestions |
| `write_report` | true | Local schema-2 explanation JSON |

See [clipskitty.yaml](clipskitty.yaml). Unavailable inputs do not become
fabricated observations.

## Verification and contest evidence

**210 tests pass** locally against the real SDK. On unchanged synthetic
fixtures, mean setup coverage increased from **86.71% to 93.06%**; detection
counts remained TP 9 / FP 0 / FN 1. Thirty additional authored adversarial
cases now pass. Their public holdout was visible during implementation and
is not blind validation. [Full comparison](docs/QUALITY_IMPROVEMENTS.md).

[Release verification](docs/morning-status.md) records SDK/media checks.
[Real footage review](docs/REAL_FOOTAGE_REVIEW.md) records actual public YouTube
facecam stream excerpts, Twitch clips, frozen comparisons and remaining misses.
[Contest checklist](docs/demo.md) separates them from pending live Twitch,
authorized Discord, rights-cleared gameplay and the public demo/session ID.
Discord delivery is tested in the host with mocked responses; no real
message or native Twitch clip is claimed here.

The [Awesome Clips Kitty contribution](marketplace/listing.md) uses the existing
catalog. No Store app upload is included.

## Documentation and license

- [Quality improvements](docs/QUALITY_IMPROVEMENTS.md)
- [Provenance and contest requirements](docs/provenance.md)
- [Public GTA V references](research/video-references.md)
- [Independent requirements](research/functional-requirements.md)
- [REA research](research/rea-review.md)
- [License inventory](docs/license-audit.md)
- [Evaluation method](docs/EVALUATION.md)

Original code and fictional fixtures are [MIT](LICENSE). The SDK scaffold
notice is retained in [TEMPLATE-LICENSE.txt](TEMPLATE-LICENSE.txt).
Clips Studio remains separately AGPL-licensed. No competitor implementation,
gameplay assets or logos are bundled. Not affiliated with Rockstar Games,
Take-Two, Twitch, Discord or Eklipse.
