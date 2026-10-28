# SPDX-License-Identifier: MIT
"""Fictional review priority across the host's preserved-score filter contract."""

import json

import pytest
from test_context_review import mapped, sdk_job, speech

from gta_highlights import adapter
from gta_highlights.detector import Config, detect
from gta_highlights.scoring import Evidence, score_nomination_review
from gta_highlights.selection import nomination_candidates, select_highlights


def activity(kind="video_motion", confidence=1, verified=True):
    return Evidence(32, 32, kind, confidence=confidence, verified=verified)


def test_review_priority_increases_with_concentration_and_independent_activity():
    modest = score_nomination_review(2, [activity()])
    concentrated = score_nomination_review(8, [activity()])
    independent = score_nomination_review(2, [activity(), activity("audio_spike")])
    assert modest.score < 0.55 < concentrated.score
    assert modest.score < independent.score and independent.score > 0.55
    assert concentrated.confidence == independent.confidence == modest.confidence == 0.35
    assert sum(dict(independent.components).values()) == pytest.approx(independent.score, abs=0.0001)


def test_repeated_measurements_and_many_nominations_cannot_inflate_unboundedly():
    rows = [activity(), activity("audio_spike")]
    ordinary = score_nomination_review(8, rows)
    assert score_nomination_review(8, rows*100) == ordinary
    saturated = score_nomination_review(10**100, rows)
    assert ordinary.score < saturated.score <= 0.69


@pytest.mark.parametrize("rows", [[], [activity(verified=False)], [activity("video_scene_change")],
                                  [activity("video_color_change")], [activity(confidence=0)]])
def test_nomination_count_alone_has_no_review_score(rows):
    assert score_nomination_review(100, rows).score == 0


@pytest.mark.parametrize("count", [0, 1, True, 2.5])
def test_review_score_preserves_two_mapped_nomination_gate(count):
    assert score_nomination_review(count, [activity()]).score == 0


def test_weak_activity_is_not_filler_even_with_valid_nomination_gate():
    rows = [mapped(count=2), activity(confidence=0.1)]
    assert nomination_candidates(rows, 100, Config()) == []
    assert score_nomination_review(2, [activity(confidence=0.1)]).score < Config().min_score


def test_review_score_is_evidence_derived_and_does_not_follow_filter_threshold():
    rows = [mapped(count=2), activity(), activity("audio_spike")]
    (ordinary,) = nomination_candidates(rows, 100, Config(min_score=0.42))
    (stricter,) = nomination_candidates(rows, 100, Config(min_score=0.55))
    assert ordinary.score == stricter.score
    assert nomination_candidates(rows, 100, Config(min_score=0.60)) == []
    assert nomination_candidates([mapped(count=100), activity(), activity("audio_spike")],
                                  100, Config(min_score=0.70)) == []


def test_explicit_source_category_still_gets_the_output_slot_before_stronger_nomination():
    source = detect([speech(70, 72, "We crashed into a barrier!")], 100)[0]
    (nominated,) = nomination_candidates([mapped(count=8), activity(), activity("audio_spike")], 100, Config())
    assert nominated.score > source.score
    assert select_highlights([nominated, source], 1) == [source]


@pytest.mark.parametrize("count,confidence,both,passes_host", [(2, 1, False, False),
                                                           (8, 1, False, True),
                                                           (2, 1, True, True),
                                                           (8, 0.2, False, False)])
def test_sdk_find_scores_remain_useful_under_host_preserved_score_filter(
        tmp_path, monkeypatch, count, confidence, both, passes_host):
    rows = [mapped(count=count), activity(confidence=confidence)]
    if both:
        rows.append(activity("audio_spike", confidence))
    monkeypatch.setattr(adapter, "collect_evidence", lambda _job: (rows, 100, []))
    job = sdk_job(tmp_path, [], {"use_local_model": False})
    # The app's find/build_job path does not currently provide limits.min_score.
    # Gaming preserves/rounds the explicit plugin score, then applies its own
    # configured quality threshold after optional image review.
    assert job.limits.min_score is None
    adapter.main(job)
    (clip,) = json.loads((job.folder / "result.json").read_text(encoding="utf-8"))["ranges"]
    assert clip["label"] == "viewer_nominated" and clip["title"] == "Viewer nominated moment"
    assert (round(clip["score"]) >= 55) is passes_host
    assert "event identity is unknown" in clip["reason"]
