from __future__ import annotations

import hashlib
import random


def derive_rng(seed: int, *parts: str) -> random.Random:
    key = "::".join([str(seed), *parts]).encode("utf-8")
    digest = hashlib.sha256(key).hexdigest()[:16]
    return random.Random(int(digest, 16))
