"""Schema configuration loading utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class SchemaConfig:
    """Container for parsed schema configuration."""

    raw: Dict[str, Any]
    path: Path


def load_schema(schema_path: str | Path) -> SchemaConfig:
    """Load a YAML schema definition from disk.

    If pyyaml is unavailable, a JSON-compatible YAML fallback parser is used.
    """

    path = Path(schema_path)
    text = path.read_text(encoding="utf-8")

    data: Dict[str, Any]
    try:
        import yaml

        loaded = yaml.safe_load(text)
    except ImportError:
        try:
            loaded = json.loads(text)
        except json.JSONDecodeError as exc:  # pragma: no cover - runtime guidance
            raise RuntimeError(
                "pyyaml is not installed and schema is not JSON-compatible YAML. "
                "Install dependencies with: pip install -r csv_generator/requirements.txt"
            ) from exc

    if not isinstance(loaded, dict):
        raise ValueError(f"Schema at {path} must be a mapping")
    if "dataset" not in loaded or "tables" not in loaded:
        raise ValueError("Schema requires top-level 'dataset' and 'tables' keys")
    data = loaded
    return SchemaConfig(raw=data, path=path)
