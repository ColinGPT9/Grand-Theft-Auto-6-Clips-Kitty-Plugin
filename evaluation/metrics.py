"""Transparent temporal metrics over authored annotations, using only stdlib."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def overlap(a: Sequence[float], b: Sequence[float]) -> float:
    return max(0.0, min(a[1], b[1]) - max(a[0], b[0]))


def temporal_iou(a: Sequence[float], b: Sequence[float]) -> float:
    intersection = overlap(a, b)
    union = max(a[1], b[1]) - min(a[0], b[0])
    return intersection / union if union > 0 else 0.0


def coverage(clip: Sequence[float], component: Sequence[float]) -> float:
    length = component[1] - component[0]
    return overlap(clip, component) / length if length > 0 else 0.0


def evaluate_case(predictions: Sequence[Mapping[str, Any]], events: Sequence[Mapping[str, Any]],
                  *, min_iou: float = 0.25, min_payoff_coverage: float = 0.5,
                  completeness_threshold: float = 0.8) -> dict[str, Any]:
    """Match one clip to at most one event, with explicit temporal thresholds.

    A match needs IoU >= .25 with the full annotation and >= .5 coverage of
    its payoff. Highest IoU wins greedily; ties use input order. Labels and
    scores never influence matching, so the energy baseline is treated alike.
    This is a small regression metric, not a validated semantic quality model.
    """
    pairs = []
    for pi, prediction in enumerate(predictions):
        clip = (prediction["start"], prediction["end"])
        for ei, event in enumerate(events):
            iou = temporal_iou(clip, (event["start"], event["end"]))
            if iou >= min_iou and coverage(clip, event["payoff"]) >= min_payoff_coverage:
                pairs.append((iou, pi, ei))
    pairs.sort(key=lambda pair: (-pair[0], pair[1], pair[2]))
    matched_predictions, matched_events, matches = set(), set(), []
    for iou, pi, ei in pairs:
        if pi in matched_predictions or ei in matched_events:
            continue
        matched_predictions.add(pi)
        matched_events.add(ei)
        clip = (predictions[pi]["start"], predictions[pi]["end"])
        event = events[ei]
        parts = {name: coverage(clip, event[name]) for name in ("setup", "payoff", "reaction")
                 if event.get(name) is not None}
        matches.append({"prediction_index": pi, "event_id": event["id"], "event_index": ei,
                        "temporal_iou": round(iou, 6),
                        "component_coverage": {name: round(value, 6) for name, value in parts.items()},
                        "complete": all(value >= completeness_threshold for value in parts.values())})
    duplicate_pairs = 0
    for i, prediction in enumerate(predictions):
        for other in predictions[i + 1:]:
            a = (prediction["start"], prediction["end"])
            b = (other["start"], other["end"])
            shortest = min(a[1] - a[0], b[1] - b[0])
            if shortest > 0 and overlap(a, b) / shortest >= 0.5:
                duplicate_pairs += 1
    # Each extra clip plausibly matching an already claimed event is also
    # counted. It remains a false positive under the one-to-one matching.
    duplicate_predictions = sum(1 for pi in range(len(predictions))
                                if pi not in matched_predictions
                                and any(p == pi for _, p, _ in pairs))
    tp = len(matches)
    fp = len(predictions) - tp
    fn = len(events) - tp
    return {"true_positives": tp, "false_positives": fp, "false_negatives": fn,
            "predictions": len(predictions), "annotated_events": len(events),
            "precision": tp / len(predictions) if predictions else None,
            "recall": tp / len(events) if events else None,
            "matched_mean_temporal_iou": sum(m["temporal_iou"] for m in matches) / tp if tp else None,
            "complete_events": sum(m["complete"] for m in matches),
            "event_completeness_rate": sum(m["complete"] for m in matches) / len(events) if events else None,
            "duplicate_predictions": duplicate_predictions,
            "duplicate_rate": duplicate_predictions / len(predictions) if predictions else 0.0,
            "overlapping_prediction_pairs": duplicate_pairs,
            "matches": matches}


def aggregate(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Micro-average counts; undefined precision/recall are JSON null."""
    names = ("true_positives", "false_positives", "false_negatives", "predictions", "annotated_events",
             "complete_events", "duplicate_predictions", "overlapping_prediction_pairs")
    result = {name: sum(case["metrics"][name] for case in cases) for name in names}
    count = result["predictions"]
    event_count = result["annotated_events"]
    tp = result["true_positives"]
    result.update({"case_count": len(cases),
                   "precision": tp / count if count else None,
                   "recall": tp / event_count if event_count else None,
                   "event_completeness_rate": result["complete_events"] / event_count if event_count else None,
                   "duplicate_rate": result["duplicate_predictions"] / count if count else 0.0,
                   "matched_mean_temporal_iou":
                   sum(m["temporal_iou"] for case in cases for m in case["metrics"]["matches"]) / tp if tp else None})
    for name in ("setup", "payoff", "reaction"):
        values = [match["component_coverage"][name] for case in cases
                  for match in case["metrics"]["matches"] if name in match["component_coverage"]]
        result[f"matched_mean_{name}_coverage"] = sum(values) / len(values) if values else None
    return result
