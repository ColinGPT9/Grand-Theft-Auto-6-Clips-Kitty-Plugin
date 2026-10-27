# SPDX-License-Identifier: MIT
"""Bound optional work and persist only validated source-window outcomes."""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

from .observations import finite, number_setting

SCHEMA_VERSION = "gta-dialogue-2"


def cache_directory():
    """Only the host may grant persistent per-plugin storage outside its code."""
    supplied = os.environ.get("CLIPS_KITTY_PLUGIN_CACHE_DIR", "")
    if not supplied:
        return None
    path = Path(supplied)
    return path / "dialogue-v2" if path.is_absolute() else None


class ReviewBudget:
    def __init__(self, job, invocation_started=None):
        self.started = time.monotonic()
        settings = getattr(job, "settings", {})
        self.maximum = number_setting(settings, "dialogue_review_minutes", 20, 0, 20) * 60
        # The manifest's 30 minute timeout covers ALL stages, not only review.
        # Job API v1 exposes no deadline. Leave 30s for results/render suggestions.
        self.host_end = (self.started if invocation_started is None else invocation_started) + 30 * 60 - 30
        supplied = finite(os.environ.get("CLIPS_KITTY_PLUGIN_DEADLINE_MONOTONIC"))
        if supplied is not None and supplied > 0:
            self.host_end = min(self.host_end, supplied - 5)
        self.end = min(self.started + self.maximum, self.host_end)
        self.stats = {"schema_version": SCHEMA_VERSION, "total_windows": 0, "reviewed_windows": 0,
                      "attempted_windows": 0, "failed_windows": 0, "cache_hits": 0, "cache_misses": 0,
                      "invalid_cache_entries": 0,
                      "covered_segments": 0, "total_segments": 0, "coverage_fraction": 0.0,
                      "budget_seconds": self.maximum, "budget_exhausted": False,
                      "deadline_basis": "manifest_30_minutes_with_reserve"}
        if supplied is not None and supplied > 0:
            self.stats["deadline_basis"] = "host_monotonic_deadline"

    def timeout(self):
        remaining = self.end - time.monotonic()
        if remaining <= 0.05:
            self.stats["budget_exhausted"] = True
            return None
        return min(15.0, remaining)

    def report(self):
        return {**self.stats, "elapsed_seconds": round(time.monotonic() - self.started, 3)}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def cache_identity(job, rows, duration, config):
    tools = getattr(job, "tools", None)
    model = getattr(tools, "ollama", None)
    if not isinstance(model, dict) or not model.get("model"):
        return None
    video = getattr(job, "video", None)
    # Fingerprint complete source transcript, not a mutable filename or a title.
    source = {"id": getattr(video, "id", ""), "duration": duration,
              "title": getattr(video, "title", ""),
              "transcript": [(r.start, r.end, r.text, r.confidence) for r in rows]}
    path = getattr(video, "path", None)
    if path is not None:
        try:
            stat = Path(path).stat()
            source["media"] = (str(Path(path).resolve()), stat.st_size, stat.st_mtime_ns)
        except OSError:
            return None
    return {"schema": SCHEMA_VERSION, "source": digest(source),
            "effective_model": {k: model.get(k) for k in ("model", "host", "revision")},
            "settings": dict(getattr(job, "settings", {})), "config": vars(config)}


def read_cache(key, directory):
    try:
        path = directory / (key + ".json")
        if path.stat().st_size > 25000:
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        if (isinstance(payload, dict) and set(payload) == {"schema", "key", "answer"}
                and payload["schema"] == SCHEMA_VERSION and payload["key"] == key
                and isinstance(payload["answer"], str)):
            return payload["answer"]
    except (OSError, ValueError, TypeError, RecursionError):
        pass
    return None


def write_cache(key, answer, directory):
    try:
        directory.mkdir(parents=True, exist_ok=True)
        # Each outcome is small and self-contained. Incomplete writes fail JSON
        # validation on read and are retried, never interpreted as valid empties.
        (directory / (key + ".json")).write_text(
            json.dumps({"schema": SCHEMA_VERSION, "key": key, "answer": answer}, ensure_ascii=False),
            encoding="utf-8")
    except OSError:
        pass
