# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ColinGPT9
"""Evidence records and conservative, explainable highlight scores.

The score is a ranking heuristic, not a calibrated probability of an event.
Repeated measurements of one type cannot inflate it. Identified event categories
require source transcript cues; a separate neutral nomination review score can
rank mapped buckets without identifying game objects or gameplay events.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable
from dataclasses import dataclass

MEDIA_KINDS = frozenset({"video_motion", "video_scene_change", "video_color_change", "audio_spike"})
EVIDENCE_KINDS = MEDIA_KINDS | {"transcript", "chat", "model"}


def _number(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(f"{name} must be a finite number") from None
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return value


@dataclass(frozen=True)
class Evidence:
    """One timestamped observation, using seconds in the source video.

    ``verified`` means the adapter actually measured a media signal (or
    validated a grounded optional model response). It does not mean that a
    video difference recognized a vehicle, NPC, weapon, or other object.
    Transcript and chat text remain source statements, not verified facts.
    """

    start: float
    end: float
    kind: str
    confidence: float = 1.0
    text: str = ""
    tags: tuple[str, ...] = ()
    source: str = ""
    verified: bool = False

    def __post_init__(self) -> None:
        start = _number(self.start, "start")
        end = _number(self.end, "end")
        confidence = _number(self.confidence, "confidence")
        if start < 0 or end < start:
            raise ValueError("evidence timestamps require 0 <= start <= end")
        if not 0 <= confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.kind not in EVIDENCE_KINDS:
            raise ValueError(f"unsupported evidence kind: {self.kind!r}")
        if not isinstance(self.text, str) or not isinstance(self.source, str):
            raise ValueError("evidence text and source must be strings")
        if isinstance(self.tags, str):
            raise ValueError("tags must be a sequence of strings")
        try:
            tags = tuple(self.tags)
        except TypeError:
            raise ValueError("tags must be a sequence of strings") from None
        if any(not isinstance(tag, str) for tag in tags):
            raise ValueError("tags must be a sequence of strings")
        if not isinstance(self.verified, bool):
            raise ValueError("verified must be a boolean")
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "tags", tags)


@dataclass(frozen=True)
class ScoreBreakdown:
    """A bounded ranking score, evidence confidence, and auditable weights."""

    score: float
    confidence: float
    components: tuple[tuple[str, float], ...] = ()


_NOMINATION = re.compile(r"\b(?:clip (?:that|this|it)|clip it|clipworthy|clip worthy|save (?:that|this)|highlight (?:that|this))\b")
_NO_NOMINATION = re.compile(r"\b(?:don'?t|do not|never|not|shouldn'?t|wouldn'?t|no need to)\b")


def is_nomination(text: str) -> bool:
    """Recognize an explicit chat nomination without treating chat as proof."""
    normalized = text.casefold().replace("’", "'")
    for clause in re.split(r"[.!?;\n]|\bbut\b", normalized):
        match = _NOMINATION.search(clause)
        if match and not _NO_NOMINATION.search(clause[:match.end()]):
            return True
    return False


_WEIGHTS = (
    ("video_motion", 0.10),
    ("video_scene_change", 0.06),
    ("video_color_change", 0.025),
    ("audio_spike", 0.075),
    ("chat", 0.07),
    ("model", 0.045),
)


def score_evidence(evidence: Iterable[Evidence], *, semantic_confidence: float = 0.0) -> ScoreBreakdown:
    """Score a semantically anchored event and its nearby supporting signals.

    The caller supplies confidence * phrase specificity for the actual event
    cue. Zero or missing semantic evidence always returns zero, regardless of
    how many loud sounds, frame changes, chat messages, or model rows exist.
    The strongest row of each kind contributes once. Model corroboration
    must already be category grounded by the detector and ``verified``.
    """
    semantic = _number(semantic_confidence, "semantic_confidence")
    if not 0 <= semantic <= 1:
        raise ValueError("semantic_confidence must be between 0 and 1")
    rows = tuple(evidence)
    if not rows or semantic == 0:
        return ScoreBreakdown(0.0, 0.0)
    # A supplied semantic number without a textual event source is not proof.
    if not any(row.kind == "transcript" and row.confidence > 0 for row in rows):
        return ScoreBreakdown(0.0, 0.0)
    strongest: dict[str, float] = {}
    for row in rows:
        if row.kind in MEDIA_KINDS and not row.verified:
            continue
        if row.kind == "model" and not row.verified:
            continue
        if row.kind == "chat" and not is_nomination(row.text):
            continue
        strongest[row.kind] = max(strongest.get(row.kind, 0.0), row.confidence)
    components = [("semantic", 0.62 * semantic)]
    support = 0.0
    available_weight = sum(weight for _, weight in _WEIGHTS)
    for kind, weight in _WEIGHTS:
        contribution = weight * strongest.get(kind, 0.0)
        if contribution:
            components.append((kind, contribution))
            support += contribution
    score = min(1.0, sum(value for _, value in components))
    confidence = min(1.0, 0.82 * semantic + 0.18 * support / available_weight)
    return ScoreBreakdown(round(score, 4), round(confidence, 4), tuple((name, round(value, 4)) for name, value in components))


def score_nomination_review(count: int, activity: Iterable[Evidence]) -> ScoreBreakdown:
    """Rank a mapped review bucket; this is not confidence in a GTA event.

    The caller supplies a host-mapped aggregate count from the same source
    bucket. Concentrated nominations saturate, repeated measurements count once,
    and agreement between audio and motion adds more support than either alone.
    No host quality threshold enters this calculation.
    """
    if isinstance(count, bool) or not isinstance(count, int) or count < 2:
        return ScoreBreakdown(0.0, 0.0)
    strongest = {"audio_spike": 0.0, "video_motion": 0.0}
    for row in activity:
        if row.verified and row.kind in strongest:
            strongest[row.kind] = max(strongest[row.kind], row.confidence)
    primary, secondary = max(strongest.values()), min(strongest.values())
    if primary <= 0:
        return ScoreBreakdown(0.0, 0.0)
    components = (("mapped_bucket_with_activity", 0.25),
                  ("nomination_concentration", 0.20 * (1 - math.exp(-(count-1)/2))),
                  ("verified_activity_strength", 0.14 * primary),
                  ("audio_motion_agreement", 0.10 * secondary))
    # Preserve conservative evidence confidence: stronger review priority does
    # not establish an event's identity or factual gameplay description.
    return ScoreBreakdown(round(sum(value for _, value in components), 4), 0.35,
                          tuple((name, round(value, 4)) for name, value in components))


__all__ = ["EVIDENCE_KINDS", "MEDIA_KINDS", "Evidence", "ScoreBreakdown", "is_nomination", "score_evidence", "score_nomination_review"]
