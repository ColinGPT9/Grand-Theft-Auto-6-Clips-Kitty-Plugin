# Hackathon provenance

Updated 2026-10-25. Project: **Grand Theft Auto 6 Clips Kitty Plugin**,
a standalone MIT SDK pipeline.

## Existing foundation

Clips Kitty, its MIT SDK, acquisition, transcription, models, rendering,
captions, history, publishing, marketplace and account infrastructure are
reused foundations. The initial plugin baseline is commit `4200ade`,
version 0.1.0, with 147 tests. Host Twitch support merged in clips-studio #182;
publishing/Discord integration merged in #186. Tested host baseline:
`5b87c6a7da509e3f34a8dfbefc031258107e439a`.
Do not represent the whole application as new plugin work.

## Work in this continuation

The 0.2.0 diff adds original context rejection, utterance preservation,
setup/reaction association, distinct-event handling, explanations, review-only
truncation safeguards, fixtures and measured regressions.
The independent implementation context used only clean functional requirements,
original plugin/SDK source and fictional fixtures. Dirty-room notes and
competitor implementations were not implementation inputs.

Separate host work supplies the necessary generic approved-digest Discord
adapter and startup wiring. A generic export example replaces a GTA-named
host demo; GTA instructions live here. Host work remains host-licensed.
Credentials, Discord and rendering stay in Clips Studio.

REA ran separately on authorized MIT source with partial static coverage.
It did not inspect Eklipse's proprietary detector.
[REA record](../research/rea-review.md) and
[quality report](QUALITY_IMPROVEMENTS.md) record limits.

## Submission requirements

The official [rules](https://twitchcon-codex.devpost.com/rules), checked
2026-10-25, set the submission window to October 23–November 2, 2026,
ending 2 PM Pacific. The entry must be new work during that window,
use Codex and connect interactively to Twitch. Disclose reused foundations.

Provide runnable source and setup instructions, a project/Codex-use description,
the actual development session ID, and a public YouTube demo under three minutes
showing Twitch operation and Codex development. Demo assets need permission.
Open-source enhancements are allowed subject to licenses; organizers determine eligibility.

The [official FAQ](https://twitchcon-codex.devpost.com/resources) explains
session-ID retrieval and judging access. No session ID was fabricated or
replaced with a commit, REA identifier or tool-run ID.

## Evidence boundaries

Synthetic checks establish integration and authored regressions, not live
service operation, real GTA quality, virality or GTA VI accuracy. Gameplay
review, live account recording, public video and Devpost submission remain
pending. No Store package or upload is part of this release.
