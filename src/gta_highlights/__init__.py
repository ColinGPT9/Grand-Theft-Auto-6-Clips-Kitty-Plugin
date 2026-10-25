# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ColinGPT9
"""Original GTA highlight heuristics, independent of the host runtime."""

from .detector import Config, Highlight, detect
from .scoring import Evidence, ScoreBreakdown, score_evidence
from .taxonomy import CATEGORIES

__all__ = ["CATEGORIES", "Config", "Evidence", "Highlight", "ScoreBreakdown", "detect", "score_evidence"]
