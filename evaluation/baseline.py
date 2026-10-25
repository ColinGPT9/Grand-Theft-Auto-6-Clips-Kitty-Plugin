"""An original, intentionally limited energy-only reference detector.

This is not Clips Kitty's built-in finder and is not a historical product
benchmark. It uses the public SDK signal helpers on the same authored cases.
"""

from __future__ import annotations

from clipskitty_sdk import signals


def detect_energy(loudness: list[float], duration: float, *, louder_by_db: float = 6.0) -> list[dict]:
    spikes = signals.spikes(loudness, louder_by=louder_by_db)
    runs = signals.stretches(spikes, gap=2.0, min_length=0)
    return [{"start": max(0.0, start - 8.0), "end": min(duration, end + 10.0),
             "category": "energy_spike", "reason": "relative loudness spike only"}
            for start, end in runs if min(duration, end + 10.0) > max(0.0, start - 8.0)]
