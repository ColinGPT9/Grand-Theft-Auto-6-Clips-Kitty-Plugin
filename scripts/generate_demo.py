#!/usr/bin/env python3
"""Generate original synthetic media for SDK integration checks, outside the plugin.

The images are geometric shapes and the audio is tones. The supplied fictional
transcript is test input, not speech recognized from those tones or real GTA
footage. No downloaded content or executable on PATH is used.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DURATION = 48.0
SEGMENTS = (
    (12.0, 15.0, "The cops are chasing me down this street."),
    (19.0, 22.0, "We crashed into a barrier!"),
    (23.0, 26.0, "I cannot stop laughing."),
)


def demo_transcript() -> dict:
    segments = []
    for start, end, text in SEGMENTS:
        words = text.split()
        step = (end - start) / len(words)
        segments.append({"start": start, "end": end, "text": text, "words": [
            {"start": round(start + i * step, 3), "end": round(start + (i + 1) * step, 3), "word": word}
            for i, word in enumerate(words)]})
    return {"language": "en", "segments": segments}


def demo_command(out: Path, ffmpeg: str = "/usr/bin/ffmpeg") -> list[str]:
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y"]
    for colour, seconds in (("0x1a2c42", 20), ("0xcfcfcf", 2), ("0x1a2c42", 26)):
        command += ["-f", "lavfi", "-i", f"color=c={colour}:s=640x360:r=24:d={seconds}"]
    command += ["-f", "lavfi", "-i", "sine=f=220:sample_rate=44100:d=48",
                "-f", "lavfi", "-i", "sine=f=880:sample_rate=44100:d=48"]
    filters = (
        "[0:v][1:v][2:v]concat=n=3:v=1:a=0,"
        "drawbox=x=100:y=210:w=440:h=100:color=0x444444:t=fill,"
        "drawbox=x=290:y=230:w=60:h=30:color=0xe0303a:t=fill,"
        "drawbox=x=290:y=230:w=60:h=30:color=0xffff00:t=fill:enable='between(t,20,22)'[v];"
        "[3:a]volume=0.03[q];"
        "[4:a]volume='if(between(t,20,22),0.8,0)':eval=frame[l];"
        "[q][l]amix=inputs=2:normalize=0[a]"
    )
    return [*command, "-filter_complex", filters, "-map", "[v]", "-map", "[a]",
            "-c:v", "mpeg4", "-q:v", "6", "-c:a", "aac", "-b:a", "64k",
            "-t", "48", "-movflags", "+faststart", "-f", "mp4", str(out)]


def _vtt_time(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, rest = divmod(milliseconds, 3600000)
    minutes, rest = divmod(rest, 60000)
    whole, fraction = divmod(rest, 1000)
    return f"{hours:02}:{minutes:02}:{whole:02}.{fraction:03}"


def generate_demo(out: Path, ffmpeg: str = "/usr/bin/ffmpeg") -> tuple[Path, Path]:
    """Write a 48-second synthetic MP4 and original transcript; return both paths.

    A .vtt caption sidecar and provenance annotations are also written. Use
    /tmp or a sibling of the plugin so generated media is never installed.
    The explicit FFmpeg path may be supplied on platforms with another path.
    """
    out = Path(out).resolve()
    if out == ROOT or ROOT in out.parents:
        raise ValueError("Generate test media outside the plugin folder, for example /tmp/gta-demo.mp4")
    tool = Path(ffmpeg)
    if not tool.is_absolute() or not tool.is_file():
        raise ValueError("Supply the absolute path of the FFmpeg executable; default is /usr/bin/ffmpeg")
    out.parent.mkdir(parents=True, exist_ok=True)
    partial = out.with_name(out.name + ".partial")
    try:
        completed = subprocess.run(demo_command(partial, str(tool)), capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=60, check=False)
        if completed.returncode != 0 or not partial.is_file():
            raise RuntimeError("FFmpeg demo generation failed: " + completed.stderr.strip()[-1500:])
        os.replace(partial, out)
    finally:
        partial.unlink(missing_ok=True)
    transcript = out.with_name(out.stem + ".transcript.json")
    transcript.write_text(json.dumps(demo_transcript(), indent=2) + "\n", encoding="utf-8")
    captions = ["WEBVTT", "", "NOTE Authored fictional test transcript; audio contains tones, not speech.", ""]
    for start, end, text in SEGMENTS:
        captions += [f"{_vtt_time(start)} --> {_vtt_time(end)}", text, ""]
    out.with_suffix(".vtt").write_text("\n".join(captions), encoding="utf-8")
    annotations = {"license": "MIT", "duration": DURATION,
                   "provenance": "Original geometric frames, synthetic tones, and fictional test transcript; not GTA footage.",
                   "scene_cuts": [20.0, 22.0], "loud_tone": [20.0, 22.0],
                   "annotated_event": {"setup": [10, 18], "payoff": [19, 22], "reaction": [23, 27]},
                   "manual_quality_review": "not_performed"}
    out.with_name(out.stem + ".annotations.json").write_text(json.dumps(annotations, indent=2) + "\n",
                                                            encoding="utf-8")
    return out, transcript


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="MP4 path outside the plugin, e.g. /tmp/gta-demo.mp4")
    parser.add_argument("--ffmpeg", default="/usr/bin/ffmpeg", help="Explicit absolute executable path")
    args = parser.parse_args()
    for path in generate_demo(args.output, args.ffmpeg):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
