#!/usr/bin/env python3
"""Re-run all authored regression fixtures; write current, reviewable results."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from evaluation.run import FIXTURES, evaluate_fixtures, load_cases, markdown_report, source_hash  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("all", "development", "holdout"), default="all")
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "results" / "current.json")
    args = parser.parse_args()
    report = evaluate_fixtures(load_cases(), split=args.split)
    report["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    report["provenance"] = {"fixture_sha256": hashlib.sha256(FIXTURES.read_bytes()).hexdigest(),
                            "plugin_source_sha256": source_hash(ROOT),
                            "python_version": sys.version.split()[0],
                            "command": "python scripts/evaluate.py --split " + args.split}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown_report(report), encoding="utf-8")
    for name, output in report["detectors"].items():
        m = output["summary"]
        print(f"{name}: TP={m['true_positives']} FP={m['false_positives']} FN={m['false_negatives']}; "
              f"precision={m['precision']} recall={m['recall']}")
    print(f"Saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
