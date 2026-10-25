# Evaluation and review

Run the real deterministic detector and the energy-only reference on the
same fixed inputs from the repository root:

```sh
python scripts/evaluate.py
python scripts/evaluate.py --split holdout --output /tmp/gta-holdout.json
python -m pytest -q tests/test_evaluation.py
```

The commands require the supported `clipskitty_sdk` package. The first
command writes fresh [JSON](../evaluation/results/current.json) and a
[readable report](../evaluation/results/current.md), including run time,
fixture and source SHA-256 hashes, predictions, match details, and counts.
The metrics calculation itself is deterministic; run time is metadata.

The [fixtures](../evaluation/fixtures/cases.json) are original fictional
transcripts, numeric loudness pulses, scene-change times, and annotations.
They contain no copied streamer speech, GTA footage, or Twitch data. Their
license is MIT. `development` and `holdout` select public partitions. Both
are visible to the authors; the second partition is a secondary regression
check, not a blind benchmark or a claim of generalization. No models are
required or supplied to these cases.

Cases cover a chase ending in a crash, a failed stunt, an NPC incident,
dialogue with an explicit humor cue, roleplay disabled and enabled, loud
noise without an event, unrelated speech, missing media, missing transcript,
and missing all evidence. The untranscribed collision deliberately counts
as a missed event: generic loudness and scene changes cannot identify it.
The long-setup case deliberately tests context that extends beyond fixed
padding. Read these failures alongside the aggregate numbers.

`energy_only_baseline` is original reference code in this repository using
the SDK's public `signals.spikes` helper. It selects relative loudness peaks
with eight seconds of lead and ten seconds of tail. It is not the Clips
Kitty app's built-in finder, a historical version of this plugin, or a human
editor. Its purpose is to show the false positives produced by treating
loudness as event relevance. A higher fixture score does not establish
better human quality, actual event recognition, or viral performance.

For each candidate, temporal intersection-over-union (IoU) is calculated
against the annotated event interval, which contains setup, payoff, and
reaction. A match needs IoU at least 0.25 and coverage of at least half the
annotated payoff. Matching greedily takes the highest IoU first and assigns
each prediction and event at most once; ties follow input order. Labels and
plugin scores do not influence matching. A matched prediction is a true
positive; an unmatched prediction is a false positive; an unmatched event is
a false negative. Precision and recall are micro-averaged over cases.
Undefined precision or recall is `null`, rather than a fabricated perfect
score. This temporal proxy measures agreement with authored event relevance,
not independent semantic understanding of video.

The report separately includes setup, payoff, and reaction coverage on
matched clips. An event is complete only if its matched clip covers at least
80% of every annotated component. Event completeness divides complete events
by all annotated events, so missed events also reduce it. Mean IoU and mean
component coverage use matched clips only. Duplicate rate is the number of
additional candidates eligible to match an already matched event divided by
all candidates. The count of prediction pairs overlapping at least half the
shorter clip is also reported; adjacent distinct events can overlap, so that
pair count is a diagnostic, not automatically an error.

No visual framing, audio, caption, or watchability scores have been assigned.
Those require an authorized source clip, its actual export, and a reviewer
who watches and listens to both. A transcript, a loudness value, or a
synthetic test pattern cannot substitute for that review.

Use this anchored 1–5 rubric for a future manual review. Record `not reviewed`
when a dimension cannot be inspected; do not infer scores from detection
confidence. A reviewer should note source, clip boundaries, export layout,
reviewer, date, and a short concrete reason for each score.

| Score | Visual framing | Audio | Captions | Watchability |
|---:|---|---|---|---|
| 1 | Main action or essential HUD is cropped out | Speech or event audio is unusable | Missing or mostly incorrect required words | Event or context cannot be understood |
| 2 | Frequent crop mistakes or blocked action | Frequent masking, clipping, or abrupt cuts | Frequent errors, obstruction, or bad timing | Major setup or payoff is lost; confusing pacing |
| 3 | Main action is visible with some distracting framing | Understandable with occasional level or cut problems | Mostly correct and readable with some timing errors | Event makes sense but has avoidable dead time or a weak ending |
| 4 | Action and necessary context remain clear | Clear, balanced audio and clean cuts | Accurate, legible, well-timed captions | Setup, payoff, and reaction form a clear sequence |
| 5 | Framing consistently supports the action across the chosen layout | Consistently clear audio preserves useful speech and game cues | Accurate accessible captions preserve speaker meaning and avoid action | Complete sequence with deliberate pacing and no obvious unnecessary span |

To create media for an SDK job integration check, use an output path outside
the plugin so generated media is never bundled with an installation:

```sh
python scripts/generate_demo.py /tmp/gta-demo.mp4
```

This uses the explicitly named `/usr/bin/ffmpeg` executable, or an absolute
path supplied by `--ffmpeg`. It generates 48 seconds of original geometric
frames and tones, with scene changes at 20 and 22 seconds, a loud tone at
20–22 seconds, an invented transcript JSON, a caption VTT, and provenance
annotations. The supplied transcript is test input; the tones contain no
speech. The media is not GTA footage and cannot validate real-game visual
recognition or any of the manual rubric dimensions.
