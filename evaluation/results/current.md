# Synthetic regression evaluation

Run: 2026-10-24T19:26:21.578954+00:00

These results cover original synthetic signal/transcript fixtures, not real gameplay or audience performance.
The energy-only baseline is original reference code, not Clips Kitty's built-in finder.

| Detector | TP | FP | FN | Precision | Recall | Complete events | Duplicate rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| energy_only_baseline | 6 | 5 | 4 | 54.5% | 60.0% | 30.0% | 0.0% |
| gta_plugin | 9 | 0 | 1 | 100.0% | 90.0% | 70.0% | 0.0% |

Manual visual framing, audio, captions, and watchability review: **not performed**.

See the JSON file for per-case predictions, match thresholds, provenance, and temporal coverage.
