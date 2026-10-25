# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ColinGPT9
"""Find bounded moments from explicit event cues and measured corroboration.

This module deliberately has no media decoder, network client, or game-object
recognizer. Adapters supply timestamped observations. Explanations describe
those observations and quote the transcript instead of inventing a scene.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

from .scoring import MEDIA_KINDS, Evidence, is_nomination, score_evidence
from .taxonomy import CATEGORIES, Cue, classify_text


@dataclass(frozen=True)
class Config:
    min_score: float = 0.42
    min_confidence: float = 0.35
    min_duration: float = 12.0
    max_duration: float = 60.0
    lead_in: float = 8.0
    payoff: float = 10.0
    merge_gap: float = 5.0
    max_highlights: int = 20
    roleplay_enabled: bool = False
    enabled_categories: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("min_score", "min_confidence", "min_duration", "max_duration", "lead_in", "payoff", "merge_gap"):
            value = getattr(self, name)
            if isinstance(value, bool):
                raise ValueError(f"{name} must be a finite number")
            try:
                value = float(value)
            except (TypeError, ValueError, OverflowError):
                raise ValueError(f"{name} must be a finite number") from None
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be a finite nonnegative number")
            object.__setattr__(self, name, value)
        if self.min_score > 1 or self.min_confidence > 1:
            raise ValueError("score and confidence thresholds must be between 0 and 1")
        if self.max_duration <= 0 or self.min_duration > self.max_duration:
            raise ValueError("durations require 0 <= min_duration <= max_duration and max_duration > 0")
        if isinstance(self.max_highlights, bool) or not isinstance(self.max_highlights, int) or self.max_highlights < 0:
            raise ValueError("max_highlights must be a nonnegative integer")
        if not isinstance(self.roleplay_enabled, bool):
            raise ValueError("roleplay_enabled must be a boolean")
        if isinstance(self.enabled_categories, str):
            raise ValueError("enabled_categories must be a sequence of category names")
        try:
            enabled = tuple(self.enabled_categories)
        except TypeError:
            raise ValueError("enabled_categories must be a sequence of category names") from None
        if any(category not in CATEGORIES for category in enabled):
            raise ValueError("enabled_categories contains an unknown category")
        object.__setattr__(self, "enabled_categories", enabled)


@dataclass(frozen=True)
class Highlight:
    start: float
    end: float
    peak: float
    category: str
    score: float
    confidence: float
    reason: str
    evidence: tuple[Evidence, ...]


@dataclass(frozen=True)
class _Seed:
    evidence: Evidence
    cue: Cue

    @property
    def confidence(self) -> float:
        return self.evidence.confidence * self.cue.strength


@dataclass(frozen=True)
class _Candidate:
    highlight: Highlight
    core_start: float
    core_end: float
    anchors: frozenset[Evidence]


def _evidence_key(row: Evidence) -> tuple:
    return row.start, row.end, row.kind, row.source, row.text, row.tags, row.confidence, row.verified


def _overlaps(row: Evidence, start: float, end: float) -> bool:
    return row.start <= end and row.end >= start


def _window(start: float, end: float, peak: float, duration: float, config: Config) -> tuple[float, float]:
    """Keep setup and reaction when possible, then fit the source and limits."""
    first = max(0.0, start - config.lead_in)
    last = min(duration, end + config.payoff)
    if last - first > config.max_duration:
        # Preserve the event endpoint/payoff instead of truncating it by
        # blindly keeping the earliest setup of a long transcript segment.
        last = min(duration, peak + config.payoff)
        first = max(0.0, last - config.max_duration)
        if peak < first:
            first = peak
            last = min(duration, first + config.max_duration)
    minimum = min(config.min_duration, duration)
    if last - first < minimum:
        missing = minimum - (last - first)
        first = max(0.0, first - missing / 2.0)
        last = min(duration, first + minimum)
        first = max(0.0, last - minimum)
    return first, last


def _model_matches(row: Evidence, category: str) -> bool:
    # Only a schema-validated, explicitly category-grounded model response
    # can support an already present transcript cue. Free-form instructions
    # or a model's unsupported event guesses do not seed anything.
    return row.verified and (category in row.tags or f"event:{category}" in row.tags)


def _support(rows: tuple[Evidence, ...], anchors: frozenset[Evidence], category: str, first: float, last: float, config: Config) -> tuple[Evidence, ...]:
    support = []
    for row in rows:
        if row.confidence == 0 or not _overlaps(row, first, last):
            continue
        if row.kind == "transcript":
            # Other explicit event/reaction cues preserve context for a
            # chase-to-crash chain. They do not change the primary semantic
            # confidence or contribute an extra score weight.
            if row in anchors or classify_text(row.text, roleplay_enabled=config.roleplay_enabled):
                support.append(row)
            continue
        if row.kind in MEDIA_KINDS and row.verified:
            support.append(row)
        elif row.kind == "chat" and is_nomination(row.text):
            support.append(row)
        elif row.kind == "model" and _model_matches(row, category):
            support.append(row)
    return tuple(support)


_OBSERVATION_NAMES = {
    "video_motion": "measured frame change",
    "video_scene_change": "measured scene change",
    "video_color_change": "measured colour change",
    "audio_spike": "measured audio spike",
    "chat": "chat nomination",
    "model": "grounded optional model corroboration",
}


def _reason(best: _Seed, support: tuple[Evidence, ...], components: tuple[tuple[str, float], ...]) -> str:
    row = best.evidence
    # Whitespace cleanup and a short quote keep reasons readable and prevent
    # raw model/chat text from masquerading as instructions in the result.
    quote = " ".join(row.text.split())
    if len(quote) > 160:
        quote = quote[:157] + "..."
    reason = f'Transcript cue for {best.cue.category.replace("_", " ")} at {row.start:g}–{row.end:g}s: "{quote}"'
    corroboration = []
    contributing = {kind for kind, value in components if value > 0 and kind != "semantic"}
    for kind in _OBSERVATION_NAMES:
        matching = [item for item in support if item.kind == kind]
        if kind in contributing and matching:
            strongest = max(matching, key=lambda item: (item.confidence, -item.start))
            corroboration.append(f"{_OBSERVATION_NAMES[kind]} at {strongest.start:g}s")
    if corroboration:
        reason += "; supported by " + ", ".join(corroboration)
    return reason + "."


def _groups(seeds: list[_Seed], config: Config) -> Iterable[list[_Seed]]:
    grouped: list[_Seed] = []
    end = 0.0
    for seed in seeds:
        if grouped and (seed.evidence.start - end > config.merge_gap or seed.evidence.end - grouped[0].evidence.start > config.max_duration):
            yield grouped
            grouped = []
        grouped.append(seed)
        end = max(end, seed.evidence.end) if len(grouped) > 1 else seed.evidence.end
    if grouped:
        yield grouped


def temporal_iou(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    """Intersection-over-union of two time intervals; point rows have no area."""
    intersection = max(0.0, min(a_end, b_end) - max(a_start, b_start))
    union = max(a_end, b_end) - min(a_start, b_start)
    return intersection / union if union > 0 else 0.0


def _duplicate(candidate: _Candidate, previous: _Candidate, merge_gap: float) -> bool:
    a, b = candidate.highlight, previous.highlight
    overlap = temporal_iou(a.start, a.end, b.start, b.end)
    shared_anchor = bool(candidate.anchors & previous.anchors)
    same_category = a.category == b.category
    shared_support = bool(set(a.evidence) & set(b.evidence))
    core_gap = max(candidate.core_start, previous.core_start) - min(candidate.core_end, previous.core_end)
    adjacent_chain = core_gap <= merge_gap
    reaction_context = "reaction" in (a.category, b.category)
    # Different categories may describe one chain (a chase ending in a
    # crash). Shared source observations and substantial temporal overlap
    # make one reviewable moment, while separate events retain their clips.
    return ((shared_anchor and overlap >= 0.30)
            or (adjacent_chain and shared_support and overlap >= 0.30)
            or (reaction_context and shared_support and overlap >= 0.30)
            or (overlap >= 0.55 and (same_category or shared_support))
            or overlap >= 0.85)


def detect(evidence: list[Evidence], duration: float, config: Config | None = None) -> list[Highlight]:
    """Return chronological, deduplicated highlights from source evidence.

    Empty evidence, audio/video-only input, and unsupported model/chat claims
    return no highlights. A source shorter than the minimum clip length may
    yield its full duration; all other clips respect both configured limits.
    """
    config = config or Config()
    if not isinstance(config, Config):
        raise TypeError("config must be a Config")
    if isinstance(duration, bool):
        raise ValueError("duration must be a finite nonnegative number")
    try:
        duration = float(duration)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("duration must be a finite nonnegative number") from None
    if not math.isfinite(duration) or duration < 0:
        raise ValueError("duration must be a finite nonnegative number")
    if any(not isinstance(row, Evidence) for row in evidence):
        raise TypeError("evidence must contain Evidence records")
    if duration == 0 or config.max_highlights == 0:
        return []
    # Events beginning at or past EOF have no source media to include.
    rows = tuple(sorted({row for row in evidence if row.start < duration and row.confidence > 0}, key=_evidence_key))
    seeds: dict[str, list[_Seed]] = {}
    for row in rows:
        if row.kind != "transcript":
            continue
        for cue in classify_text(row.text, roleplay_enabled=config.roleplay_enabled):
            if config.enabled_categories and cue.category not in config.enabled_categories:
                continue
            seeds.setdefault(cue.category, []).append(_Seed(row, cue))
    candidates = []
    for category in sorted(seeds):
        for group in _groups(seeds[category], config):
            best = max(group, key=lambda item: (item.confidence, item.evidence.end, item.evidence.start))
            core_start = min(seed.evidence.start for seed in group)
            core_end = min(duration, max(seed.evidence.end for seed in group))
            peak = min(duration, best.evidence.end)
            first, last = _window(core_start, core_end, peak, duration, config)
            anchors = frozenset(seed.evidence for seed in group)
            support = _support(rows, anchors, category, first, last, config)
            breakdown = score_evidence(support, semantic_confidence=best.confidence)
            if breakdown.score < config.min_score or breakdown.confidence < config.min_confidence or last <= first:
                continue
            highlight = Highlight(first, last, peak, category, breakdown.score, breakdown.confidence, _reason(best, support, breakdown.components), support)
            candidates.append(_Candidate(highlight, core_start, core_end, anchors))
    # Rank before suppression so the strongest explanation survives. Stable
    # ties and a final chronological sort make the result reproducible.
    ranked = sorted(candidates, key=lambda item: (-item.highlight.score, -item.highlight.confidence, item.highlight.start, item.highlight.category))
    selected: list[_Candidate] = []
    for candidate in ranked:
        if not any(_duplicate(candidate, previous, config.merge_gap) for previous in selected):
            selected.append(candidate)
            if len(selected) >= config.max_highlights:
                break
    return [item.highlight for item in sorted(selected, key=lambda item: (item.highlight.start, item.highlight.end, item.highlight.category))]


__all__ = ["Config", "Highlight", "detect", "temporal_iou"]
