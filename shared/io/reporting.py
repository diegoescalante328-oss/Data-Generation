from __future__ import annotations

import json
from pathlib import Path


def write_validation_report(out_dir: str | Path, errors: list[str], table_counts: dict[str, int]) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    report = {"ok": not errors, "errors": errors, "table_counts": table_counts}
    report_path = out / "validation_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report_path
