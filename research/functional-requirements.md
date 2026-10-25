# Independent functional specification

Version 1, 2026-10-24. This specification is derived from the user's brief,
the public MIT SDK contract, official service documentation where available,
and general clipping behavior. Public competitor observations and their
limitations are kept in [public-sources.md](public-sources.md). No
competitor source, private API, decompiled implementation, or assets were
used. Separate research and implementation agents exchanged functional
requirements; this shared session is not claimed as a strict independent
clean room.

| ID | Requirement | Observable acceptance condition |
| --- | --- | --- |
| FR-01 | Detect GTA-style moments through the actual Clips Kitty SDK | SDK manifest validation and a host-compatible subprocess run accept the result |
| FR-02 | Require semantic evidence before assigning a game event | Loud audio, scene cuts, frame movement, colors, chat, or a model alone cannot assert a crash, NPC incident, chase, or reaction |
| FR-03 | Combine independent available signals with bounded influence | A timestamped reason identifies the semantic source and supporting signals; repeated equivalent evidence cannot inflate the score without bound |
| FR-04 | Keep setup, action, and reaction where available | Selected ranges include configurable lead and tail, respect video bounds and creator duration limits, and report any shortened context |
| FR-05 | Suppress overlapping duplicate moments | Repeated transcript mentions, correlated signals, and nominations for the same event produce one best candidate under the documented overlap rule |
| FR-06 | Treat roleplay as source-dependent | RP categories are disabled by default and require explicit source configuration; no GTA VI launch or server capability is assumed |
| FR-07 | Fail safely when evidence is missing | Missing transcript, optional model, audio, or footage produces a clear limitation or empty result rather than invented detections |
| FR-08 | Keep titles factual | Titles and reasons describe supported evidence and do not invent people, weapons, wanted levels, success, or outcomes |
| FR-09 | Reuse host analysis and rendering | Plugin uses SDK transcript, FFmpeg/media helpers, and optional local model; Clips Kitty owns acquisition, transcription, rendering, captions, history, and posting |
| FR-10 | Use community interaction as corroboration | An accepted viewer nomination influences review priority or bounded score; cooldowns and duplicate prevention limit flooding |
| FR-11 | Keep integrations in the reusable host | Twitch/Discord credentials, discovery, native clip API calls, monitoring, and digest publication never enter the game detector |
| FR-12 | Preserve source-relative timing | Host maps local source offsets to validated VOD offsets; missing or invalid mapping cannot create a misleading timestamp link |
| FR-13 | Report real delivery state | Timestamp VOD links are a fallback; native clip links appear only after the API returns a real clip; Discord posting requires configured credentials and explicit authorization |
| FR-14 | Make automatic posting opt-in | Creator can select destination and digest size and preview manually; duplicate delivery and provider retry behavior are tested in the host |
| FR-15 | Separate technical validation from footage quality | Synthetic contract tests may validate timing and scoring, but cannot establish visual quality, virality, or GTA VI accuracy |

The taxonomy is independently specified around police pursuits, vehicle
crashes, stunts, combat, NPC/accident comedy, dialogue, opt-in roleplay,
unexpected failures, and streamer reactions. Categories remain hypotheses
about footage until supported by actual source evidence. Model descriptions
and transcript mentions can be wrong; low-confidence candidates should be
reviewed by a creator.

Public descriptions do not reveal a competitor's model, algorithm,
thresholds, or inference quality. No implementation requirement depends on
an inferred proprietary mechanism. When a source cannot be accessed, its
claim remains unverified and cannot justify a benchmark result.
