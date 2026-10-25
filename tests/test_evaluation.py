"""Check metric arithmetic and the reproducibility of actual detector runs."""

from __future__ import annotations

from evaluation.metrics import aggregate, coverage, evaluate_case, temporal_iou
from evaluation.run import evaluate_fixtures, load_cases

EVENT = {"id": "example", "start": 10, "end": 30,
         "setup": [10, 17], "payoff": [18, 21], "reaction": [22, 30]}


def test_matching_is_one_to_one_and_duplicate_is_false_positive():
    metrics = evaluate_case([{"start": 10, "end": 30}, {"start": 11, "end": 29}], [EVENT])
    assert metrics["true_positives"] == 1
    assert metrics["false_positives"] == 1
    assert metrics["false_negatives"] == 0
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 1.0
    assert metrics["duplicate_rate"] == 0.5
    assert metrics["overlapping_prediction_pairs"] == 1
    assert metrics["event_completeness_rate"] == 1.0


def test_overlap_alone_does_not_count_without_payoff():
    metrics = evaluate_case([{"start": 10, "end": 18.5}], [EVENT])
    assert metrics["true_positives"] == 0
    assert metrics["false_positives"] == 1
    assert metrics["false_negatives"] == 1
    assert coverage((10, 18.5), EVENT["payoff"]) == 1 / 6
    assert temporal_iou((0, 10), (5, 15)) == 1 / 3


def test_truncated_setup_can_match_but_is_incomplete():
    metrics = evaluate_case([{"start": 16, "end": 30}], [EVENT])
    assert metrics["true_positives"] == 1
    assert metrics["complete_events"] == 0
    assert metrics["matches"][0]["component_coverage"]["payoff"] == 1
    assert metrics["event_completeness_rate"] == 0


def test_empty_cases_have_explicit_undefined_precision_and_recall():
    metrics = evaluate_case([], [])
    assert metrics["precision"] is None
    assert metrics["recall"] is None
    assert metrics["duplicate_rate"] == 0
    summary = aggregate([{"metrics": metrics}])
    assert summary["precision"] is None
    assert summary["recall"] is None


def test_fixture_annotations_have_valid_unique_bounded_components():
    document = load_cases()
    assert len({case["id"] for case in document["cases"]}) == len(document["cases"])
    assert {case["split"] for case in document["cases"]} == {"development", "holdout"}
    for case in document["cases"]:
        assert case["duration"] > 0
        for event in case["events"]:
            assert 0 <= event["start"] < event["end"] <= case["duration"]
            for name in ("setup", "payoff", "reaction"):
                start, end = event[name]
                assert event["start"] <= start < end <= event["end"]


def test_real_detectors_run_deterministically_on_every_authored_case():
    document = load_cases()
    first = evaluate_fixtures(document)
    assert evaluate_fixtures(document) == first
    assert first["manual_review"]["visual_framing"] is None
    plugin = {case["case_id"]: case for case in first["detectors"]["gta_plugin"]["cases"]}
    baseline = {case["case_id"]: case for case in first["detectors"]["energy_only_baseline"]["cases"]}
    assert plugin["loud_noise_negative"]["predictions"] == []
    assert baseline["loud_noise_negative"]["metrics"]["false_positives"] > 0
    assert plugin["roleplay_default_off"]["predictions"] == []
    assert plugin["roleplay_explicit_opt_in"]["predictions"]
    assert plugin["no_inputs"]["predictions"] == []
    # Explicitly preserve the documented recall limitation.
    assert plugin["untranscribed_crash_is_missed"]["metrics"]["false_negatives"] == 1
