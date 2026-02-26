from __future__ import annotations

import json
from pathlib import Path


def write_ndjson(path: str, events: list[dict]) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
    return out
