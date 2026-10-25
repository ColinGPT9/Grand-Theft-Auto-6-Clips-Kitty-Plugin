"""Run the actual detector and the explicit energy baseline on fixed inputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from clipskitty_sdk import signals

from gta_highlights import Config, Evidence, detect

from .baseline import detect_energy
from .metrics import aggregate, evaluate_case

FIXTURES = Path(__file__).with_name("fixtures") / "cases.json"


def load_cases(path: Path = FIXTURES) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def loudness_for(case: dict) -> list[float]:
    """Expand a compact one-sample-per-second, synthetic LUFS fixture."""
    if not case.get("media_available", True):
        return []
    values = [-42.0] * int(case["duration"])
    for pulse in case.get("audio_pulses", []):
        for second in range(int(pulse[0]), min(len(values), int(pulse[1]))):
            values[second] = float(pulse[2])
    return values


def evidence_for(case: dict) -> list[Evidence]:
    evidence = []
    for segment in case.get("transcript", []):
        evidence.append(Evidence(start=segment["start"], end=segment["end"], kind="transcript",
                                 text=segment["text"], source="authored_synthetic_transcript"))
    if case.get("media_available", True):
        # Derive low-level spike evidence from exactly the samples used by
        # the reference detector, rather than promoting every pulse by fiat.
        spikes = signals.spikes(loudness_for(case), louder_by=6.0)
        for start, last in signals.stretches(spikes, gap=2.0, min_length=0):
            evidence.append(Evidence(start=start, end=last + 1, kind="audio_spike", confidence=0.8,
                                     source="authored_synthetic_signal", verified=True))
        for at in case.get("scene_cuts", []):
            evidence.append(Evidence(start=at, end=at + 0.25, kind="video_scene_change", confidence=0.8,
                                     source="authored_synthetic_signal", verified=True))
    return evidence


def evaluate_fixtures(document: dict[str, Any], *, split: str = "all") -> dict[str, Any]:
    cases = [case for case in document["cases"] if split == "all" or case["split"] == split]
    outputs: dict[str, list[dict]] = {"energy_only_baseline": [], "gta_plugin": []}
    for case in cases:
        config = Config(**case.get("config", {}))
        actual = detect(evidence_for(case), duration=case["duration"], config=config)
        plugin = [{"start": item.start, "end": item.end, "category": item.category,
                   "score": item.score, "confidence": item.confidence, "reason": item.reason}
                  for item in actual]
        baseline = detect_energy(loudness_for(case), case["duration"])
        for name, predictions in (("energy_only_baseline", baseline), ("gta_plugin", plugin)):
            outputs[name].append({"case_id": case["id"], "split": case["split"],
                                  "description": case["description"], "predictions": predictions,
                                  "metrics": evaluate_case(predictions, case["events"])})
    return {"schema_version": 1, "fixture_set": document["name"], "split": split,
            "matching": {"minimum_temporal_iou": 0.25, "minimum_payoff_coverage": 0.5,
                         "complete_component_coverage": 0.8},
            "limitations": ["Original synthetic annotations and signals; no real GTA footage reviewed.",
                            "Baseline is an authored energy-only reference, not Clips Kitty's built-in finder.",
                            "Public holdout fixtures are regression checks, not a blind generalization claim.",
                            "No visual, audio, caption, watchability, or virality scores were assigned."],
            "manual_review": {"status": "not_performed", "reason": "No authorized real footage was reviewed.",
                              "visual_framing": None, "audio": None, "captions": None, "watchability": None},
            "detectors": {name: {"summary": aggregate(items), "cases": items}
                          for name, items in outputs.items()}}


def source_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((root / "src").rglob("*.py")):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def markdown_report(report: dict[str, Any]) -> str:
    def percent(value):
        return "n/a" if value is None else f"{value:.1%}"
    lines = ["# Synthetic regression evaluation", "", f"Run: {report.get('generated_at_utc', 'unsaved')}", "",
             "These results cover original synthetic signal/transcript fixtures, not real gameplay or audience performance.",
             "The energy-only baseline is original reference code, not Clips Kitty's built-in finder.", "",
             "| Detector | TP | FP | FN | Precision | Recall | Complete events | Duplicate rate |", 
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name, output in report["detectors"].items():
        m = output["summary"]
        lines.append(f"| {name} | {m['true_positives']} | {m['false_positives']} | {m['false_negatives']} | "
                     f"{percent(m['precision'])} | {percent(m['recall'])} | "
                     f"{percent(m['event_completeness_rate'])} | {percent(m['duplicate_rate'])} |")
    lines += ["", "Manual visual framing, audio, captions, and watchability review: **not performed**.", "",
              "See the JSON file for per-case predictions, match thresholds, provenance, and temporal coverage.", ""]
    return "\n".join(lines)
