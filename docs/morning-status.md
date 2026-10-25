# Morning status and remaining checks

Prepared 2026-10-24. Start with the final test output and `git diff`; this
checklist distinguishes implementation evidence from real service and
footage evidence. The requested project display name includes **6**.

## Available locally

- MIT plugin `colingpt9/gta-vi-highlights` version `0.1.0`, with real SDK
  `find`, `understand`, `rate`, and `edit` adapters. Recorded verification:
  **147 plugin tests passed**, including **21 adapter tests**. SDK validation
  has two documented development-only import-path warnings; see
  [SDK audit](SDK_AUDIT.md).
- Eight conservative transcript categories, measured media corroboration,
  bounded mapped nominations, duplicate control, and setup/payoff timing.
  RP, existing-local-model corroboration, trim suggestions, and title overlays
  are off by default. Generic loudness/motion cannot establish a game event.
- The generic SDK sample correctly returned zero GTA events. The original
  48-second synthetic source and authored transcript produced a crash range
  at 11–32 seconds. The existing host exported a real captioned MP4 at
  `/workspace/scratch/gta-plugin-demo/highlight-01.mp4` and retained a
  provenance manifest and isolated history. No human clip-quality review or
  real GTA accuracy is claimed.
- Final host verification: **464 tests passed** across account, Twitch,
  workflow, SDK gateway, renderer demo, watch, WoopSocial, and API checks.
  UI client checks, TypeScript checks, production build, Python lint, and API
  reference checks passed. An isolated CLI startup verified healthy service,
  session-protected account/workflow routes, and sanitized account metadata.
  The final demo export is at
  `/workspace/scratch/gta-plugin-demo-final/highlight-01.mp4`.
- Synthetic regression fixtures and recorded comparisons with the original
  energy-only reference. This reference is not the host's production finder.
  See [evaluation](EVALUATION.md) and its [results](../evaluation/results/current.md).
- New reusable local host work for nominations, explicit source/VOD mapping,
  manually approved/exportable digests, and authorized VOD-native clip
  requests. Matching current host/SDK changes are required; these changes
  are on the separate Clips Studio `codex/twitch-connected-accounts` review
  branch. An approved digest without a delivery adapter stays unsent.
- Dependency/license inventory, actual scoped REA investigation, independent
  functional specification, benchmark rubric, and real demo instructions.
- Marketplace contribution format and existing GTA section researched from
  `awesome-clips-kitty@cf3b87a88fe3b44017a5eaabbb991f9746509559`. Static listing
  fields were validated with the actual registry validator; the template's
  deliberate release-commit marker correctly fails installation validation.

The display name includes **6**. The actual source remote still lacks `6`;
The GitHub integration's rename permission returned HTTP 403. The intended new URL is not
claimed as an existing renamed or published repository. Marketplace
publication and hackathon submission remain pending.

## Must be completed with real accounts or media

| Check | Current evidence / blocker | Next action |
| --- | --- | --- |
| Real GTA clip quality | No rights-cleared gameplay or reviewed baseline/plugin exports supplied | Provide authorized source; run identical baseline/plugin settings and score [benchmark rubric](../research/benchmark.md) |
| GTA VI accuracy | No authentic GTA VI test footage evaluated | Label current tests honestly; test later against authorized actual footage |
| Live Twitch nomination | Mock/contract tests cannot establish live provider behavior | Use authorized broadcaster/viewer accounts, verify real accepted command affects candidate |
| Native Twitch clip | Requires current documented endpoint authorization and available VOD | Exercise with consenting broadcaster/editor; verify returned clip through API |
| Timestamp accuracy | Needs playable VOD and checked source mapping | Click generated link and observe intended event |
| Real Discord digest | Separate delivery adapter, credentials, installation, channel permissions, and explicit posting approval required; current no-adapter digest remains unsent | Connect the approved adapter; send test digest and verify real links, retry/duplicate behavior, and disconnect |
| Public viral references | Public access may be restricted; no invented counts or visual review | Follow verified source record; add authorized observations when access permits |
| Hackathon eligibility | Current official rules must be reviewed; access restrictions recorded separately | Verify rules, window, prior-work policy, required assets, and deadline directly |
| Marketplace release | Public immutable commit with manifest required | Confirm real repository URL, release commit and SDK listing validation; prepare one-file catalog PR |
| Submission/demo | No session ID, public recording, or submission provided by repository | Retrieve real session ID and record a rights-cleared functional demo |

Keep automatic posting off until the creator opts in. A real delivery test
is separate from a mocked test and requires the owner's authorized test
server/channel. Publishing a repository, catalog PR, or public demo is a
separate release action.

## Suggested order

1. Read the recorded tests and SDK warnings; use the matching local host/SDK
   additions until they are released.
2. Run the plugin through Clips Kitty on authorized GTA V footage, inspect
   the video, and complete at least one comparable benchmark case.
3. Connect consenting Twitch accounts, receive a nomination, and verify a
   real VOD timestamp/native clip result.
4. Preview and explicitly approve a real test-channel digest.
5. Verify official rules, project URL, release commit, listing, and session
   ID; then record only completed functionality using [demo.md](demo.md).

Do not present synthetic fixture success as real footage quality, a dry-run
setup as an installed REA MCP server, a draft listing as a published
marketplace release, or mock provider tests as live Twitch/Discord success.
