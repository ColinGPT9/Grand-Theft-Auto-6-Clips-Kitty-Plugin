# Candidate 0.5.1: concise context and bounded dialogue review

This candidate implements the behavior-only context/timing handoff using the
existing plugin and SDK contract plus original fictional regressions. It makes
no competitor parity, real-footage quality, holdout or live-service claim.

Deterministic events and grounded dialogue are discovered together. Discovery
does not stop at the requested output count. Joint selection first favors
complete source utterances, ranks supported events ahead of neutral nomination
review candidates, suppresses overlapping alternatives for the same source
incident, and only then applies the clip limit. Separate nearby incidents retain
their own causal intervals. A complete explicit action of at most 40 seconds can
replace an overlapping conversation longer than 45 seconds; its action title is
retained rather than the conversation's question or accusation title.

Dialogue source IDs retain the causal setup through the complete response.
Generic padding does not enlarge a source-selected exchange. An explicit
grammatical continuation carries a divided response into the next supplied ASR
segment. A gap of at least 12 seconds without source speech, or a sustained
low-information transcript interval between exchanges, rejects a merged model
proposal. Brief gaps and visually quiet source speech remain eligible. These
are conservative heuristics, not topic recognition or word-level alignment.
The plugin cannot cut inside an ASR segment without a finer host transcript.

The preferred length is 15–40 seconds, without a plugin minimum or quota.
Host minimum/maximum duration constraints still apply. Source-grounded long
exchanges receive a duration ranking penalty and review warnings beyond 45
seconds. Beyond 60 seconds, at least five close source turns and explicit
setup/payoff/response timing are required. Existing deterministic event padding
remains an allowance when the source lacks a more precise contextual boundary.
Known setup questions and meaningful reactions define tighter boundaries;
identified recovery and unrelated following actions stop the tail.

Dialogue review uses 32 transcript segments per window with stride 28. Mapped
nomination windows come first, followed by measured audio/motion activity and
coverage spread across remaining portions. The scheduler indexes signal times
rather than rescanning all media for every comparison. Source IDs, window
membership, category, causal ordering, exact payoff quotation, confidence,
routine/hypothetical exclusions and source duration are validated before a
proposal is admitted. Invalid responses and transient model failures cannot
create source events.

Each optional request receives at most 15 seconds. The configurable
`dialogue_review_minutes` setting defaults to 20 and accepts 0–20 minutes;
corroboration shares this elapsed-time allowance. A zero budget retains
deterministic findings. The manifest's 30 minute invocation limit, with a 30
second result-writing reserve, also bounds optional work. When the host provides
the finite positive `CLIPS_KITTY_PLUGIN_DEADLINE_MONOTONIC` capability, review is
also clamped to that actual runner deadline with a five second result-writing
reserve. Older hosts without it retain the manifest fallback; their shorter
timeout overrides cannot be discovered through SDK API v1 alone.

Whole-call timeout enforcement uses the companion SDK fix that shares the
deadline across model capability lookup and generation. Legacy SDK helpers may
spend their own capability-lookup timeout before generation; this plugin rejects
late responses but cannot cancel an older helper's blocking internal request.

Persistent cache storage is granted only through the host-owned absolute
`CLIPS_KITTY_PLUGIN_CACHE_DIR` capability. The plugin writes its `dialogue-v2`
subdirectory there; it never creates cache storage in the installed source
tree. Older hosts without this capability continue discovery with caching
disabled and report that limitation. Cache keys fingerprint source/transcript
identity, effective local model, settings, configuration and prompt/schema
version. Only fully validated successful outcomes, including valid empty
arrays, are persisted. Disk outcomes are validated again on read; invalid
entries cause fresh requests. Timeouts, late answers, malformed JSON and
unsupported proposals are retried on a later invocation rather than cached as
empty discoveries. Chat identities are never copied into cache or reports.

Only the SDK's permitted, host-mapped Twitch aggregate nomination context is
read. A neutral `viewer_nominated` candidate requires at least two mapped
nominations and verified audio-spike or motion evidence in the same derived
10 second source bucket. A scene/brightness change alone does not qualify.
Source-supported categories rank ahead of nomination-only candidates; mapped
interest cannot identify police, damage, factions, battles or any gameplay
event. Disabled, unmapped, single or unrelated nominations cannot create this
category. Nomination commands and aggregate counts are retained, not chat/user
identities. The host may legitimately return unavailable nomination context.

Version 0.5.1 corrects the initial constant nomination review priority of 43.
Code inspection established that the host's find job does not supply its quality
threshold in `limits.min_score`, the runner preserves the plugin's score, and
Gaming applies its configured threshold after optional image review. A constant
43 therefore made every neutral bucket ineligible at a host threshold of 55
when image review left the score unchanged.

Neutral review priority now combines an admissible mapped bucket with verified
activity (0.25), saturating nomination concentration (up to 0.20), the strongest
verified audio/motion measurement (up to 0.14), and independent audio/motion
agreement (up to 0.10). Repeated measurements of one modality cannot inflate it.
The resulting heuristic is independent of the host threshold and remains
bounded by 0.69; evidence confidence remains conservative at 0.35 and no event
identity is inferred. Weak buckets may fail either the plugin or host threshold;
there is no threshold-dependent floor, guarantee of Library admission or quota.
Explicit source-supported categories retain priority for the plugin's limited
output slots. Gaming still owns final image review, filtering and sorting.

An original fictional integration check used the actual host
`runner.to_candidates` and `gaming.review` functions with image review disabled
and minimum score 55. Two nominations with one strong modality scored 47 and
were filtered; eight with one strong modality scored 58 and passed; two with
both strong audio and motion scored 57 and passed; eight with weak motion
scored 47 and were filtered. No media or model service was read by this check.

The existing schema-2 explanation report gains a `dialogue_review` object and
per-highlight `required_context`; existing fields remain available. Review
metadata includes successful/attempted/failed windows, source-segment coverage,
cache hits/misses, elapsed seconds, configured budget and budget exhaustion.
Coverage describes validated windows, not recognition accuracy or exhaustive
semantic event discovery. Review notes also reach the SDK's finish summary.
Per-plugin model selection continues through the SDK; no model name, remote
service, rendering, Gaming framing, YOLO, captions or audio processing is added.

Validation uses original fictional tests and generated synthetic media. The
frozen tuning input and untouched holdout must be evaluated separately by the
coordinator after this independent implementation; they were not read here.

Initial 0.5.0 verification on Windows with Python 3.11 and the companion SDK timeout
fix (`ced0d69`): `python -m pytest -o addopts= --disable-warnings` passed all
319 tests, including original synthetic FFmpeg/SDK subprocess cases, in 4.39
seconds. `python -m ruff check .` and `git diff --check` passed. SDK validation
accepted version 0.5.0 with three existing development-script import warnings
in `evaluation/quality.py`, `evaluation/run.py` and `scripts/evaluate.py`; none
concerns the runtime entry point or new modules. These checks do not establish
quality on the coordinator's frozen tuning source or untouched holdout.

The 0.5.1 integration correction passes 337 tests (18 additional original
fictional regressions) in 4.21 seconds. Ruff and whitespace checks pass. SDK
validation accepts 0.5.1 with the same three development-script warnings.
