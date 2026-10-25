# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ColinGPT9
"""Deterministic source-evidence, clip-boundary, and duplicate regressions."""

import pytest

from gta_highlights import Config, Evidence, detect
from gta_highlights.detector import temporal_iou


def speech(start=30, end=32, text="We crashed into a truck!", confidence=1):
    return Evidence(start, end, "transcript", confidence, text, source="test transcript")


def media(start=31, kind="audio_spike", confidence=1, verified=True):
    return Evidence(start, start, kind, confidence, verified=verified, source="test measurement")


def test_explicit_crash_has_setup_payoff_and_honest_source_explanation():
    spoken = speech()
    measured = media()
    found = detect([spoken, measured], 120)
    assert len(found) == 1
    moment = found[0]
    assert (moment.start, moment.end, moment.peak, moment.category) == (22, 42, 32, "crash")
    assert spoken in moment.evidence and measured in moment.evidence
    assert 'Transcript cue for crash at 30–32s: "We crashed into a truck!"' in moment.reason
    assert "measured audio spike" in moment.reason
    assert "recognized" not in moment.reason
    assert 0.42 <= moment.score <= 1
    assert 0.35 <= moment.confidence <= 1


def test_audio_video_chat_and_ungrounded_model_cannot_invent_events():
    rows = [
        media(), media(kind="video_motion"), media(kind="video_scene_change"),
        Evidence(31, 32, "chat", text="clip that crash", tags=("event:crash",)),
        Evidence(31, 32, "model", text="Explosive crash", tags=("event:crash",), verified=True),
    ]
    assert detect(rows, 120) == []
    assert detect([], 120) == []


@pytest.mark.parametrize("text", [
    "We did not crash into a truck.",
    "If we crashed into a truck, it would be bad.",
    "I'm going to crash into a truck.",
    "I have a car and the police are at the station.",
])
def test_negative_and_hypothetical_speech_cannot_be_rescued_by_loudness(text):
    assert detect([speech(text=text), media(), media(kind="video_scene_change")], 120) == []


def test_measured_corroboration_raises_score_but_unverified_or_distant_does_not():
    spoken = speech()
    baseline = detect([spoken], 120)[0]
    actual = detect([spoken, media()], 120)[0]
    asserted = detect([spoken, media(verified=False)], 120)[0]
    distant = detect([spoken, media(start=100)], 120)[0]
    assert actual.score > baseline.score
    assert asserted.score == distant.score == baseline.score
    assert len(asserted.evidence) == len(distant.evidence) == 1


def test_only_nearby_explicit_chat_nomination_and_grounded_model_add_support():
    spoken = speech()
    baseline = detect([spoken], 120)[0]
    rows = [
        spoken,
        Evidence(33, 34, "chat", text="CLIP THAT"),
        Evidence(31, 33, "model", tags=("event:crash",), verified=True),
        Evidence(31, 33, "model", tags=("event:combat",), verified=True),
        Evidence(100, 101, "chat", text="clip that"),
    ]
    result = detect(rows, 120)[0]
    assert result.score > baseline.score
    assert len(result.evidence) == 3
    assert "chat nomination at 33s" in result.reason


def test_minimum_length_respects_short_source_and_eof():
    early = detect([speech(0, 1)], 120, Config(lead_in=0, payoff=0))[0]
    assert (early.start, early.end) == (0, 12)
    late = detect([speech(119, 120)], 120, Config(lead_in=0, payoff=0))[0]
    assert (late.start, late.end) == (108, 120)
    short = detect([speech(1, 2)], 5)[0]
    assert (short.start, short.end) == (0, 5)


def test_maximum_length_keeps_peak_and_reaction_tail():
    result = detect([speech(30, 50)], 120, Config(min_duration=10, max_duration=15, lead_in=8, payoff=5))[0]
    assert result.end - result.start == 15
    assert result.start <= result.peak <= result.end
    assert result.end == 55


def test_evidence_beyond_eof_is_ignored_and_straddling_eof_is_clamped():
    assert detect([speech(120, 125)], 120) == []
    result = detect([speech(119, 130)], 120)[0]
    assert result.end == result.peak == 120
    assert result.start >= 0
    assert detect([speech()], 0) == []


def test_repeated_same_event_is_joined_and_duplicate_rows_do_not_raise_score():
    first = speech(30, 32)
    second = speech(33, 35)
    normal = detect([first, second, media()], 120)
    repeated = detect([first, second, media()] * 30, 120)
    assert len(normal) == 1
    assert normal == repeated
    assert normal[0].start == 22 and normal[0].end == 45


def test_separate_events_survive_and_result_is_chronological():
    first, second = speech(10, 12), speech(90, 92)
    moments = detect([second, first], 120)
    assert len(moments) == 2
    assert [item.start for item in moments] == [2, 82]
    assert detect([first, second], 120, Config(max_highlights=1)) == moments[:1]


def test_same_transcript_with_multiple_categories_does_not_duplicate_clip():
    rows = [speech(text="The cops are chasing me and we crashed into a truck!")]
    assert len(detect(rows, 120)) == 1


def test_adjacent_chase_to_crash_chain_has_one_clip_with_both_source_cues():
    chase = speech(30, 32, "The cops are chasing me!")
    crash = speech(34, 35)
    result = detect([chase, crash], 120)
    assert len(result) == 1
    assert {chase, crash} <= set(result[0].evidence)


def test_reaction_in_the_payoff_is_context_instead_of_an_extra_clip():
    crash = speech(30, 32)
    reaction = speech(38, 39, "Oh my god!")
    result = detect([crash, reaction], 120)
    assert len(result) == 1
    assert result[0].category == "crash"
    assert reaction in result[0].evidence


def test_categories_and_roleplay_are_explicitly_configurable():
    assert detect([speech()], 120, Config(enabled_categories=("chase",))) == []
    rp = speech(text="We are in a traffic stop.")
    assert detect([rp], 120) == []
    result = detect([rp], 120, Config(roleplay_enabled=True))
    assert len(result) == 1 and result[0].category == "roleplay"
    assert detect([speech()], 120, Config(max_highlights=0)) == []


def test_low_confidence_unsupported_cue_cannot_pass_default_thresholds():
    assert detect([speech(confidence=0.1), media()], 120) == []


@pytest.mark.parametrize("kwargs", [
    {"min_score": 1.1}, {"min_confidence": -1}, {"min_duration": 61},
    {"max_duration": 0}, {"lead_in": float("nan")}, {"payoff": float("inf")},
    {"merge_gap": -1}, {"max_highlights": -1}, {"max_highlights": True},
    {"enabled_categories": ("not_gta",)}, {"enabled_categories": "crash"},
    {"roleplay_enabled": "yes"},
])
def test_invalid_config_is_rejected(kwargs):
    with pytest.raises(ValueError):
        Config(**kwargs)


@pytest.mark.parametrize("duration", [-1, float("nan"), float("inf"), True, None])
def test_invalid_duration_is_rejected(duration):
    with pytest.raises(ValueError):
        detect([], duration)


def test_temporal_iou_handles_overlap_disjoint_and_points():
    assert temporal_iou(0, 10, 5, 15) == pytest.approx(1 / 3)
    assert temporal_iou(0, 1, 2, 3) == 0
    assert temporal_iou(1, 1, 1, 1) == 0
