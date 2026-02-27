from __future__ import annotations

from pathlib import Path
from typing import Any

from shared.cli.common import write_validation_report as _write_validation_report


def write_validation_report(
    out_dir: str | Path,
    errors: list[str],
    table_counts: dict[str, int],
    *,
    generator: str = "unknown",
    schema_path: str | Path = "",
    output_path: str | Path = "",
    seed: int | None = None,
    checks: list[dict[str, Any]] | None = None,
) -> Path:
    """Backward-compatible wrapper for validation reports."""

    return _write_validation_report(
        out_dir,
        generator=generator,
        schema_path=schema_path,
        output_path=output_path,
        seed=seed,
        checks=checks or [],
        errors=errors,
        stats={"table_counts": table_counts},
    )
