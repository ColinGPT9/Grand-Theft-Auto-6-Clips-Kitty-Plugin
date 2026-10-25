# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ColinGPT9
"""Offline score invariants; no game media or external models are needed."""

from dataclasses import FrozenInstanceError

import pytest

from gta_highlights.scoring import Evidence, is_nomination, score_evidence


def transcript(confidence=1.0):
    return Evidence(10, 12, "transcript", confidence, "We crashed into the wall.")


def test_missing_semantics_and_media_only_have_zero_score():
    loud = Evidence(11, 11, "audio_spike", verified=True)
    assert score_evidence([]).score == 0
    assert score_evidence([loud]).score == 0
    assert score_evidence([loud], semantic_confidence=1).score == 0
    assert score_evidence([transcript()]).score == 0


def test_verified_independent_support_improves_bounded_explainable_score():
    speech = transcript(0.9)
    initial = score_evidence([speech], semantic_confidence=0.9)
    supported = score_evidence([
        speech,
        Evidence(10, 11, "video_motion", 0.8, verified=True),
        Evidence(11, 11, "audio_spike", 0.9, verified=True),
    ], semantic_confidence=0.9)
    assert 0 < initial.score < supported.score <= 1
    assert 0 < initial.confidence < supported.confidence <= 1
    assert dict(supported.components) == {"semantic": 0.558, "video_motion": 0.08, "audio_spike": 0.0675}


def test_duplicate_and_weaker_measurements_cannot_inflate_score():
    speech = transcript()
    loud = Evidence(11, 11, "audio_spike", 0.9, verified=True)
    weak = Evidence(11.1, 11.1, "audio_spike", 0.2, verified=True)
    assert score_evidence([speech, loud], semantic_confidence=1) == score_evidence([speech] * 20 + [loud] * 100 + [weak], semantic_confidence=1)


def test_unverified_media_and_models_are_ignored():
    speech = transcript()
    baseline = score_evidence([speech], semantic_confidence=1)
    assert score_evidence([
        speech,
        Evidence(11, 11, "video_scene_change"),
        Evidence(11, 11, "model", text="A huge crash!"),
    ], semantic_confidence=1) == baseline


def test_chat_requires_positive_explicit_nomination():
    speech = transcript()
    baseline = score_evidence([speech], semantic_confidence=1)
    for text in ("hello", "do not clip that", "Don't clip this", "this is not clip worthy"):
        assert score_evidence([speech, Evidence(10, 12, "chat", text=text)], semantic_confidence=1) == baseline
    assert score_evidence([speech, Evidence(10, 12, "chat", text="clip that!")], semantic_confidence=1).score > baseline.score
    assert is_nomination("don't clip this; but clip that!")


@pytest.mark.parametrize("kwargs", [
    {"start": -1}, {"start": float("nan")}, {"end": float("inf")},
    {"end": -1}, {"confidence": -0.1}, {"confidence": 1.1},
    {"confidence": True}, {"kind": "object_detection"}, {"tags": "crash"},
    {"tags": (123,)}, {"text": None}, {"verified": "yes"},
])
def test_invalid_evidence_is_rejected(kwargs):
    values = {"start": 0, "end": 1, "kind": "transcript"}
    values.update(kwargs)
    with pytest.raises(ValueError):
        Evidence(**values)


def test_evidence_normalizes_sequences_and_is_immutable():
    row = Evidence(0, 1, "transcript", tags=["one"])
    assert row.tags == ("one",)
    with pytest.raises(FrozenInstanceError):
        row.confidence = 0.2


@pytest.mark.parametrize("confidence", [-1, 2, float("nan"), True])
def test_invalid_semantic_confidence_is_rejected(confidence):
    with pytest.raises(ValueError):
        score_evidence([transcript()], semantic_confidence=confidence)
