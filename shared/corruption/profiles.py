from __future__ import annotations

import random


PROFILE_DEFAULTS = {
    "fast": {"missingness": 0.0, "duplicates": 0.0, "outliers": 0.0},
    "realistic": {"missingness": 0.01, "duplicates": 0.0, "outliers": 0.005},
    "dirty": {"missingness": 0.08, "duplicates": 0.0, "outliers": 0.03},
}


def apply_profile(rows: list[dict], profile: str, rng: random.Random) -> list[dict]:
    opts = PROFILE_DEFAULTS.get(profile, PROFILE_DEFAULTS["realistic"])
    if not rows:
        return rows
    keys = list(rows[0].keys())
    for row in rows:
        if rng.random() < opts["missingness"]:
            row[rng.choice(keys)] = None
    if opts["duplicates"] > 0 and len(rows) > 2:
        dup_count = int(len(rows) * opts["duplicates"])
        for _ in range(max(1, dup_count)):
            rows.append(dict(rng.choice(rows)))
    return rows
