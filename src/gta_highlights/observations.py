# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ColinGPT9
"""Read only the media, transcript, and mapped audience signals the SDK supplies."""

from __future__ import annotations

import math
import statistics
from pathlib import Path

from clipskitty_sdk import media, signals

from .scoring import Evidence


def number_setting(settings, name, default, low, high):
    value = settings.get(name, default)
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number from {low:g} to {high:g}")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(f"{name} must be a number from {low:g} to {high:g}") from None
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{name} must be a number from {low:g} to {high:g}")
    return value


def enabled(settings, name, default=False):
    value = settings.get(name, default)
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be true or false")
    return value


def finite(value):
    if isinstance(value, bool):
        return None
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return value if math.isfinite(value) else None


def _transcript(job, notes):
    if getattr(job, "transcript", None) is None:
        notes.append("No transcript was supplied; low-level media signals alone do not identify GTA events.")
        return []
    try:
        segments = job.transcript.segments()
    except (OSError, ValueError, TypeError, AttributeError):
        notes.append("The transcript could not be read; continuing with available evidence.")
        return []
    rows = []
    skipped = 0
    for segment in segments if isinstance(segments, (list, tuple)) else ():
        if not isinstance(segment, dict):
            skipped += 1
            continue
        start, end = finite(segment.get("start")), finite(segment.get("end"))
        confidence = finite(segment.get("confidence", 1.0))
        text = segment.get("text")
        if (start is None or end is None or start < 0 or end < start
                or confidence is None or not 0 <= confidence <= 1
                or not isinstance(text, str) or not text.strip()):
            skipped += 1
            continue
        rows.append(Evidence(start, end, "transcript", confidence, text.strip(), source="SDK transcript"))
    if skipped:
        notes.append(f"Ignored {skipped} malformed or empty transcript segment(s).")
    return rows


def _nominations(job, duration, notes):
    if not enabled(job.settings, "use_nominations", True) or duration <= 0:
        return []
    accounts = getattr(job, "accounts", None)
    twitch = getattr(accounts, "twitch", None) if accounts is not None else None
    operation = getattr(twitch, "audience_signals", None)
    if not callable(operation):
        return []
    try:
        payload = operation()
    except Exception:
        # Connected-account support is optional. No credentials or transport
        # escape this host operation, and unavailable signals are not errors.
        notes.append("Mapped audience nominations were unavailable.")
        return []
    if not isinstance(payload, dict) or payload.get("status") not in ("ok", "available", "mapped"):
        return []
    nominations = payload.get("nominations")
    if not isinstance(nominations, list):
        return []
    rows = []
    for nomination in nominations[:1000]:
        if not isinstance(nomination, dict):
            continue
        offset = finite(nomination.get("offset_seconds"))
        count = finite(nomination.get("count"))
        commands = nomination.get("commands")
        if offset is None or not 0 <= offset < duration or count is None or count < 1 or not isinstance(commands, dict):
            continue
        accepted = []
        for name in ("clip", "chaos", "funny"):
            amount = finite(commands.get(name, commands.get("!" + name, 0)))
            if amount is not None and amount > 0:
                accepted.append("!" + name)
        if not accepted:
            continue
        # A host-mapped !chaos/!funny command is a nomination, never a claim
        # that chaos or humor was observed at that source time.
        rows.append(Evidence(offset, offset, "chat", min(1.0, 0.5 + math.log1p(count) / 10),
                             "clip that (mapped audience nomination)", tuple(accepted),
                             "host-mapped audience signals", True))
    return rows


def collect_evidence(job):
    """Return ``(observations, source_duration, nonfatal_notes)``.

    Missing video supports transcript-only use. A supplied unreadable video
    is reported through the SDK failure path. Media observations describe
    pixel/brightness differences and LUFS spikes, never object recognition.
    """
    notes = []
    rows = _transcript(job, notes)
    video = getattr(job, "video", None)
    known_duration = finite(getattr(video, "duration", None)) if video is not None else None
    duration = known_duration if known_duration is not None and known_duration > 0 else 0.0
    use_media = enabled(job.settings, "use_media", True)
    fps = number_setting(job.settings, "sample_fps", 1, 0.25, 2)
    threshold = number_setting(job.settings, "motion_threshold", 0.12, 0.01, 1)
    louder_by = number_setting(job.settings, "louder_by_db", 6, 1, 30)
    if video is not None:
        path = getattr(video, "path", None)
        if path is None or not Path(path).is_file():
            job.fail("The supplied video file does not exist or is not a readable file. Select the source footage again.")
        if use_media:
            try:
                info = media.probe(job)
                probed = finite(info.duration)
                if probed is not None and probed > 0:
                    duration = probed
                previous = None
                previous_brightness = None
                for frame in media.frames(job, fps=fps, size=(32, 18)):
                    timestamp = finite(frame.t)
                    if timestamp is None or timestamp < 0 or (duration and timestamp >= duration):
                        continue
                    brightness = signals.brightness(frame)
                    if previous is not None:
                        delta = signals.difference(previous, frame) / 255.0
                        if delta >= threshold:
                            rows.append(Evidence(timestamp, timestamp, "video_motion", min(1.0, delta / (threshold * 2)),
                                                 tags=(f"rgb_difference:{delta:.4f}",), source="SDK sampled RGB frame difference", verified=True))
                        if delta >= max(0.30, threshold * 2):
                            rows.append(Evidence(timestamp, timestamp, "video_scene_change", min(1.0, delta / 0.60),
                                                 tags=(f"rgb_difference:{delta:.4f}",), source="SDK large sampled frame difference", verified=True))
                        brightness_delta = abs(brightness - previous_brightness) / 255.0
                        if brightness_delta >= 0.20:
                            rows.append(Evidence(timestamp, timestamp, "video_color_change", min(1.0, brightness_delta / 0.40),
                                                 tags=(f"brightness_difference:{brightness_delta:.4f}",), source="SDK sampled mean brightness change", verified=True))
                    previous, previous_brightness = frame, brightness
                loudness = media.loudness(job)
                for second in signals.spikes(loudness, louder_by=louder_by):
                    if duration and second >= duration:
                        continue
                    around = loudness[max(0, second - 15):second + 16]
                    excess = loudness[second] - statistics.median(around)
                    rows.append(Evidence(second, second, "audio_spike", min(1.0, max(0.0, excess / (louder_by * 2))),
                                         tags=(f"excess_lufs:{excess:.2f}",), source="SDK measured LUFS above local median", verified=True))
            except (media.MediaError, OSError, ValueError) as error:
                job.fail(f"The supplied footage could not be measured: {error}")
    elif use_media:
        notes.append("No video was supplied; using transcript evidence only.")
    if duration <= 0:
        duration = max([row.end for row in rows] + [getattr(moment, "end", 0) for moment in getattr(job, "moments", [])] + [0.0])
    rows.extend(_nominations(job, duration, notes))
    return rows, duration, notes


__all__ = ["collect_evidence", "enabled", "finite", "number_setting"]
