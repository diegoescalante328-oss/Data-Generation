from __future__ import annotations

import json
from pathlib import Path


def write_json(out_path: str | Path, rows: list[dict], mode: str) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if mode == "ndjson":
        out.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    else:
        out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return out
