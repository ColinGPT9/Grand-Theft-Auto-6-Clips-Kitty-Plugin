# Grand Theft Auto 6 Clips Kitty Plugin

An unofficial, independently developed **MIT** highlight plugin for GTA-style
gameplay, built with the Clips Kitty SDK. It finds explicit event cues in the
host transcript, adds measured audio/picture evidence and permitted viewer
nominations, and returns explainable moments to Clips Kitty for rendering.

**Local version:** `0.1.0` · **Plugin ID:** `colingpt9/gta-vi-highlights` ·
**Contract:** plugin API 1, SDK 1.3.0, manifest target Clips Kitty `>=2.1.0`.
The Twitch context permission additionally requires the matching
Connected Accounts SDK/host changes on Clips Studio's
[`codex/twitch-connected-accounts` branch](https://github.com/ColinGPT9/clips-studio/tree/codex/twitch-connected-accounts).
These are development branches awaiting review, not a released app or plugin.

The current source remote is
[ColinGPT9/Grand-Theft-Auto-Clips-Kitty-Plugin](https://github.com/ColinGPT9/Grand-Theft-Auto-Clips-Kitty-Plugin).
The intended name is `ColinGPT9/Grand-Theft-Auto-6-Clips-Kitty-Plugin`.
The GitHub integration lacks permission to rename repositories (HTTP 403).
The implementation is on the `codex/gta6-highlights` review branch; select
that branch to see the plugin files. No remote rename or release is claimed.

## What it does

- Classifies transcript cues into **chase, crash, stunt, combat, NPC chaos,
  funny dialogue, roleplay, and reaction**. Roleplay requires explicit opt-in.
- Corroborates those cues with sampled frame differences, brightness/scene
  changes, and relative loudness. These measurements do not recognize police,
  vehicles, explosions, or faces from pixels.
- Uses mapped Twitch nominations as bounded supporting evidence when the
  host supplies a verified source timeline. Repeated signals do not force
  selection or publish anything.
- Optionally asks the creator's existing local model to corroborate an
  already grounded candidate. This is off by default; no model is installed
  and no cloud fallback is used.
- Supports all four SDK stages: **find**, **understand**, **rate**, and
  **edit**. Optional trim/title suggestions are off by default; the host
  retains approval and rendering.
- Preserves setup and payoff windows, suppresses duplicate moments, and
  writes a local `gta-highlight-explanations.json` report with evidence,
  timestamps, heuristic score, and confidence.

The detector requires semantic source evidence; loudness, motion, chat, or a
model alone cannot establish a GTA event. Commentary can describe something
incorrectly, so categories remain reviewable hypotheses. No GTA VI footage
or detection accuracy has been evaluated.

Clips Kitty owns source acquisition, cached transcription, models, captions,
framing, rendering, history, accounts, and publishing. This plugin imports
only its own modules, Python's standard library, and the MIT SDK. It adds no
Whisper, Gemma, OpenCV, Torch, downloader, renderer, OAuth flow, or publisher.

## Install from source

Use Python **3.11**, FFmpeg/FFprobe, Git, and a matching Clips Kitty source
checkout. The SDK is installed from `sdk/python`, not from a project package
on PyPI. Use the matching host development branch until Connected Accounts
is merged; a stock release does not provide `twitch.context.read`.

The existing repository can be cloned with its current real URL:

```bash
git clone --branch codex/twitch-connected-accounts https://github.com/ColinGPT9/clips-studio.git
git clone --branch codex/gta6-highlights https://github.com/ColinGPT9/Grand-Theft-Auto-Clips-Kitty-Plugin.git
```

With this plugin and `clips-studio` as sibling source directories, run from
their parent directory. Keep the development environment outside the plugin
folder because Clips Kitty copies the installation folder's contents.

```bash
python3.11 -m venv .venv-gta6
source .venv-gta6/bin/activate
python -m pip install -e './clips-studio/sdk/python[yaml,test]'
cd Grand-Theft-Auto-Clips-Kitty-Plugin
python -m clipskitty_sdk validate .
python -m pytest -q
```

On Windows use `py -3.11 -m venv .venv-gta6`, activate
`.venv-gta6\Scripts\Activate.ps1`, and use the same subsequent Python
commands. Start the matching Clips Kitty host, then install the local folder:

```bash
python -m clipskitty_sdk install .
```

Review the host's requested permissions and enable the plugin for the desired
stage. It requests local media/transcript/FFmpeg access, optional local model
access, and read-only Twitch context; `network` and `sends` are empty. The
SDK validator currently reports two development-only import-path warnings;
their scope and actual runtime checks are recorded in [SDK audit](docs/SDK_AUDIT.md).

## Run the reproducible technical demo

Generate original 48-second geometric footage, tones, and an authored
fictional transcript outside the installation folder:

```bash
python scripts/generate_demo.py /tmp/gta-demo.mp4 --ffmpeg /usr/bin/ffmpeg
python -m clipskitty_sdk run . \
  --video /tmp/gta-demo.mp4 \
  --transcript /tmp/gta-demo.transcript.json
python scripts/evaluate.py
python scripts/evaluate.py --split holdout --output /tmp/gta-holdout.json
```

Supply your actual absolute FFmpeg path on other systems. The authored
transcript describes a chase and crash; the audio contains tones, not speech.
The recorded run selects a crash range at **11–32 seconds**. In contrast,
`python -m clipskitty_sdk run . --sample` correctly returns **zero** moments
for the generic SDK sample, which has no GTA event evidence.

To produce an actual MP4 through the existing application renderer, use the
matching host environment with its usual video dependencies installed:

```bash
cd ../clips-studio
python scripts/demo_gta_plugin.py \
  --plugin ../Grand-Theft-Auto-Clips-Kitty-Plugin \
  --video /tmp/gta-demo.mp4 \
  --transcript /tmp/gta-demo.transcript.json \
  --synthetic-demo --output /tmp/gta-app-export
```

This saves a captioned MP4, provenance manifest, SDK job, and isolated history.
A completed local export is available at
`/workspace/scratch/gta-plugin-demo/highlight-01.mp4`. This is technical
SDK-to-host-export evidence, not real GTA footage, a transcription test, or
a human review of clip quality. Generated media is kept outside this repository.

## Configuration

Use the host's plugin settings or SDK `--set name=value` for local runs.

| Setting | Default | Purpose |
| --- | --- | --- |
| `min_score` / `min_confidence` | `42` / `35` | Minimum heuristic evidence thresholds, 0–100 |
| `lead_in` / `payoff` | `8` / `10` seconds | Preserve context around an event, within host limits |
| `max_highlights` | `10` | Bound output count; host clip limit also applies |
| `enabled_categories` | empty | All categories; otherwise comma-separated category IDs |
| `roleplay_enabled` | `false` | Enable only for a source that actually contains RP |
| `use_media` / `use_nominations` | `true` / `true` | Add available measured/mapped supporting evidence |
| `use_local_model` | `false` | Corroborate with the existing local model |
| `trim_to_event` / `title_overlay` | `false` / `false` | Opt into edit suggestions |
| `write_report` | `true` | Save the local explanation report |

See [clipskitty.yaml](clipskitty.yaml) for complete settings and limits.
Missing optional media, model, or audience context produces a note and retains
available source evidence. Missing semantic evidence produces no invented
highlight.

## Twitch, catch-up delivery, and release status

The separate Clips Studio host branch supports nomination collection, verified
source/VOD calibration, manually approved/exportable digests, and authorized
VOD-native clip requests. Credentials remain in the host. Native clip
requests stay pending until Twitch returns a real public URL; timestamp
links require verified source mapping.

These changes are awaiting review on development branches. No authenticated livestream,
real native clip, or full Twitch-to-Discord result was verified in this task.
Discord delivery needs the separately developed adapter and authorized
server/channel configuration. An approved digest without a delivery adapter
remains **unsent**. Automatic posting is off unless the creator opts in.

The plugin's recorded verification passed **147 tests**, including **21
adapter tests**. The [synthetic evaluation](evaluation/results/current.md)
compares authored fixtures with an original energy-only reference, not the
host's production finder. Its metrics do not establish real gameplay quality
or virality. Authorized footage, visual review, real accounts, and a live
demo remain required.

The [marketplace contribution](marketplace/listing.md) uses the actual catalog
schema and GTA section. It remains a draft until a tested public release
commit can be fetched; no live marketplace listing or public release is claimed.

## Documentation and license

- [Morning status and remaining checks](docs/morning-status.md)
- [SDK and host reuse audit](docs/SDK_AUDIT.md)
- [Synthetic evaluation method](docs/EVALUATION.md) and [real-footage rubric](research/benchmark.md)
- [Verified public sources and access limits](research/public-sources.md)
- [Independent requirements](research/functional-requirements.md)
- [Demo checklist](docs/demo.md) and [hackathon provenance](docs/provenance.md)
- [Dependency, model, and media audit](docs/license-audit.md)

Copyright 2026 ColinGPT9. Original plugin code is [MIT](LICENSE); the MIT
scaffold notice is retained in [TEMPLATE-LICENSE.txt](TEMPLATE-LICENSE.txt).
Clips Kitty's separate application retains its AGPL license. No Rockstar
assets, proprietary competitor code, model weights, or gameplay are bundled.
Game/service names identify compatibility; no endorsement is claimed.
