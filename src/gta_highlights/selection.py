# SPDX-License-Identifier: MIT
"""Joint ranking of complete source incidents and conservative viewer review picks."""

from __future__ import annotations

import math
from dataclasses import replace

from .detector import Highlight, _window
from .scoring import score_nomination_review

BUCKET_SECONDS = 10


def mapped_count(row):
    if row.kind != "chat" or not row.verified or row.source != "host-mapped audience signals":
        return 0
    values = [int(tag[6:]) for tag in row.tags if tag.startswith("count:") and tag[6:].isdigit()]
    return values[0] if len(values) == 1 else 0


def nomination_candidates(evidence, duration, config):
    if config.enabled_categories and "viewer_nominated" not in config.enabled_categories:
        return []
    buckets = {}
    # Identical aggregate rows describe the same host bucket, not extra voters.
    for row in set(evidence):
        if mapped_count(row):
            buckets.setdefault(math.floor(row.start / BUCKET_SECONDS), []).append(row)
    found = []
    for bucket, nominations in sorted(buckets.items()):
        count = sum(mapped_count(row) for row in nominations)
        first, last = bucket * BUCKET_SECONDS, min(duration, (bucket+1)*BUCKET_SECONDS)
        activity = [r for r in evidence if r.verified and r.confidence > 0
                    and r.kind in {"audio_spike", "video_motion"} and first <= r.start < last]
        if count < 2 or not activity:
            continue
        peak = max(activity, key=lambda r: r.confidence).start
        start, end = _window(first, last, peak, duration, replace(config, lead_in=0, payoff=0))
        breakdown = score_nomination_review(count, activity)
        score, confidence = breakdown.score, breakdown.confidence
        if score < config.min_score or confidence < config.min_confidence:
            continue
        found.append(Highlight(start, end, peak, "viewer_nominated", score, confidence,
                     f"{count} mapped viewer nominations coincide with measured audio or motion in a 10s source bucket; event identity is unknown.",
                     tuple(nominations + activity), first, last,
                     breakdown.components, ("chat", "measured_activity"),
                     ("Viewer nomination review candidate; no gameplay event is identified.",), "Viewer nominated moment"))
    return found


def required_bounds(item):
    """A selected source response is required even after the action cue ends."""
    transcript = [r for r in item.evidence if r.kind == "transcript"]
    return (min([item.action_start] + [r.start for r in transcript]),
            max([item.action_end] + [r.end for r in transcript]))


def _complete(item):
    first, last = required_bounds(item)
    return item.start <= first and item.end >= last


def _same_incident(a, b):
    intersection = max(0, min(a.action_end, b.action_end) - max(a.action_start, b.action_start))
    smaller = min(a.action_end-a.action_start, b.action_end-b.action_start)
    # Use causal cores, not generic padding, to preserve neighboring events.
    overlap = intersection / smaller if smaller > 0 else 0
    shared = set(r for r in a.evidence if r.kind == "transcript") & set(r for r in b.evidence if r.kind == "transcript")
    dialogue = any(r.source == "source-grounded local-model dialogue selection" for r in a.evidence+b.evidence)
    if not dialogue and "viewer_nominated" not in {a.category, b.category} and a.reason != b.reason:
        # The detector has already deduplicated its explicit cues. Separate
        # actions must survive even when their source segments and contextual
        # padding overlap. Joint discovery must not undo that distinction.
        return False
    return overlap >= 0.6 and (bool(shared) or "viewer_nominated" in {a.category, b.category})


def select_highlights(candidates, limit):
    """Apply the count only after joint discovery, completeness and deduplication."""
    candidates = list(candidates)
    removed = set()
    action_categories = {"chase", "crash", "stunt", "combat", "npc_chaos", "milestone"}
    # A complete explicit short action is a reviewable alternative to a long
    # conversation containing it. Keep its action title; the conversation's
    # question/accusation title cannot describe the narrower source cut.
    for index, broad in enumerate(candidates):
        if broad.end-broad.start <= 45 or broad.category not in {"roleplay", "funny_dialogue"}:
            continue
        alternatives = [(i, h) for i, h in enumerate(candidates) if i != index
                        and h.category in action_categories and _complete(h) and h.end-h.start <= 40
                        and broad.action_start <= h.action_start < h.action_end <= broad.action_end
                        and _same_incident(broad, h)]
        if alternatives:
            chosen, narrow = max(alternatives, key=lambda pair: (pair[1].score, pair[1].confidence, -pair[1].start))
            removed.add(index)
            reason = (f"Preferred complete {narrow.category} alternative {narrow.action_start:g}-{narrow.action_end:g}s "
                      f"over long {broad.category} conversation {broad.action_start:g}-{broad.action_end:g}s; retained the action title.")
            candidates[chosen] = replace(narrow, suppressed_reasons=narrow.suppressed_reasons+(reason,))
    candidates = [h for i, h in enumerate(candidates) if i not in removed]
    ranked = sorted(candidates, key=lambda h: (not _complete(h), h.category == "viewer_nominated",
                    -h.score, -h.confidence, h.end-h.start, h.start, h.category))
    selected = []
    for candidate in ranked:
        duplicate = next((i for i, h in enumerate(selected) if _same_incident(candidate, h)), None)
        if duplicate is None:
            selected.append(candidate)
        else:
            previous = selected[duplicate]
            reason = f"Suppressed overlapping {candidate.category} alternative {candidate.action_start:g}-{candidate.action_end:g}s for the same incident."
            selected[duplicate] = replace(previous, suppressed_reasons=previous.suppressed_reasons+(reason,))
    return sorted(selected[:limit], key=lambda h: (h.start, h.end, h.category))
