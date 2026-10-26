# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ColinGPT9
"""Original adversarial constraints beyond the frozen before/after corpus."""

import json
import random
from pathlib import Path

import pytest

from evaluation.quality import evaluate
from gta_highlights import Config, Evidence, detect


def speech(start, end, text):
    return Evidence(start, end, "transcript", text=text, source="original test commentary")


def test_all_frozen_quality_cases_pass_with_identical_before_after_input_hashes():
    report = evaluate()
    before = json.loads((Path(__file__).parents[1] / "evaluation/results/quality-before.json").read_text(encoding="utf-8"))
    assert report["fixture_sha256"] == before["fixture_sha256"]
    assert all(row["passed"] for row in report["cases"])


@pytest.mark.parametrize("frame", ["Here is my plan.", "Last week was wild.", "Imagine this.", "In my dream."])
def test_context_in_preceding_asr_segment_prevents_false_incident(frame):
    rows = [speech(20, 22, frame), speech(23, 25, "We crashed into a truck.")]
    rows += [Evidence(24, 24, "audio_spike", verified=True), Evidence(24, 24, "video_motion", verified=True)]
    assert detect(rows, 100) == []


def test_explicit_current_time_resets_a_preceding_historical_frame():
    rows = [speech(20, 22, "Last week was wild."), speech(23, 25, "Now we crashed into a truck.")]
    assert len(detect(rows, 100)) == 1


def test_separate_actions_with_overlapping_source_intervals_are_preserved():
    rows = [speech(30, 34, "We crashed into a wall."), speech(32, 36, "That car just flipped.")]
    found = detect(rows, 100)
    assert len(found) == 2
    assert {(h.action_start, h.action_end) for h in found} == {(30, 34), (32, 36)}


def test_suppression_explains_why_one_incident_has_one_output():
    rows = [speech(30, 32, "The cops are chasing me!"), speech(34, 36, "We crashed into a wall.")]
    found = detect(rows, 100)
    assert len(found) == 1
    assert found[0].suppressed_reasons
    assert "same supported incident" in found[0].suppressed_reasons[0]


def test_long_action_is_never_silently_truncated():
    moment = detect([speech(20, 70, "We crashed into a wall.")], 100,
                    Config(min_duration=10, max_duration=20))[0]
    assert moment.action_start == 20 and moment.action_end == 70
    assert any("truncated" in warning for warning in moment.review_warnings)
    assert moment.end - moment.start <= 20


def test_score_components_sum_to_score_and_modalities_are_observations_only():
    source = speech(30, 32, "We crashed into a wall.")
    transcript = detect([source], 100)[0]
    supported = detect([source, Evidence(31, 31, "audio_spike", verified=True)], 100)[0]
    assert transcript.available_modalities == ("transcript",)
    assert supported.available_modalities == ("audio", "transcript")
    assert sum(dict(supported.score_components).values()) == pytest.approx(supported.score, abs=0.0001)
    assert dict(transcript.score_components).get("audio_spike", 0) == 0
    assert supported.score > transcript.score
    assert dict(supported.score_components)["novelty"] == 0


def test_factual_reaction_title_has_no_invented_gameplay_cause():
    found = detect([speech(30, 32, "Oh my goodness!")], 100)
    assert found[0].title == "Creator reaction"
    assert found[0].action_start == 30


@pytest.mark.parametrize("requested", [0, 1, 2, 7])
def test_top_n_never_fills_with_unsupported_events(requested):
    rows = [speech(10, 12, "We crashed into a wall."), speech(70, 72, "An NPC just stole my car.")]
    rows += [Evidence(50, 50, "audio_spike", verified=True)]
    assert len(detect(rows, 100, Config(max_highlights=requested))) == min(requested, 2)


def test_setup_utterance_is_preserved_as_context_evidence():
    premise = speech(19, 28, "Why does the mechanic want my receipt?")
    payoff = speech(30, 33, "I said the car is the receipt. That was hilarious.")
    found = detect([premise, payoff], 100)[0]
    assert premise in found.evidence
    assert found.start <= premise.start and found.end >= payoff.end


def test_low_level_signals_cannot_rescue_uncertain_context():
    rows = [speech(30, 32, "Maybe that car just flipped.")]
    rows += [Evidence(31, 31, kind, verified=True) for kind in ("audio_spike", "video_motion", "video_scene_change")]
    assert detect(rows, 100) == []


def test_varied_source_edges_and_duration_limits_preserve_action_or_explain_truncation():
    rng = random.Random(20261025)
    for _ in range(300):
        duration = rng.uniform(1, 180)
        start = rng.uniform(0, duration - 0.01)
        end = rng.uniform(start + 0.001, duration)
        maximum = rng.uniform(1, 60)
        minimum = rng.uniform(0, maximum)
        config = Config(min_duration=minimum, max_duration=maximum,
                        lead_in=rng.uniform(0, 12), payoff=rng.uniform(0, 10))
        found = detect([speech(start, end, "We crashed into a wall.")], duration, config)
        assert len(found) == 1
        moment = found[0]
        assert 0 <= moment.start < moment.end <= duration
        assert moment.end - moment.start <= maximum + 1e-8
        assert moment.end - moment.start >= min(minimum, duration) - 1e-8
        if end - start <= maximum:
            assert moment.start <= start and moment.end >= end
        else:
            assert any("truncated" in warning for warning in moment.review_warnings)
