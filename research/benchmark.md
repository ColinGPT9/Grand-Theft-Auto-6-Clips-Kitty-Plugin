# Footage benchmark and evaluation protocol

Status on 2026-10-24: real-footage benchmark **not run**. No rights-cleared
GTA gameplay, baseline video exports, public-example visual inspection,
or GTA VI gameplay was available to this task. Synthetic detector and SDK
tests are technical evidence only. No improvement in real watchability or
GTA VI detection accuracy is claimed.

## Comparable cases

Use the same authorized source, cached host transcript/analysis, export
layout, clip limits, and model configuration for baseline and plugin runs.
Record source and export hashes and an explicit source-to-VOD time mapping.
Two reviewers should score blind where practical. Keep failures and missing
dimensions, including clips that look impressive but miss the actual event.

| Case | Required source observation | Review the selected clip for |
| --- | --- | --- |
| Police pursuit | Pursuit setup, escalation, observed resolution | Enough context to understand pursuit; actual payoff and reaction retained |
| Vehicle crash | Approach, visible impact, immediate aftermath | Starts before impact; includes aftermath; no unsupported vehicle or outcome claim |
| Stunt | Attempt and visible landing or failure | Preserves trajectory/action; outcome visible; excess approach removed |
| NPC chaos | Actual unusual interaction | Explains the situation without inventing NPC intent; keeps useful reaction |
| Funny dialogue | Audible setup and punchline | Sentence boundaries and punchline intact; factual title and readable captions |
| Roleplay | Source explicitly supports roleplay | Turn-taking, negotiation or betrayal context intact; not inferred from all conversation |
| Unexpected failure | Visible or audible attempted action and failure | Attempt/failure relationship clear; reaction retained when relevant |
| Streamer reaction | Observed reaction with contextual event | Reaction tied to what happened; loudness alone is insufficient |

## Anchored 1–5 rubric

Score each dimension separately. Use `N/A` with a reason when it cannot be
judged; never convert missing evidence to a positive score.

| Dimension | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Event relevance | Wrong event or unsupported claim | Correct general event, weak context | Clear event with traceable supporting evidence |
| Opening hook | Confusing/irrelevant opening | Understandable after a delay | Immediately legible while preserving needed setup |
| Setup and payoff | Main setup or outcome absent | Both partly visible | Complete causal sequence without excess footage |
| Reaction inclusion | Relevant reaction lost | Reaction partly retained | Useful reaction complete; no needless padding |
| Visual framing | Main action cropped out | Action mostly visible | Main action consistently visible in chosen layout |
| Audio clarity | Important speech/action inaudible | Understandable with effort | Clear speech/action and balanced levels |
| Duration | Abruptly cut or mostly irrelevant | Usable with visible trimming opportunities | Appropriate start/end and pacing for this event |
| Captions | Incorrect/unreadable or obscure action | Mostly accurate/readable | Accurate, well timed, legible, and unobtrusive |
| Duplicate prevention | Same moment repeatedly selected | Some redundant overlap | Distinct moments with no redundant event copy |
| Overall watchability | Cannot understand why selected | Understandable but needs editing | Coherent, useful clip suitable for creator review |

Scores 2 and 4 represent intermediate behavior. Do not average away a
missing payoff or misleading title. Review event recall and false positives
against a human timestamped source annotation separately from clip quality.
Engagement counts are contextual observations, never evidence that an edit
caused popularity. Publication age, audience, creator reach, platform, and
promotion confound comparisons.

## Reproducible improvement log

For each iteration create a row with case ID, authorized source reference,
license/permission, source SHA-256, host commit, plugin commit, settings,
model name/version if used, baseline ranges/export SHA-256, plugin ranges/
export SHA-256, reviewer scores, concrete failure, change, and rerun result.
Keep exports outside this repository unless rights permit redistribution.

1. Record human ground truth before tuning.
2. Run host baseline and save outputs.
3. Run plugin using the same cached inputs and save outputs.
4. Review both against this rubric and timestamped ground truth.
5. Change one documented rule for an observed failure.
6. Rerun the same cases plus held-out cases; report regressions as well as gains.

The initial plan above preceded the real-footage evaluation. Current SDK and
app cases, source hashes, inspected exports, misses and limitations are in
[Real footage review](../docs/REAL_FOOTAGE_REVIEW.md) and its linked JSON results.
These are development cases, not a blind quality or engagement measurement.

The requested Eklipse baseline remains unavailable: the owner has no hosted
account/results access. Public GTA and GTA 6 tool pages provide workflow
requirements; an already selected clip's crop/caption export cannot measure
the hosted VOD finder's recall or ranking. No Eklipse result is fabricated.
