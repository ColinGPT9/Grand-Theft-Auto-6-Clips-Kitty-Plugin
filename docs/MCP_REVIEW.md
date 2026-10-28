# Actual Clips Kitty MCP review — 0.4.1

Recorded 2026-10-26. This is a small, non-blind development review, not an
accuracy benchmark or evidence of superiority over another service. Public media
and full transcripts remain outside the repository. The attributed, private review
video is 167 seconds and contains actual app exports. Streamer comparisons use
the creator's own Twitch VOD or verified creator uploads; the XQC fan edit and
viewer clip are excluded. See [derived measurements](../evaluation/results/mcp-review.json).

## Method

The running desktop app used an isolated configuration and history. A real stdio
MCP client called `queue_local_file`, `job_status`, `list_clips` and `export_clip`.
The original evaluation comprises 26 completed jobs with no failures in that set;
the later single-VOD follow-up used jobs 32 and 33. Earlier prototypes
are not release results. The final plugin ran in jobs 20–24 and 26; job 25 is
the additional regular Gaming comparison. A successful job does not imply that
it found a good highlight.

Each paired input was a byte-identical local copy with the same cached actual
Whisper transcript. Settings were minimum score 55, at most two clips, automatic
Gaming layout detection and the existing local `gemma4:e4b` model. Captions were
enabled except for both arms of the already-captioned Spanish vertical source.
No generic Gaming finder runs alongside GTA. Both arms use the host's Gaming
OpenCV/audio review, YOLO pose webcam detection, framing and FFmpeg renderer.
Saved Gaming layout boxes remain supported by host regression tests; this run
used automatic detection in the original comparison jobs.

The earlier XQC YouTube source was a fan edit that credits multiple streamers;
it is not used in the final review. The replacement is xQc's own [Twitch VOD
2880410519](https://www.twitch.tv/videos/2880410519), a five-minute excerpt from
03:43:00 to 03:48:00. It is one creator POV with xQc's webcam over his gameplay.
Jobs 32 (Gaming) and 33 (GTA 0.4.1) used the same file, byte-identical SHA-256,
cached Whisper transcript, local `gemma4:e4b` model, score threshold and the
owner's manually selected Gaming picker layout (`half`, webcam box selected by
the user). Both exports show xQc in the upper half and his gameplay below. No
automatic camera-detection change is claimed.

The local model failed the host's image-capability probe. Semantic image review
was therefore skipped; OpenCV measurements and YOLO framing did run. We did not
bypass the probe. Optional sound-model support was unavailable. Dialogue grounding
checks source words and boundaries, not visual truth or comedic quality.

## Actual selections

Times below are seconds in the downloaded source excerpt, before rendering.
Scores are internal heuristics, not calibrated confidence or predicted views.

| Source | Regular Gaming | GTA 0.4.1 | Human review |
| --- | --- | --- | --- |
| [DarkViperAU stream](https://www.youtube.com/watch?v=op3LIcOB4GU), excerpt 300–480s | 11.50–26.50; 138.22–162.32 | No clips | Routine donor/progress chatter. The old GTA 0.3.0 selection 134.54–172.32 was a false positive; removed. |
| [DarkViperAU spinout](https://www.youtube.com/watch?v=Uqub0AtkX5s) | 3.00–18.00 | 0.00–13.98 | GTA retains the earlier action; Gaming retains more of the later software-crash joke. |
| Buddha Twitch clip, exploratory only | 14.20-33.97 | 0.00-36.17 | Viewer-created clip; excluded from the final review video. |
| [xQc's official NoPixel V Twitch VOD](https://www.twitch.tv/videos/2880410519), excerpt 03:43:00-03:48:00 | 100.30-124.50; 125.00-143.90 | 0.00-20.80; 239.34-263.66 | Same picker layout. Gaming found police dialogue; GTA missed it and returned two generic `Creator reaction` clips for human review. |
| Vista Gamer vertical, discovery only | 1.50-16.92; 31.86-48.08 | 0.00-15.10; 29.86-48.58 | Origin stream was not verified; excluded from the final source review. |
| Eklipse-watermarked third-party upload, exploratory only | No clips | No clips | Already-edited, non-creator source; excluded from the final video and not detector ground truth. |

The review presents the same single-POV VOD with matching camera/game framing,
source-aligned times and explicit no-selection panels. Gaming selected a later
police-dialogue exchange that GTA did not select. GTA's two generic reaction
selections are shown for human review. The earlier Crulfy test also missed a
quiet background police-car fall; transcript-first detection has not solved
silent actions.

## Improvements driven by failures

Routine numeric wave counts no longer qualify as mission milestones. The optional
dialogue fallback runs only when explicit rules found no candidate and the source
has GTA/RP context. It uses existing local inference, opaque source-segment IDs,
normalized exact-word setup/payoff grounding, duration/category checks and exclusions
for routine thanks, hypothetical scenes and retellings. Invalid or unavailable
model output fails closed. At most three bounded transcript windows are reviewed;
this is not exhaustive coverage of a long stream.

An unreleased 0.4 prototype confused segment IDs with timestamps and selected an
unrelated zombie hypothetical. Actual MCP testing exposed these failures before
release. Source-ID and context regressions now cover them. Dialogue remains a
model judgement for human review, and titles still need editorial review.

## Creator discovery and Eklipse comparison limits

Searches included xQc, Buddha, Lord_Kebun, Zerkaa, Esfand and Fanum. Primary service
metadata captured 154,610 views for [Buddha/xQc](https://www.youtube.com/watch?v=j96a-j9BCGU), 94,618 for
[Buddha's driving test](https://www.youtube.com/watch?v=D90Lp0sPmFo), about 521K
for the DarkViperAU short and 10.52M for the Vista Gamer vertical. Counts change.
These are examples of popular footage, not evidence that any detector caused
engagement. The additional Buddha references were inspected, not queued as
additional pipeline cases. A 1.79M-view Fanum full stream was discovery only.

Public TikTok discovery was blocked and Instagram searches did not yield a
verifiable direct GTA RP sample. No direct TikTok/Reels performance comparison
is claimed, and no authenticated account or challenge bypass was used.

The [Eklipse GTA page](https://eklipse.gg/use-case/gta/) supplies public examples.
The verified YouTube reference visibly carries an Eklipse watermark; that proves
an Eklipse export, not which detector selected its interval. Its full raw VOD is
unknown and no hosted Eklipse account was available. The
[GTA 6 tool page](https://eklipse.gg/tool/gta-6-clips-tool/) describes browser
editing/export and does not establish a publicly testable GTA VI detector. We
did not access model weights, private code or hosted scores. This comparison
cannot measure same-input Eklipse recall or establish that GTA is better.

## Validation and boundaries

251 plugin tests pass, including real SDK subprocess and FFmpeg/media tests;
Ruff and SDK validation pass (three development import-path warnings). The host
has tests for shared vision/layout reuse, source provenance, per-plugin local
models, MCP options/timestamps and Gaming-only scope. Twitch and Discord remain
host responsibilities. No Store package, social publication, native Twitch clip,
Discord message or hackathon submission was performed. GTA VI gameplay and live
Twitch integration were not tested in this review.
