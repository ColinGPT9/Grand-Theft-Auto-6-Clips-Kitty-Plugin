# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ColinGPT9
"""Frozen original adversarial checks; metadata regression, never video accuracy."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from gta_highlights import Config, Evidence, detect

FIXTURES = Path(__file__).with_name("fixtures") / "quality_cases.json"


def evaluate(document=None):
    document = document or json.loads(FIXTURES.read_text(encoding="utf-8"))
    results = []
    for case in document["cases"]:
        rows = [Evidence(**row) for row in case["evidence"]]
        found = detect(rows, case["duration"], Config(**case.get("config", {})))
        expected = case["expected"]
        checks = {"count": len(found) == expected["count"]}
        checks["valid_limits"] = all(0 <= h.start < h.end <= case["duration"]
                                     and h.end - h.start <= case.get("config", {}).get("max_duration", 60)
                                     for h in found)
        if "categories" in expected:
            checks["categories"] = sorted(h.category for h in found) == sorted(expected["categories"])
        if "contains" in expected:
            checks["complete_required_interval"] = any(h.start <= expected["contains"][0]
                                                       and h.end >= expected["contains"][1] for h in found)
        if "action" in expected:
            checks["action_provenance"] = any((getattr(h, "action_start", None), getattr(h, "action_end", None))
                                               == tuple(expected["action"]) for h in found)
        if "warning" in expected:
            checks["constraint_explained"] = any(expected["warning"] in " ".join(getattr(h, "review_warnings", ())) for h in found)
        if "before" in expected:
            checks["unrelated_reaction_excluded"] = all(h.end <= expected["before"] for h in found if h.category == "crash")
        if expected.get("metadata"):
            checks["review_metadata"] = bool(found) and all(getattr(h, "title", "")
                            and getattr(h, "score_components", ()) and getattr(h, "available_modalities", ()) for h in found)
        if "max_score" in expected:
            checks["incomplete_priority"] = bool(found) and max(h.score for h in found) <= expected["max_score"]
        checks["deterministic"] = found == detect(list(reversed(rows)), case["duration"], Config(**case.get("config", {})))
        results.append({"id": case["id"], "split": case["split"], "checks": checks,
                        "passed": all(checks.values()), "predictions": [asdict(h) for h in found]})
    return {"fixture_name": document["name"], "fixture_sha256": hashlib.sha256(FIXTURES.read_bytes()).hexdigest(),
            "limitations": "Authored transcript/signal metadata only. Public holdout is not blind. No GTA VI accuracy, rendered output or entertainment quality measured.",
            "summary": {split: {"cases": sum(r["split"] == split for r in results),
                                "passed": sum(r["split"] == split and r["passed"] for r in results)}
                        for split in ("development", "holdout")}, "cases": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate()
    root = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    for path in sorted((root / "src").rglob("*.py")):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    result["source_sha256"] = digest.hexdigest()
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"]))


if __name__ == "__main__":
    main()
