# Private Fanum GTA comparison: recorded results and limits

This is a sanitized summary of the actual hosted Eklipse GTA V run and actual
Clips Kitty runs. Raw observations, footage and provider media stay outside this
repository. The results are retrospective tuning evidence, not a blind quality
benchmark or proof of parity with Eklipse.

## Input and method

Colin approved the official Fanum Live YouTube fallback when no qualifying Twitch
recording was available: `https://www.youtube.com/watch?v=qOen1OcaOAg`.
The local input is 5913.797370 seconds, 854x480, with gameplay and webcam visible
in inspected source frames. Full continuity was not independently certified.

Input SHA-256:
`f9f4d6fb069f165acaf2bf37302af79e87c47706c9aa82894a4e9e4576fd15ff`.

Colin uploaded that source to hosted Eklipse. Completed job 143536633 was actually
labeled Grand Theft Auto V. This was its full-recording highlight workflow;
the separate branded GTA6 single-clip reframer was not substituted for it.
Seventeen original horizontal suggestions were inventoried. Premium export
restrictions were preserved; no provider video assets were downloaded.

Actual Clips Kitty MCP jobs used independent data directories, the same source,
the same 1,473 cached real ASR segments and existing local model. The app arms
shared a ceiling of 50 clips and horizontal comparison rendering without captions
or an end card. The ordinary Gaming arm reached its ceiling, so count alone
cannot be treated as recall or a fair quality ranking. A matched host 0.4.1
control reproduced its original seven outputs byte for byte.

## Recorded measurements

| Arm | Clips | Median selected duration | Meaning |
|---|---:|---:|---|
| Hosted Eklipse GTA V | 17 | 77s |Provider-reported clip durations 49-166s; no exported-media alignment claim.|
| Clips Kitty ordinary Gaming | 50 | 22.95s |Configured count ceiling was reached.|
| GTA 0.4.1 | 7 | 19.84s |Frozen baseline; matched-host control reproduced the same outputs.|
| GTA 0.5.2 at `6ab55bd` | 28 | 14.08s |Selected durations 10-22.96s; approximately 8.9 minutes for the actual app run.|

All 57 original app baseline outputs and all 28 candidate outputs contained audio
and fully decoded. Rendered media includes the host's approximately 0.4 second
tail padding and frame quantization; selected source durations above exclude
that padding. The provider's native duration statistics are a different
measurement and are not presented as aligned source ranges.

Optional dialogue review fully validated 14 of 53 windows, with 7 additional partial
windows. Those are review-coverage counts, not semantic recall. The candidate's
valid partial proposals are retained without caching a partially invalid result
as a fully validated window.

Colin reviewed the private jail, street-question and impound timing examples
and explicitly chose to keep the shorter cuts. That approval does not establish
precision, title accuracy or watchability for every output. Longer output
remains configurable.

## Gaming facecam correction

The prepared desktop profile initially copied the horizontal timing-comparison
outputs, which had no Gaming render options. Colin clarified that he uses
**Draw it**. The existing host renderer then re-rendered all 28 source intervals
as 1080x1920 Gaming splits with a manual source facecam box. Actual picker,
preview, gallery and MCP export checks passed. Every original interval, title
and duration was preserved; all 28 new files contained audio and fully decoded.
The original comparison outputs remain backed up. This configuration correction
did not change detector code, rankings, cut boundaries or the matched baseline.

## Incomplete work

No pre-output event annotations, untouched holdout, blind rubric, provider-media
cross-correlation, semantic precision/recall or general quality superiority is
claimed. Eklipse export entitlements prevent an exported-media comparison on
this account. GTA VI gameplay was not tested. Further tuning/holdout work was
deferred under Colin's fast-submission direction; these unrun checks are not
passing results.

Implementation used the behavior-only specification and original fictional
regressions in an explicitly approved separate context. This aggregate report
was written afterward and supplied no competitor internals or raw material to
that implementation context. See [CONTEXT_TIMING_0_5.md](CONTEXT_TIMING_0_5.md)
for behavior and [HACKATHON_TEST_LOG.md](HACKATHON_TEST_LOG.md) for scope.
