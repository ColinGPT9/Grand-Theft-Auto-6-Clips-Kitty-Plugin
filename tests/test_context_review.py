# SPDX-License-Identifier: MIT
"""Original fictional context, coverage, reliability and nomination regressions."""

import io
import json
import os
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest
from clipskitty_sdk.job import Job

from gta_highlights import adapter, dialogue, review
from gta_highlights.detector import Config, detect
from gta_highlights.observations import collect_evidence
from gta_highlights.scoring import Evidence
from gta_highlights.selection import nomination_candidates, select_highlights


def speech(start, end, text):
    return Evidence(start, end, "transcript", text=text, source="original fictional transcript")


def exchange(offset=0):
    return [speech(offset+6, offset+10, "Crew navigator: Why is the receipt wearing a helmet?"),
            speech(offset+11, offset+18, "That is our accountant, and he charges by the crash."),
            speech(offset+19, offset+22, "Then please ask him to stop billing the parking meter.")]


def proposal(first=0, payoff=1, last=2, rows=None, **patch):
    rows = rows or exchange()
    return {"start_id": f"s{first}", "payoff_id": f"s{payoff}", "end_id": f"s{last}",
            "quote": rows[payoff].text, "category": "funny_dialogue", "strength": 5, **patch}


def answer(*proposals):
    return json.dumps({"exchanges": list(proposals)})


def long_source(n=150):
    return [speech(i*3, i*3+2, f"Crew member {i}: Why does the accountant charge parking meters?") for i in range(n)]


def request_ids(prompt):
    return [int(row["id"][1:]) for row in json.loads(prompt.split("Source segments: ", 1)[1])]


def fake_job(settings=None, model="fictional-override"):
    return SimpleNamespace(settings=settings or {}, tools=SimpleNamespace(ollama={"model": model, "host": "localhost"}))


def sdk_job(tmp_path, rows, settings=None, steps=None):
    tmp_path.mkdir(parents=True, exist_ok=True)
    transcript = tmp_path / "transcript.json"
    transcript.write_text(json.dumps({"segments": [{"start": r.start, "end": r.end, "text": r.text} for r in rows]}), encoding="utf-8")
    return Job(tmp_path, {"plugin": {"id": "colingpt9/gta-vi-highlights", "version": "0.5.0"},
                          "transcript": {"path": str(transcript)}, "steps": steps or ["find"],
                          "settings": {"use_media": False, "use_local_model": True, "write_report": True, **(settings or {})},
                          "limits": {"min_duration": 0, "max_duration": 90}}, out=io.StringIO())


@pytest.fixture(autouse=True)
def isolated_cache(monkeypatch, tmp_path):
    monkeypatch.setenv("CLIPS_KITTY_PLUGIN_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.delenv("CLIPS_KITTY_PLUGIN_DEADLINE_MONOTONIC", raising=False)


def test_joint_discovery_does_not_let_generic_reaction_suppress_quiet_roleplay(tmp_path, monkeypatch):
    rows = [speech(1, 3, "Oh my goodness!")] + exchange(40)
    def ask(_job, prompt, **_kwargs):
        if "Candidate JSON:" in prompt:
            return "{}"
        return answer(proposal(1, 2, 3, rows, category="roleplay"))
    monkeypatch.setattr(dialogue.local_model, "ask", ask)
    job = sdk_job(tmp_path, rows, {"max_highlights": 1})
    adapter.main(job)
    result = json.loads((job.folder / "result.json").read_text(encoding="utf-8"))
    (clip,) = result["ranges"]
    assert clip["label"] == "roleplay"
    assert (clip["start"], clip["end"]) == (46, 62)
    report = json.loads((job.output_dir / "gta-highlight-explanations.json").read_text(encoding="utf-8"))
    assert report["dialogue_review"]["coverage_fraction"] == 1


def test_tight_budget_discovers_dialogue_before_corroborating_known_reaction(tmp_path, monkeypatch):
    clock = SimpleNamespace(now=100.0)
    monkeypatch.setattr(review.time, "monotonic", lambda: clock.now)
    rows = [speech(1, 3, "Oh my goodness!")] + exchange(40)
    calls = []
    def ask(_job, prompt, **kwargs):
        calls.append(prompt)
        assert "Source segments:" in prompt
        clock.now += kwargs["timeout"]
        return answer(proposal(1, 2, 3, rows, category="roleplay"))
    monkeypatch.setattr(dialogue.local_model, "ask", ask)
    job = sdk_job(tmp_path, rows, {"dialogue_review_minutes": 0.25, "max_highlights": 1})
    adapter.main(job)
    (clip,) = json.loads((job.folder / "result.json").read_text(encoding="utf-8"))["ranges"]
    assert len(calls) == 1 and clip["label"] == "roleplay"


def test_setup_action_reaction_end_before_sustained_idle_and_unrelated_topic(monkeypatch):
    rows = [speech(6, 10, "Why are you aiming at the empty barrier?"),
            speech(11, 18, "We crashed into the barrier!"), speech(19, 22, "Oh my goodness!"),
            speech(25, 43, "Just waiting in the loading screen."),
            speech(49, 55, "Crew member: Who ate the receipt?"),
            speech(56, 61, "The accountant said it was a paper lunch."),
            speech(62, 64, "Please put the menu down before he gets dessert.")]
    deterministic = detect(rows, 90, Config(min_duration=0))
    crash = next(h for h in deterministic if h.category == "crash")
    assert (crash.start, crash.end) == (6, 22)
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: answer(
        proposal(0, 1, 6, rows)))
    assert dialogue.find_dialogue(fake_job(), rows, 90, Config(min_duration=0, max_duration=90), []) == []


def test_midconversation_question_begins_concise_complete_exchange(monkeypatch):
    rows = [speech(1, 12, "Our crew has been discussing lunch and routes."),
            speech(13, 24, "The bridge schedule takes a long time to read."), *exchange(25)]
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: answer(proposal(2, 3, 4, rows)))
    (clip,) = dialogue.find_dialogue(fake_job(), rows, 100, Config(min_duration=0), [])
    assert (clip.start, clip.end) == (31, 47)
    assert clip.start < rows[3].start and clip.end == rows[4].end


def test_short_complete_action_is_alternative_to_long_dialogue_with_accurate_title():
    rows = [speech(5, 10, "Crew inspector: Who signed this receipt?"),
            speech(35, 38, "We crashed into the paper delivery truck!"),
            speech(39, 42, "Oh my goodness!")]
    action = detect(rows, 100, Config(min_duration=0))[0]
    broad = replace(action, start=5, end=70, action_start=5, action_end=70,
                    category="roleplay", score=action.score-0.01, title="GTA dialogue exchange")
    selected = select_highlights([broad, action], 10)
    assert len(selected) == 1 and selected[0].start == action.start and selected[0].end == action.end
    assert "Preferred complete crash alternative" in selected[0].suppressed_reasons[-1]
    assert selected[0].title == "Vehicle incident"


def test_full_pipeline_prefers_short_action_inside_long_conversation_with_its_own_title(tmp_path, monkeypatch):
    rows = [speech(5, 10, "Crew inspector: Who signed the accountant's permit?"),
            speech(11, 20, "The permit lists every sandwich that has left the office."),
            speech(21, 28, "Please keep the receipt flat while I read it."),
            speech(29, 32, "We crashed into the paper delivery truck!"),
            speech(33, 36, "Oh my goodness!"),
            speech(37, 46, "The permit has now become a parking ticket for the sandwich."),
            speech(47, 54, "Then the sandwich will have to appeal to the lunch court.")]
    def ask(_job, prompt, **_kwargs):
        return "{}" if "Candidate JSON:" in prompt else answer(proposal(0, 5, 6, rows, category="roleplay"))
    monkeypatch.setattr(dialogue.local_model, "ask", ask)
    job = sdk_job(tmp_path, rows)
    adapter.main(job)
    (clip,) = json.loads((job.folder / "result.json").read_text(encoding="utf-8"))["ranges"]
    assert clip["label"] == "crash" and clip["title"] == "Vehicle incident"
    assert clip["end"]-clip["start"] <= 40 and clip["end"] == 36


@pytest.mark.parametrize("duration,turns,expected", [(8, 3, 1), (46, 5, 1), (65, 6, 1), (65, 3, 0)])
def test_preferred_duration_is_not_a_minimum_or_hard_cut(monkeypatch, duration, turns, expected):
    step = duration/turns
    rows = [speech(5+i*step, 5+(i+1)*step, f"Crew member {i}: The receipt has changed its lunch order again.")
            for i in range(turns)]
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k:
                        answer(proposal(0, turns-2, turns-1, rows)))
    found = dialogue.find_dialogue(fake_job(), rows, 100, Config(min_duration=0, max_duration=90), [])
    assert len(found) == expected
    if found:
        assert found[0].end-found[0].start == pytest.approx(duration)
        if duration > 60:
            assert any("Exceptional duration retains setup" in warning for warning in found[0].review_warnings)


def test_complete_response_beats_clipped_short_alternative():
    complete = detect([speech(10, 18, "We crashed into the barrier!"),
                       speech(19, 22, "Oh my goodness!")], 100, Config(min_duration=0))[0]
    clipped = replace(complete, end=20, score=1.0)
    selected = select_highlights([clipped, complete], 1)
    assert selected[0].end == 22


def test_grammatically_split_response_is_kept_complete(monkeypatch):
    rows = exchange()
    rows[2] = speech(19, 22, "I cannot accept that receipt because")
    rows.append(speech(22.5, 25, "it has already been eaten by the accountant."))
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: answer(proposal(rows=rows)))
    (clip,) = dialogue.find_dialogue(fake_job(), rows, 100, Config(min_duration=0), [])
    assert clip.action_end == 25 and clip.end == 25


@pytest.mark.parametrize("gap, expected", [(3, 1), (11.9, 1), (12, 0), (20, 0)])
def test_brief_fades_do_not_split_but_sustained_ungrounded_gap_does(monkeypatch, gap, expected):
    rows = exchange()
    rows[2] = speech(rows[1].end+gap, rows[1].end+gap+3, rows[2].text)
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: answer(proposal(rows=rows)))
    assert len(dialogue.find_dialogue(fake_job(), rows, 100, Config(min_duration=0), [])) == expected


def test_visually_quiet_source_speech_needs_no_loud_or_motion_evidence(monkeypatch):
    rows = exchange()
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: answer(proposal(rows=rows)))
    (clip,) = dialogue.find_dialogue(fake_job(), rows, 100, Config(min_duration=0), [])
    assert clip.available_modalities == ("transcript", "model")


def test_crew_number_and_fictional_identity_accusation_stay_neutral(monkeypatch):
    rows = [speech(2, 6, "Crew Forty-One asked whether you are the inspector."),
            speech(7, 10, "I inspect sandwiches, and this one has no permit."),
            speech(11, 14, "Then please issue the tomato a written warning.")]
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: answer(proposal(rows=rows, category="roleplay")))
    (clip,) = dialogue.find_dialogue(fake_job(), rows, 40, Config(roleplay_enabled=True), [])
    assert clip.category == "roleplay" and clip.title == "GTA dialogue exchange"
    assert "police" not in clip.title.casefold() and "41" not in clip.reason
    assert "battle" not in clip.reason and "damage" not in clip.reason


def test_every_early_middle_late_window_is_reviewed_without_output_quota(monkeypatch):
    source = long_source(150)
    reviewed = []
    def ask(_job, prompt, **kwargs):
        ids = request_ids(prompt)
        reviewed.append(ids)
        assert kwargs == {"json": True, "timeout": 15}
        return answer(proposal(ids[0], ids[1], ids[2], source))
    monkeypatch.setattr(dialogue.local_model, "ask", ask)
    budget = review.ReviewBudget(fake_job())
    found = dialogue.find_dialogue(fake_job(), source, 500, Config(max_highlights=1), [], budget)
    assert len(reviewed) == 6 and len(found) == 6
    assert sorted(ids[0] for ids in reviewed) == [0, 28, 56, 84, 112, 140]
    assert set().union(*(set(ids) for ids in reviewed)) == set(range(150))
    assert budget.report()["coverage_fraction"] == 1
    assert not budget.report()["budget_exhausted"]


def test_mapped_nominations_then_measured_activity_prioritize_review(monkeypatch):
    source = long_source(100)
    signals = [Evidence(265, 265, "chat", text="clip that", tags=("count:1",),
                        source="host-mapped audience signals", verified=True),
               Evidence(126, 126, "audio_spike", verified=True)]
    reviewed = []
    monkeypatch.setattr(dialogue.local_model, "ask", lambda _j, prompt, **_k:
                        reviewed.append(request_ids(prompt)) or answer())
    dialogue.find_dialogue(fake_job(), source+signals, 320, Config(), [])
    assert reviewed[0][0] == 84 and reviewed[1][0] == 28
    assert len(reviewed) == 4


def test_overlapping_window_proposals_deduplicate_by_source_incident(monkeypatch):
    source = long_source(70)
    def ask(_job, prompt, **_kwargs):
        ids = request_ids(prompt)
        return answer(proposal(28, 29, 30, source)) if {28, 29, 30} <= set(ids) else answer()
    monkeypatch.setattr(dialogue.local_model, "ask", ask)
    found = dialogue.find_dialogue(fake_job(), source, 250, Config(), [])
    assert len(found) == 2
    selected = select_highlights(found, 10)
    assert len(selected) == 1 and selected[0].suppressed_reasons


def test_exhausted_budget_reports_partial_coverage_and_bounds_each_call(monkeypatch):
    clock = SimpleNamespace(now=100.0)
    monkeypatch.setattr(review.time, "monotonic", lambda: clock.now)
    job = fake_job({"dialogue_review_minutes": 0.5})
    source = long_source(150)
    timeouts = []
    def ask(_job, _prompt, **kwargs):
        timeouts.append(kwargs["timeout"])
        clock.now += kwargs["timeout"]
        return answer()
    monkeypatch.setattr(dialogue.local_model, "ask", ask)
    budget = review.ReviewBudget(job)
    dialogue.find_dialogue(job, source, 500, Config(), [], budget)
    stats = budget.report()
    assert timeouts == [15, 15]
    assert stats["reviewed_windows"] == 2 and stats["coverage_fraction"] < 1
    assert stats["elapsed_seconds"] == 30 and stats["budget_exhausted"]


def test_host_deadline_and_manifest_budget_are_bounded(monkeypatch):
    monkeypatch.setattr(review.time, "monotonic", lambda: 100.0)
    job = fake_job()
    monkeypatch.setenv("CLIPS_KITTY_PLUGIN_DEADLINE_MONOTONIC", "112")
    budget = review.ReviewBudget(job, invocation_started=0)
    assert budget.timeout() == 7
    assert budget.report()["deadline_basis"] == "host_monotonic_deadline"
    monkeypatch.delenv("CLIPS_KITTY_PLUGIN_DEADLINE_MONOTONIC")
    late = review.ReviewBudget(fake_job(), invocation_started=-1700)
    assert late.timeout() is None


@pytest.mark.parametrize("capability", [None, "", "NaN", "inf", "-30", "0", "invalid"])
def test_missing_or_invalid_host_deadline_preserves_manifest_fallback(monkeypatch, capability):
    monkeypatch.setattr(review.time, "monotonic", lambda: 100.0)
    if capability is None:
        monkeypatch.delenv("CLIPS_KITTY_PLUGIN_DEADLINE_MONOTONIC", raising=False)
    else:
        monkeypatch.setenv("CLIPS_KITTY_PLUGIN_DEADLINE_MONOTONIC", capability)
    budget = review.ReviewBudget(fake_job())
    assert budget.timeout() == 15
    assert budget.report()["deadline_basis"] == "manifest_30_minutes_with_reserve"


@pytest.mark.parametrize("value", [-1, 21, True, float("nan")])
def test_review_budget_setting_is_validated(value):
    with pytest.raises(ValueError):
        review.ReviewBudget(fake_job({"dialogue_review_minutes": value}))


def test_zero_budget_disables_requests_and_keeps_deterministic_findings(tmp_path, monkeypatch):
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: pytest.fail("zero review budget"))
    job = sdk_job(tmp_path, [speech(10, 12, "We crashed into the barrier!")]+exchange(20),
                  {"dialogue_review_minutes": 0})
    adapter.main(job)
    payload = json.loads((job.folder / "result.json").read_text(encoding="utf-8"))
    assert any(row["label"] == "crash" for row in payload["ranges"])
    report = json.loads((job.output_dir / "gta-highlight-explanations.json").read_text(encoding="utf-8"))
    assert report["dialogue_review"]["budget_exhausted"]


def test_valid_empty_and_successful_outcomes_cache_with_fresh_equivalence(monkeypatch):
    source = long_source(70)
    calls = []
    def ask(job, prompt, **_kwargs):
        assert job.tools.ollama["model"] == "fictional-override"
        ids = request_ids(prompt)
        calls.append(ids)
        return answer(proposal(ids[0], ids[1], ids[2], source)) if ids[0] == 28 else answer()
    monkeypatch.setattr(dialogue.local_model, "ask", ask)
    job = fake_job()
    fresh_budget = review.ReviewBudget(job)
    fresh = dialogue.find_dialogue(job, source, 250, Config(), [], fresh_budget)
    cached_budget = review.ReviewBudget(job)
    cached = dialogue.find_dialogue(job, source, 250, Config(), [], cached_budget)
    assert fresh == cached and len(fresh) == 1 and len(calls) == 3
    assert fresh_budget.report()["cache_misses"] == 3
    assert cached_budget.report()["cache_hits"] == 3 and cached_budget.report()["coverage_fraction"] == 1


@pytest.mark.parametrize("failure", ["invalid", "timeout", "wrong_id", "wrong_quote", "late"])
def test_invalid_or_transient_outcome_is_retried_not_permanently_empty(monkeypatch, failure):
    clock = SimpleNamespace(now=100.0)
    monkeypatch.setattr(review.time, "monotonic", lambda: clock.now)
    calls = []
    def ask(_job, _prompt, **_kwargs):
        calls.append(1)
        if len(calls) > 1:
            return answer(proposal())
        if failure == "timeout":
            raise dialogue.local_model.LocalModelError("fictional timeout")
        if failure == "late":
            clock.now += 16
            return answer(proposal())
        if failure == "wrong_id":
            return answer(proposal(end_id="s900"))
        if failure == "wrong_quote":
            return answer(proposal(quote="Nobody supplied these invented words."))
        return "not JSON"
    monkeypatch.setattr(dialogue.local_model, "ask", ask)
    job = fake_job()
    assert not dialogue.find_dialogue(job, exchange(), 100, Config(), [])
    assert len(dialogue.find_dialogue(job, exchange(), 100, Config(), [])) == 1
    assert len(calls) == 2


@pytest.mark.parametrize("change", ["transcript", "timestamp", "model", "setting", "schema"])
def test_cache_key_tracks_source_effective_model_settings_and_schema(monkeypatch, change):
    calls = []
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: calls.append(1) or answer())
    job, source = fake_job(), exchange()
    dialogue.find_dialogue(job, source, 100, Config(), [])
    if change == "transcript":
        source[0] = replace(source[0], text=source[0].text+" Additional source word.")
    elif change == "timestamp":
        source[0] = replace(source[0], start=5.5)
    elif change == "model":
        job.tools.ollama["model"] = "another-fictional-override"
    elif change == "setting":
        job.settings["roleplay_enabled"] = False
    else:
        monkeypatch.setattr(review, "SCHEMA_VERSION", "fictional-next-schema")
    dialogue.find_dialogue(job, source, 100, Config(), [])
    assert len(calls) == 2


def test_corrupted_cached_response_gets_a_fresh_request(monkeypatch):
    calls = []
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: calls.append(1) or answer())
    job = fake_job()
    dialogue.find_dialogue(job, exchange(), 100, Config(), [])
    (path,) = list((Path(os.environ["CLIPS_KITTY_PLUGIN_CACHE_DIR"])/"dialogue-v2").glob("*.json"))
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["answer"] = answer(proposal(end_id="s999"))
    path.write_text(json.dumps(payload), encoding="utf-8")
    budget = review.ReviewBudget(job)
    dialogue.find_dialogue(job, exchange(), 100, Config(), [], budget)
    assert len(calls) == 2 and budget.report()["invalid_cache_entries"] == 1


def test_missing_host_cache_capability_never_writes_plugin_installation_tree(monkeypatch):
    monkeypatch.delenv("CLIPS_KITTY_PLUGIN_CACHE_DIR")
    monkeypatch.setattr(review, "write_cache", lambda *_a, **_k: pytest.fail("no host cache write capability"))
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: answer(proposal()))
    job, notes = fake_job(), []
    budget = review.ReviewBudget(job)
    assert len(dialogue.find_dialogue(job, exchange(), 100, Config(), notes, budget)) == 1
    assert review.cache_directory() is None
    assert budget.report()["persistent_cache_available"] is False
    assert any("Persistent dialogue caching is disabled" in note for note in notes)
    assert detect([speech(10, 12, "We crashed into a barrier!")], 100)


def test_deep_invalid_json_cannot_break_optional_fallback(monkeypatch):
    nested = '{"exchanges":'+"["*1500+"]"*1500+"}"
    monkeypatch.setattr(dialogue.local_model, "ask", lambda *_a, **_k: nested)
    job = fake_job()
    budget = review.ReviewBudget(job)
    assert dialogue.find_dialogue(job, exchange(), 100, Config(), [], budget) == []
    assert budget.report()["failed_windows"] == 1


def test_relative_cache_capability_is_not_resolved_inside_installation(monkeypatch):
    monkeypatch.setenv("CLIPS_KITTY_PLUGIN_CACHE_DIR", ".clipskitty/cache")
    assert review.cache_directory() is None


def mapped(start=31, count=2):
    return Evidence(start, start, "chat", text="clip that (mapped audience nomination)",
                    tags=(f"count:{count}",), source="host-mapped audience signals", verified=True)


@pytest.mark.parametrize("count,kind,activity_time,verified,expected", [
    (1, "audio_spike", 31, True, 0), (2, "audio_spike", 31, True, 1),
    (2, "video_motion", 39.9, True, 1), (2, "video_scene_change", 31, True, 0),
    (2, "audio_spike", 40, True, 0), (2, "video_motion", 29.9, True, 0),
    (2, "video_motion", 31, False, 0), (2, "video_color_change", 31, True, 0),
])
def test_neutral_nominations_require_two_and_coincident_verified_audio_or_motion(
        count, kind, activity_time, verified, expected):
    rows = [mapped(count=count), Evidence(activity_time, activity_time, kind, verified=verified)]
    found = nomination_candidates(rows, 100, Config())
    assert len(found) == expected
    if found:
        assert found[0].category == "viewer_nominated" and found[0].title == "Viewer nominated moment"
        assert "event identity is unknown" in found[0].reason


def test_unmapped_or_arbitrary_chat_cannot_create_nomination_event():
    activity = Evidence(31, 31, "video_motion", verified=True)
    assert not nomination_candidates([replace(mapped(), verified=False), activity], 100, Config())
    assert not nomination_candidates([replace(mapped(), source="unmapped chat"), activity], 100, Config())
    assert not nomination_candidates([mapped()], 100, Config())


def test_two_single_mapped_nominations_in_same_bucket_aggregate_without_identity():
    rows = [mapped(31, 1), mapped(35, 1), Evidence(37, 37, "audio_spike", verified=True)]
    (clip,) = nomination_candidates(rows, 100, Config())
    assert clip.reason.startswith("2 mapped viewer nominations")
    assert not nomination_candidates([mapped(31, 1)]*2+rows[2:], 100, Config())


def test_source_supported_event_ranks_ahead_of_neutral_nomination():
    source = detect([speech(70, 72, "We crashed into a barrier!")], 100)[0]
    nominated = nomination_candidates([mapped(), Evidence(31, 31, "video_motion", verified=True)], 100, Config())[0]
    nominated = replace(nominated, score=1.0)
    assert select_highlights([nominated, source], 1) == [source]


def test_source_and_nomination_alternatives_are_not_duplicate_outputs():
    rows = [speech(31, 35, "We crashed into a barrier!"), mapped(),
            Evidence(32, 32, "video_motion", verified=True)]
    selected = select_highlights(detect(rows, 100)+nomination_candidates(rows, 100, Config()), 10)
    assert len(selected) == 1 and selected[0].category == "crash"


def test_joint_selection_preserves_separate_explicit_actions_despite_overlapping_asr(tmp_path):
    rows = [speech(30, 35, "We crashed into the red barrier!"),
            speech(31, 36, "That car just flipped behind the barrier!")]
    job = sdk_job(tmp_path, rows, {"use_local_model": False})
    adapter.main(job)
    clips = json.loads((job.folder / "result.json").read_text(encoding="utf-8"))["ranges"]
    assert len(clips) == 2


@pytest.mark.parametrize("status,enabled,expected", [("mapped", True, 1), ("ok", True, 1),
                                                     ("unavailable", True, 0), ("mapped", False, 0)])
def test_only_host_permitted_mapped_context_is_read(tmp_path, status, enabled, expected):
    job = sdk_job(tmp_path, [speech(90, 95, "Ordinary quiet commentary.")],
                  {"use_nominations": enabled, "use_local_model": False})
    calls = []
    def audience():
        calls.append(1)
        return {"status": status, "nominations": [{"offset_seconds": 31, "count": 2,
                                                     "commands": {"clip": 2}, "user": "ignored-fictional-user"}]}
    job.accounts = SimpleNamespace(twitch=SimpleNamespace(audience_signals=audience))
    rows, _, _ = collect_evidence(job)
    assert len([r for r in rows if r.kind == "chat"]) == expected
    assert len(calls) == int(enabled)
    assert "ignored-fictional-user" not in repr(rows)


def test_disabled_nominations_do_not_add_neutral_candidates(tmp_path, monkeypatch):
    rows = [speech(90, 95, "Ordinary quiet commentary."), mapped(), Evidence(31, 31, "video_motion", verified=True)]
    monkeypatch.setattr(adapter, "collect_evidence", lambda _j: (rows, 100, []))
    job = sdk_job(tmp_path, rows[:1], {"use_nominations": False, "use_local_model": False})
    adapter.main(job)
    assert json.loads((job.folder / "result.json").read_text(encoding="utf-8"))["ranges"] == []
