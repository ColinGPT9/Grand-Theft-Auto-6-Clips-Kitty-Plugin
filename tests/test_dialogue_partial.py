# SPDX-License-Identifier: MIT
"""Original fictional partial-response retention, retry and coverage checks."""

import json

import pytest
from test_context_review import answer, exchange, fake_job, long_source, proposal, request_ids, sdk_job

from gta_highlights import adapter, dialogue, review
from gta_highlights.detector import Config


@pytest.fixture(autouse=True)
def host_cache(monkeypatch, tmp_path):
    monkeypatch.setenv("CLIPS_KITTY_PLUGIN_CACHE_DIR", str(tmp_path / "host-cache"))
    monkeypatch.delenv("CLIPS_KITTY_PLUGIN_DEADLINE_MONOTONIC", raising=False)
    return tmp_path / "host-cache" / "dialogue-v2"


@pytest.mark.parametrize("bad_position", [0, 1, 2])
def test_bad_sibling_preserves_both_independently_grounded_exchanges(monkeypatch, host_cache, bad_position):
    rows = exchange()+exchange(25)
    proposals = [proposal(rows=rows), proposal(3, 4, 5, rows)]
    proposals.insert(bad_position, proposal(rows=rows, end_id="s999"))
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: answer(*proposals))
    job, notes = fake_job(), []
    budget = review.ReviewBudget(job)
    found = dialogue.find_dialogue(job, rows, 100, Config(), notes, budget)
    assert {(h.action_start, h.action_end) for h in found} == {(6, 22), (31, 47)}
    assert all(h.category == "funny_dialogue" and h.confidence == 0.55 for h in found)
    stats = budget.report()
    assert stats["validated_proposals"] == 2 and stats["partial_windows"] == 1
    assert stats["failed_windows"] == 1 and stats["reviewed_windows"] == 0
    assert stats["coverage_fraction"] == 0 and stats["validation_failures"] == {"source_ids": 1}
    assert list(host_cache.glob("*.json")) == []
    assert "source_ids=1" in notes[-1] and "1 partial" in notes[-1]


@pytest.mark.parametrize("bad,category", [
    ({"end_id": "s999"}, "source_ids"),
    ({"start_id": True}, "source_ids"),
    ({"start_id": "s1"}, "causal_order"),
    ({"category": "crash"}, "category_strength"),
    ({"strength": 3}, "category_strength"),
    ({"quote": "PRIVATE_INVALID_QUOTE_DO_NOT_LOG"}, "quote_grounding"),
    ({"execute": "PRIVATE_INVALID_INSTRUCTION_DO_NOT_LOG"}, "proposal_fields"),
])
def test_partial_acceptance_preserves_every_existing_source_check(monkeypatch, host_cache, bad, category):
    supplied = answer(proposal(), proposal(**bad))
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: supplied)
    job, notes = fake_job(), []
    budget = review.ReviewBudget(job)
    found = dialogue.find_dialogue(job, exchange(), 100, Config(), notes, budget)
    assert len(found) == 1
    assert budget.report()["validation_failures"] == {category: 1}
    assert budget.report()["partial_windows"] == 1
    assert list(host_cache.glob("*.json")) == []
    assert "PRIVATE_INVALID" not in json.dumps(budget.report())+" ".join(notes)


def test_partial_outcome_is_retried_then_only_fully_valid_outcome_is_cached(monkeypatch, host_cache):
    calls = []
    def ask(*_args, **_kwargs):
        calls.append(1)
        return answer(proposal(), proposal(quote="PRIVATE_INVALID_QUOTE_DO_NOT_LOG")) if len(calls) == 1 else answer(proposal())
    monkeypatch.setattr(dialogue.local_model, "ask", ask)
    job = fake_job()
    first_budget = review.ReviewBudget(job)
    first = dialogue.find_dialogue(job, exchange(), 100, Config(), [], first_budget)
    assert len(first) == 1 and first_budget.report()["partial_windows"] == 1
    assert list(host_cache.glob("*.json")) == []
    fresh_budget = review.ReviewBudget(job)
    fresh = dialogue.find_dialogue(job, exchange(), 100, Config(), [], fresh_budget)
    assert fresh == first and fresh_budget.report()["reviewed_windows"] == 1
    assert fresh_budget.report()["coverage_fraction"] == 1
    assert len(list(host_cache.glob("*.json"))) == 1
    cached_budget = review.ReviewBudget(job)
    assert dialogue.find_dialogue(job, exchange(), 100, Config(), [], cached_budget) == fresh
    assert len(calls) == 2 and cached_budget.report()["cache_hits"] == 1
    assert cached_budget.report()["validation_failures"] == {}


def test_all_invalid_response_is_retried_instead_of_becoming_cached_empty(monkeypatch, host_cache):
    calls = []
    def ask(*_args, **_kwargs):
        calls.append(1)
        return answer(proposal(end_id="s999"), proposal(quote="PRIVATE_INVALID_QUOTE_DO_NOT_LOG")) if len(calls) == 1 else answer()
    monkeypatch.setattr(dialogue.local_model, "ask", ask)
    job = fake_job()
    invalid_budget = review.ReviewBudget(job)
    assert dialogue.find_dialogue(job, exchange(), 100, Config(), [], invalid_budget) == []
    stats = invalid_budget.report()
    assert stats["partial_windows"] == stats["validated_proposals"] == stats["reviewed_windows"] == 0
    assert stats["failed_windows"] == 1 and stats["coverage_fraction"] == 0
    assert stats["validation_failures"] == {"source_ids": 1, "quote_grounding": 1}
    assert list(host_cache.glob("*.json")) == []
    empty_budget = review.ReviewBudget(job)
    assert dialogue.find_dialogue(job, exchange(), 100, Config(), [], empty_budget) == []
    assert empty_budget.report()["reviewed_windows"] == 1 and empty_budget.report()["coverage_fraction"] == 1
    assert len(list(host_cache.glob("*.json"))) == 1
    cached_budget = review.ReviewBudget(job)
    assert dialogue.find_dialogue(job, exchange(), 100, Config(), [], cached_budget) == []
    assert len(calls) == 2 and cached_budget.report()["cache_hits"] == 1


@pytest.mark.parametrize("malformation,category", [("json", "response_json"), ("envelope", "response_schema"),
                                                  ("duplicate", "response_schema"), ("excess", "response_schema"),
                                                  ("type", "response_format")])
def test_malformed_top_level_cannot_salvage_embedded_proposals(monkeypatch, host_cache, malformation, category):
    supplied = {
        "json": answer(proposal())[:-1],
        "envelope": json.dumps({"exchanges": [proposal()], "extra": "PRIVATE_INVALID_DATA_DO_NOT_LOG"}),
        "duplicate": '{"exchanges":['+json.dumps(proposal())+'],"exchanges":[]}',
        "excess": answer(*([proposal()]*7)),
        "type": None,
    }[malformation]
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: supplied)
    job = fake_job()
    budget = review.ReviewBudget(job)
    assert dialogue.find_dialogue(job, exchange(), 100, Config(), [], budget) == []
    assert budget.report()["validation_failures"] == {category: 1}
    assert budget.report()["partial_windows"] == budget.report()["validated_proposals"] == 0
    assert list(host_cache.glob("*.json")) == []


def test_invalid_items_are_counted_without_raw_response_logging(monkeypatch):
    supplied = answer(proposal(), proposal(quote="PRIVATE_INVALID_QUOTE_DO_NOT_LOG"),
                      proposal(quote="ANOTHER_PRIVATE_INVALID_QUOTE_DO_NOT_LOG"), None, "PRIVATE_INVALID_ENTRY_DO_NOT_LOG")
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: supplied)
    notes, job = [], fake_job()
    budget = review.ReviewBudget(job)
    assert len(dialogue.find_dialogue(job, exchange(), 100, Config(), notes, budget)) == 1
    assert budget.report()["validation_failures"] == {"quote_grounding": 2, "proposal_fields": 2}
    assert "quote_grounding=2" in notes[-1] and "proposal_fields=2" in notes[-1]
    assert "PRIVATE_INVALID" not in json.dumps(budget.report())+" ".join(notes)


def test_partial_and_failed_windows_reduce_full_coverage_without_discarding_grounded_proposal(monkeypatch):
    rows = long_source(70)
    def ask(_job, prompt, **_kwargs):
        first = request_ids(prompt)[0]
        if first == 0:
            return answer(proposal(0, 1, 2, rows), proposal(0, 1, 2, rows, end_id="s999"))
        return answer() if first == 56 else "PRIVATE_INVALID_NON_JSON_DO_NOT_LOG"
    monkeypatch.setattr(dialogue.local_model, "ask", ask)
    job, notes = fake_job(), []
    budget = review.ReviewBudget(job)
    found = dialogue.find_dialogue(job, rows, 250, Config(), notes, budget)
    stats = budget.report()
    assert len(found) == 1 and stats["validated_proposals"] == 1
    assert stats["reviewed_windows"] == 1 and stats["partial_windows"] == 1 and stats["failed_windows"] == 2
    assert stats["covered_segments"] == 14 and stats["coverage_fraction"] == 0.2
    assert stats["validation_failures"] == {"source_ids": 1, "response_json": 1}
    assert "PRIVATE_INVALID" not in " ".join(notes)


def test_partially_corrupted_cache_gets_fresh_validation_and_never_becomes_partial_hit(monkeypatch, host_cache):
    calls = []
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: calls.append(1) or answer(proposal()))
    job = fake_job()
    dialogue.find_dialogue(job, exchange(), 100, Config(), [])
    (path,) = list(host_cache.glob("*.json"))
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["answer"] = answer(proposal(), proposal(end_id="s999"))
    path.write_text(json.dumps(payload), encoding="utf-8")
    budget = review.ReviewBudget(job)
    assert len(dialogue.find_dialogue(job, exchange(), 100, Config(), [], budget)) == 1
    stats = budget.report()
    assert len(calls) == 2 and stats["invalid_cache_entries"] == 1 and stats["cache_hits"] == 0
    assert stats["cache_validation_failures"] == {"source_ids": 1}
    assert stats["validation_failures"] == {} and stats["partial_windows"] == 0
    assert stats["reviewed_windows"] == 1
    assert json.loads(path.read_text(encoding="utf-8"))["answer"] == answer(proposal())


def test_sdk_report_retains_valid_clip_and_explains_partial_coverage(tmp_path, monkeypatch):
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k:
                        answer(proposal(), proposal(quote="PRIVATE_INVALID_QUOTE_DO_NOT_LOG")))
    job = sdk_job(tmp_path, exchange())
    adapter.main(job)
    result = json.loads((job.folder / "result.json").read_text(encoding="utf-8"))
    report = json.loads((job.output_dir / "gta-highlight-explanations.json").read_text(encoding="utf-8"))
    (clip,) = result["ranges"]
    assert clip["start"] == 6 and clip["end"] == 22
    assert report["dialogue_review"]["validation_failures"] == {"quote_grounding": 1}
    assert report["dialogue_review"]["partial_windows"] == 1
    assert report["dialogue_review"]["coverage_fraction"] == 0
    assert "quote_grounding=1" in result["notes"]
    assert "PRIVATE_INVALID" not in json.dumps(result)+json.dumps(report)+job._out.getvalue()
