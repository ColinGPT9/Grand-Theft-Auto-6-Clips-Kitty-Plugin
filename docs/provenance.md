# Hackathon provenance and submission notes

Prepared 2026-10-24. The display name requested by the owner is **Grand
Theft Auto 6 Clips Kitty Plugin**. The current checkout was originally
provided as `ColinGPT9/Grand-Theft-Auto-Clips-Kitty-Plugin`; the owner's
intended repository name is `ColinGPT9/Grand-Theft-Auto-6-Clips-Kitty-Plugin`.
Confirm the actual remote and public release URL before submitting or
generating a registry entry. A local name change alone does not rename a
GitHub repository.

## Existing work

Clips Kitty, its MIT Python SDK, game-events scaffold, media/signal helpers,
local model abstraction, host job queue, source acquisition, analysis,
rendering/captions, publishing, Watched Channels/feed monitoring, marketplace,
and the supplied connected-account/Twitch work existed in the workspace
before this plugin task. They are reused foundations, not newly authored
plugin features. `clips-studio` HEAD was
`33fe54b45415e525910038a1571bf362f00db2b0`; it had substantial uncommitted
connected-account/Twitch changes when this task began. Do not attribute
that dirty baseline to new plugin work or overwrite it.

## New work in this task

- Original standalone GTA event taxonomy, evidence-based detection and
  bounded scoring, source-dependent RP, setup/payoff timing, duplicate
  prevention, SDK stage adapters, and fixtures/tests, as present in the
  final source and test report.
- Independent requirements and research records, actual authorized REA
  use, dependency/model audit, evaluation protocol, release checklist,
  demo instructions, and a catalog-schema-based listing draft.
- New local host additions include `stream_workflows/`,
  `server/stream_workflows_api.py`, `scripts/demo_gta_plugin.py`, their docs
  and tests, plus VOD-native clip operations added to the existing
  `connected_accounts/twitch.py`. These remain host-licensed work and are
  separate from the pre-existing connected-account baseline. Final host
  diffs identify the exact additional changes. Provider mocks and synthetic
  rendering checks do not establish real Twitch or Discord operation.

The list describes task scope, not proof of hackathon eligibility. Verify
the official submission window and record the actual creation dates,
commits, substantial new functionality, and allowed use of pre-existing
code under the current rules. Neither the user's stated deadline nor a
local clock establishes the official window.

## Codex record

Codex was used to inspect the real SDK, implement and review the plugin,
write tests, inspect integration boundaries, investigate public sources,
run REA on authorized open source, and prepare documentation. Separate
research and implementation agents exchanged functional requirements.
No proprietary competitor implementation was inspected or copied; the
shared session is not described as a strict independent clean room.

Codex session ID: **not retrieved in this document**. Use the live session's
`/status` or current documented interface, retain the actual identifier,
and supply it in the final submission. Do not substitute a repository,
REA Evidence ID, tool execution ID, or an invented value.

## Submission record to complete

| Item | Required evidence |
| --- | --- |
| Rules and eligibility | Official rules URL, retrieval date, verified window and restrictions |
| Repository | Public source URL and immutable release commit with setup instructions |
| Prior work | Existing host/SDK and dirty Twitch baseline disclosure above |
| New work | Final plugin files, tests, and separately identified host changes |
| Codex use | Concise explanation and actual session ID |
| Demonstration | Public video under three minutes, rights-cleared assets, actual working features |
| Twitch interaction | Real account connection, viewer participation, and useful result |
| Catch-up delivery | Real Discord message with verified playable Twitch link |
| Quality claims | Actual rubric results on authorized footage; none inferred from synthetic tests |

No hackathon submission, marketplace PR, message to another person, GitHub
publication, or public video upload is performed by these documents.
