# Independent synthetic quality regression report

Evaluation date: 2026-10-25. This report covers original transcript/signal metadata and unit/SDK fixtures. It does **not** establish real GTA footage quality, GTA VI detection accuracy, console capture support, audience performance, or release readiness. No authorized real footage or baseline/updated gameplay exports were available to this implementation exercise. Real video benchmarking remains pending.

## Independent implementation boundary

Implementation input was the clean functional specification, the user's existing plugin source/tests/evaluation, and the authorized SDK environment. No competitor source, pages, assets, dirty-room research, external speech, or downloaded footage was used. The new code and fictional fixtures are original MIT-licensed work. This describes the workflow; it is not a legal guarantee.

Changes are confined to detector/taxonomy code, tests, evaluation fixtures/results/runner, and this report. Host integration, adapters, publishing, marketplace packaging, and licensing files were outside this implementation task. Existing public category identifiers remain compatible. The configured default minimum remains 12 seconds for compatibility with existing plugin/host settings; durations are configurable.

## Recorded baseline and comparison

Before detector/taxonomy edits, the existing suite passed **147 tests**. The same isolated Python environment with the real editable `clipskitty-sdk` 1.3.0 was used before and after. The final suite passes **165 tests**, including generated original-media SDK checks already present in the suite. One prior expectation that silently clamped an out-of-range transcript interval was intentionally changed to require rejection, consistent with the clean specification. Added checks include 300 reproducible generated combinations of source edges, action lengths, and duration limits.

The 30-case original adversarial corpus was frozen and executed before source changes. Its 10 public holdout cases were authored and visible to the implementer before changes. They are secondary regressions, **not a blind test or generalization evidence**. The same fixture SHA-256 appears in both saved outputs; each output also records the full plugin Python-source snapshot hash. Subsequent adapter or packaging edits can change the source hash without changing these detector results.

| Check on identical frozen inputs | Before | After |
|---|---:|---:|
| Development cases satisfying every case assertion | 6/20 | 20/20 |
| Public holdout cases satisfying every case assertion | 5/10 | 10/10 |
| Individual assertions satisfied | 87/116 | 116/116 |
| Expected candidate counts satisfied | 18/30 | 30/30 |
| Required setup/action/reaction intervals retained | 2/7 | 7/7 |

Case pass counts include metadata assertions as well as behavior. They must not be presented as event accuracy percentages. Source records and predictions are in `evaluation/results/quality-before.json` and `quality-after.json`; exact case definitions and provenance are in `evaluation/fixtures/quality_cases.json`.

The existing 16-case corpus was also run unchanged before and after, independently of the new corpus. Its authored energy-only comparison remains an original reference detector, **not the host's built-in finder**. The table compares the actual plugin before and after this change:

| Existing synthetic corpus metric | Before | After |
|---|---:|---:|
| True positives / false positives / false negatives | 9 / 0 / 1 | 9 / 0 / 1 |
| Annotated incidents retaining all evaluated components | 7/10 | 8/10 |
| Mean setup coverage among matched incidents | 86.71% | 93.06% |
| Mean action/payoff coverage among matched incidents | 100% | 100% |
| Mean reaction coverage among matched incidents | 100% | 100% |
| Duplicate predictions | 0 | 0 |

The completeness metric requires at least 80% coverage of each annotated setup/payoff/reaction component; it does not mean full visual action was independently verified. The single newly complete existing case is `failed_ramp_stunt`: retaining the complete nearby setup utterance improves coverage. The untranscribed annotated collision remains missed by design. Existing corpus outputs are `evaluation/results/regression-before.json` and `regression-after.json`. No thresholds or event annotations in that corpus were changed.

## Concrete behavior changes

- Reject historical, retold, dream, future-plan, explicitly retracted, and negated-object event mentions rather than letting generic motion or loudness turn them into observations. Historical/hypothetical framing persists across sentences and closely adjacent ASR segments; explicit current-time or contrast language can reset that context.
- Record `action_start` and `action_end` separately from clip boundaries. These are the source utterance intervals supporting the event, **not visually measured physical action timing**. An action that fits the configured maximum survives padding reduction intact. An action longer than the maximum carries explicit truncation/review warnings.
- Extend to a nearby complete setup utterance within the lead-in allowance and to the end of a related reaction utterance that begins within the aftermath allowance. A separate supported later action bounds the prior aftermath. A relevant reaction that cannot fit the requested duration gets a review warning.
- Preserve distinct supported actions even when their selected clips or evidence intervals overlap. Normalize identical nearby semantic descriptions into one incident; suppress attached reactions and pursuit-to-payoff duplicates with explicit reasons. Distinct action evidence is an exception to overlap-based suppression.
- Classify isolated laughter/humor commentary as a creator reaction, with the neutral title `Creator reaction`. Dialogue payoff remains eligible when actual dialogue/premise evidence is supplied, including quiet transcript-only examples.
- Expose factual generic titles, available input modalities, separate structural score components, warnings, and duplicate-suppression reasons on the `Highlight` record. Setup and related reaction contribute small explicit bonuses; a pursuit with no supported escalation/resolution is lower priority. Novelty is explicitly zero because it is not measured. Missing modalities contribute no inferred bonus.
- Reject source intervals that extend beyond known media duration rather than silently changing their meaning by clamping them. Finite/negative/inverted timestamp validation remains in the existing immutable evidence contract.

Scores remain ranking heuristics, not probabilities or predicted views. The detector can retain an overlong supported utterance as a bounded review candidate. The SDK adapter withholds its find range and records it as `review_only` in the schema-2 explanation report; trim suggestions also require the complete supporting utterance. Three adapter regressions bring the integrated release suite to 168 passing tests. No publishing or automatic posting behavior was added.

## Reproduction

From the plugin root, with the isolated SDK/test environment already installed:

```powershell
$python = 'D:\clips_research\gta-release\env\Scripts\python.exe'
$env:PYTHONPATH = 'src;.'
& $python -m pytest
& $python -m evaluation.quality --output evaluation/results/quality-after.json
```

The legacy fixture comparison is callable through `evaluation.run.evaluate_fixtures(load_cases())`; the saved before/after files contain each prediction and temporal matching result. The before files are historical snapshots and must not be regenerated using updated source. The new quality runner uses standard-library checks against actual detector outputs and does not substitute hand-entered predictions.

## Remaining limitations and pending evaluation

The detector still requires a recognized explicit transcript cue. It does not recognize objects, collisions, NPCs, or game state from pixels, does not reliably infer humor from unrestricted dialogue, and misses untranscribed incidents. Frame differences and volume only corroborate an existing semantic cue. English rule-based framing is conservative and can reject true events in ambiguous, historical, mixed, or unusual phrasing. There is no general discourse/coreference model, calibrated confidence, or measured novelty model.

Setup/reaction association is a bounded temporal and language heuristic. A complete nearby utterance may still be unrelated. Default padding can include quiet/unrelated material when stronger context is absent. A requested minimum duration that cannot fit before a distinct next action is reported as a review constraint; it is not silently satisfied by appending that next action. Reaction-only candidates intentionally remain eligible, and generic titles avoid inventing their cause. Deduplication can conservatively merge genuinely repeated identically described incidents within ten seconds; unusual paraphrases can escape semantic repetition matching.

Titles are deliberately generic; this work does not measure open-domain factual title accuracy beyond the authored fixtures. Available modalities mean input observations supplied to the detector, not successful object recognition. New fields are analysis metadata; they require host/report serialization and review UI support for users to see them. No rendered framing, audio clarity, caption placement, watchability, or entertainment rubric scores were assigned.

A completed real-footage benchmark still needs an authorized rights/provenance manifest; frozen media/transcript/model configuration and hashes; pre-annotated factual setup/action/reaction; identical baseline/updated clip limits and actual exported videos; recorded reviewer identity and reasons; and visual/audio/caption review. No public video should be downloaded for testing merely because it is accessible. Until those artifacts exist, real-footage, GTA VI, and entertainment-quality conclusions remain pending.
