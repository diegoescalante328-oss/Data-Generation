from __future__ import annotations

import json
from pathlib import Path

from csv_generator.generator.cli import main


def test_cli_validate_writes_report(tmp_path: Path) -> None:
    out_file = tmp_path / "report.json"
    exit_code = main(
        [
            "validate",
            "--schema",
            "csv_generator/schemas/retail_basic.yaml",
            "--rows",
            "10",
            "--seed",
            "4",
            "--out",
            str(out_file),
        ]
    )

    assert exit_code == 0
    report = json.loads(out_file.read_text(encoding="utf-8"))
    assert report["valid"] is True
    assert "summary" in report
