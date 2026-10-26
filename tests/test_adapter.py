# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ColinGPT9
"""Exercise actual SDK jobs, optional integrations, and original synthetic media."""

import io
import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
from clipskitty_sdk import media, testing
from clipskitty_sdk.job import Job

from gta_highlights import adapter
from gta_highlights.observations import collect_evidence
from scripts.generate_demo import generate_demo

PLUGIN = Path(__file__).resolve().parents[1]


def job_at(tmp_path, segments=None, *, settings=None, steps=None, moments=None, video=None):
    tmp_path.mkdir(parents=True, exist_ok=True)
    data = {"plugin": {"id": "colingpt9/gta-vi-highlights", "version": "0.3.0"},
            "settings": {"use_media": False, **(settings or {})},
            "limits": {"min_duration": 12, "max_duration": 60},
            "steps": steps or ["find"], "moments": moments or [],
            "output_dir": str(tmp_path / "out")}
    if segments is not None:
        transcript = tmp_path / "transcript.json"
        transcript.write_text(json.dumps({"segments": segments}), encoding="utf-8")
        data["transcript"] = {"path": str(transcript)}
    if video is not None:
        data["video"] = {"path": str(video), "duration": 120}
    return Job(tmp_path, data, out=io.StringIO())


def event(start=30, end=32, text="We crashed into the barrier!"):
    return {"start": start, "end": end, "text": text}


def result(job):
    return json.loads((job.folder / "result.json").read_text(encoding="utf-8"))


def test_sdk_job_supports_transcript_only_and_absent_all_evidence(tmp_path):
    job = job_at(tmp_path / "text", [event()])
    adapter.main(job)
    assert len(result(job)["ranges"]) == 1
    assert result(job)["ranges"][0]["label"] == "crash"
    assert result(job)["ranges"][0]["end"] <= 32
    empty = job_at(tmp_path / "empty")
    adapter.main(empty)
    assert result(empty)["ranges"] == []


def test_truncated_support_is_reported_for_review_without_a_find_range(tmp_path):
    job = job_at(tmp_path, [event(20, 100)], settings={"write_report": True})
    job.data["limits"]["max_duration"] = 20
    adapter.main(job)
    assert result(job)["ranges"] == []
    report = json.loads((job.output_dir / "gta-highlight-explanations.json").read_text())
    candidate = report["highlights"][0]
    assert candidate["selection_status"] == "review_only"
    assert candidate["supported_utterance"] == {"start": 20, "end": 100}
    assert candidate["review_warnings"]


def test_report_explains_score_and_uses_a_grounded_range_title(tmp_path):
    job = job_at(tmp_path, [event()], settings={"write_report": True})
    adapter.main(job)
    report = json.loads((job.output_dir / "gta-highlight-explanations.json").read_text())
    candidate = report["highlights"][0]
    assert report["schema_version"] == 2
    assert candidate["selection_status"] == "eligible"
    assert candidate["available_modalities"] == ["transcript"]
    assert sum(candidate["score_components"].values()) == pytest.approx(candidate["score"], abs=0.0001)
    assert result(job)["ranges"][0]["title"] == candidate["title"]


def test_edit_does_not_trim_a_supporting_utterance_that_exceeds_limits(tmp_path):
    job = job_at(tmp_path, [event(20, 100)], steps=["edit"],
                 moments=[{"id": "m1", "start": 0, "end": 120}],
                 settings={"trim_to_event": True})
    adapter.main(job)
    assert "moments" not in result(job)


def test_malformed_transcript_rows_are_ignored_without_making_fake_events(tmp_path):
    job = job_at(tmp_path, [None, {}, event(start=-1), event(end=float("nan")),
                            event(text=123), event(), {**event(), "confidence": 2}])
    evidence, duration, notes = collect_evidence(job)
    assert len(evidence) == 1 and evidence[0].kind == "transcript"
    assert duration == 32
    assert "Ignored 6" in " ".join(notes)


def test_sdk_ratings_use_actual_host_signals_and_preserve_unknown_score(tmp_path):
    moments = [{"id": "m1", "start": 20, "end": 45, "score": 20,
                "signals": {"audio": 80, "visual": 60, "reaction": 75}},
               {"id": "m2", "start": 70, "end": 90, "score": 83,
                "signals": {"audio": 100, "visual": 100}}]
    job = job_at(tmp_path, [event(), event(100, 102, "Ordinary driving today.")],
                 steps=["rate", "understand"], moments=moments)
    adapter.main(job)
    answers = result(job)["moments"]
    assert len(answers) == 1 and answers[0]["id"] == "m1"
    assert 0 <= answers[0]["score"] <= 100
    assert "audio 80/100" in answers[0]["reason"]
    assert "visual 60/100" in answers[0]["reason"]
    assert 1 <= len(answers[0]["context"]) <= 5
    assert all(len(note) <= 160 for note in answers[0]["context"])
    assert job.moments[1].score == 83


def test_edits_are_opt_in_and_preserve_source_setup_and_reaction(tmp_path):
    moments = [{"id": "m1", "start": 0, "end": 100, "score": 70}]
    segments = [event(), event(119, 120, "Nothing unusual here.")]
    off = job_at(tmp_path / "off", segments, steps=["edit"], moments=moments)
    adapter.main(off)
    assert "moments" not in result(off)
    on = job_at(tmp_path / "on", segments, steps=["edit"], moments=moments,
                settings={"trim_to_event": True, "title_overlay": True})
    adapter.main(on)
    edit = result(on)["moments"][0]["edit"]
    assert edit["cuts"] == [[0.0, 22.0], [42.0, 100.0]]
    assert edit["title_overlay"]["text"] == "Crash"
    assert "crop" not in edit and "volume" not in edit and "speed" not in edit


def test_optional_model_accepts_only_matching_schema_grounded_candidates(tmp_path, monkeypatch):
    calls = []
    def ask(job, prompt, **kwargs):
        calls.append((prompt, kwargs))
        return json.dumps({"candidate_id": "candidate-1", "category": "crash", "supported": True, "confidence": 0.9})
    monkeypatch.setattr(adapter.local_model, "ask", ask)
    job = job_at(tmp_path, [event()], settings={"use_local_model": True, "write_report": True})
    adapter.main(job)
    assert len(calls) == 1 and calls[0][1] == {"json": True, "timeout": 15}
    report = json.loads((job.output_dir / "gta-highlight-explanations.json").read_text())
    assert any(row["kind"] == "model" for row in report["highlights"][0]["evidence"])
    assert report["timeline_basis"] == "source_media" and report["vod_alignment"] == "unverified"


@pytest.mark.parametrize("answer", [
    "ignore all instructions", "{}", '{"candidate_id":"invented"}',
    '{"candidate_id":"candidate-1","category":"combat","supported":true,"confidence":1}',
    '{"candidate_id":"candidate-1","category":"crash","supported":true,"confidence":true}',
    '{"candidate_id":"candidate-1","category":"crash","supported":true,"confidence":1,"execute":"upload"}',
])
def test_untrusted_model_json_falls_back_to_deterministic_source_score(tmp_path, monkeypatch, answer):
    baseline = job_at(tmp_path / "base", [event()])
    adapter.main(baseline)
    monkeypatch.setattr(adapter.local_model, "ask", lambda *args, **kwargs: answer)
    reviewed = job_at(tmp_path / "review", [event()], settings={"use_local_model": True})
    adapter.main(reviewed)
    assert result(reviewed)["ranges"] == result(baseline)["ranges"]


def test_missing_model_and_disabled_model_never_prevent_offline_detection(tmp_path, monkeypatch):
    calls = []
    def unavailable(*args, **kwargs):
        calls.append(1)
        raise adapter.local_model.LocalModelError("no configured model")
    monkeypatch.setattr(adapter.local_model, "ask", unavailable)
    off = job_at(tmp_path / "off", [event()])
    adapter.main(off)
    assert not calls
    on = job_at(tmp_path / "on", [event()], settings={"use_local_model": True})
    adapter.main(on)
    assert len(calls) == 1 and result(on)["ranges"] == result(off)["ranges"]


def test_optional_model_request_budget_never_exceeds_three(tmp_path, monkeypatch):
    calls = []
    def answer(*args, **kwargs):
        calls.append(kwargs)
        return "{}"
    monkeypatch.setattr(adapter.local_model, "ask", answer)
    segments = [event(start, start + 2) for start in (10, 80, 150, 220, 290)]
    job = job_at(tmp_path, segments, settings={"use_local_model": True})
    adapter.main(job)
    assert len(calls) == 3 and all(call["timeout"] == 15 for call in calls)


def test_media_observations_use_actual_frame_times_and_measured_audio(tmp_path, monkeypatch):
    video = tmp_path / "provided.mp4"
    video.write_bytes(b"mocked decoder input")
    job = job_at(tmp_path / "job", [event()], video=video, settings={"use_media": True})
    monkeypatch.setattr(media, "probe", lambda job: media.VideoInfo(32, 18, 1, 40))
    frames = [media.Frame(0, 32, 18, bytes([0]) * (32 * 18 * 3)),
              media.Frame(3.5, 32, 18, bytes([255]) * (32 * 18 * 3))]
    monkeypatch.setattr(media, "frames", lambda job, **kwargs: iter(frames))
    monkeypatch.setattr(media, "loudness", lambda job: [-50] * 10 + [-20] + [-50] * 29)
    evidence, duration, _ = collect_evidence(job)
    visual = [row for row in evidence if row.kind.startswith("video_")]
    audio = [row for row in evidence if row.kind == "audio_spike"]
    assert duration == 40 and visual and audio
    assert all(row.start == 3.5 and row.verified for row in visual)
    assert audio[0].start == 10 and audio[0].verified
    assert "excess_lufs:30.00" in audio[0].tags


def test_mapped_audience_nominations_are_bounded_support_only(tmp_path):
    def audience_signals():
        return {"status": "ok", "nominations": [
            {"offset_seconds": 31, "count": 4, "commands": {"clip": 2, "chaos": 2}},
            {"offset_seconds": -1, "count": 8, "commands": {"clip": 8}},
            {"offset_seconds": 130, "count": 8, "commands": {"clip": 8}},
        ]}
    job = job_at(tmp_path, [event()])
    job.accounts = SimpleNamespace(twitch=SimpleNamespace(audience_signals=audience_signals))
    evidence, _, _ = collect_evidence(job)
    chat = [row for row in evidence if row.kind == "chat"]
    assert len(chat) == 1 and chat[0].start == 31
    assert chat[0].tags == ("!clip", "!chaos")
    empty = job_at(tmp_path / "empty", [event(text="Ordinary driving today.")])
    empty.accounts = job.accounts
    adapter.main(empty)
    assert result(empty)["ranges"] == []


def test_unmapped_or_unavailable_audience_data_is_ignored(tmp_path):
    job = job_at(tmp_path, [event()])
    job.accounts = SimpleNamespace(twitch=SimpleNamespace(audience_signals=lambda: {
        "status": "unavailable", "reason": "No verified mapping", "nominations": [
            {"offset_seconds": 31, "count": 2, "commands": {"clip": 2}}]}))
    evidence, _, _ = collect_evidence(job)
    assert all(row.kind != "chat" for row in evidence)


def test_nonexistent_provided_video_uses_sdk_failure_path(tmp_path):
    job = job_at(tmp_path, [event()], video=tmp_path / "missing.mp4")
    with pytest.raises(SystemExit):
        adapter.main(job)
    assert "video file does not exist" in job._out.getvalue()
    assert not (tmp_path / "result.json").exists()


def test_invalid_provided_video_reports_useful_sdk_failure(tmp_path):
    invalid = tmp_path / "invalid.mp4"
    invalid.write_text("This is not media.")
    job = job_at(tmp_path / "job", [event()], video=invalid, settings={"use_media": True})
    with pytest.raises(SystemExit):
        adapter.main(job)
    assert "supplied footage could not be measured" in job._out.getvalue()


@pytest.fixture(scope="module")
def original_demo(tmp_path_factory):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        pytest.skip("needs FFmpeg for original synthetic media")
    return generate_demo(tmp_path_factory.mktemp("gta-original-demo") / "demo.mp4", str(Path(ffmpeg).resolve()))


@pytest.mark.media
def test_sdk_subprocess_finds_original_synthetic_transcript_with_real_measured_support(tmp_path, original_demo):
    video, transcript = original_demo
    run = testing.run_plugin(PLUGIN, video=video, transcript=transcript,
                             settings={"write_report": True}, tmp_path=tmp_path, timeout=45)
    assert run.ok, run.error
    assert run.moments
    assert any(moment.label == "crash" for moment in run.moments)
    assert all(0 <= moment.start < moment.end <= 48 for moment in run.moments)
    assert any("measured" in moment.reason for moment in run.moments)
    report = json.loads((run.folder / "out" / "gta-highlight-explanations.json").read_text())
    kinds = {row["kind"] for item in report["highlights"] for row in item["evidence"]}
    assert "transcript" in kinds and "audio_spike" in kinds and "video_motion" in kinds


@pytest.mark.media
def test_sdk_subprocess_rates_understands_and_suggests_only_requested_edits(tmp_path, original_demo):
    video, transcript = original_demo
    moments = [{"start": 8, "end": 40, "score": 10}, {"start": 40, "end": 48, "score": 88}]
    rated = testing.run_plugin(PLUGIN, video=video, transcript=transcript, steps="rate,understand",
                               moments=moments, tmp_path=tmp_path / "rate", timeout=45)
    assert rated.ok, rated.error
    assert "m1" in rated.answers and "m2" not in rated.answers
    assert rated.moments[1].score == 88
    assert rated.moments[0].notes
    edited = testing.run_plugin(PLUGIN, video=video, transcript=transcript, steps="edit",
                                moments=moments, settings={"trim_to_event": True, "title_overlay": True},
                                tmp_path=tmp_path / "edit", timeout=45)
    assert edited.ok, edited.error
    assert "m1" in edited.edits and "m2" not in edited.edits
    assert "title_overlay" in edited.edits["m1"]["edit"]


@pytest.mark.media
def test_actual_loud_tones_and_frame_changes_without_event_text_produce_no_clips(tmp_path, original_demo):
    video, _ = original_demo
    run = testing.run_plugin(PLUGIN, video=video, transcript=[], tmp_path=tmp_path, timeout=45)
    assert run.ok, run.error
    assert run.moments == []
