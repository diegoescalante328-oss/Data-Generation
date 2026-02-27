"""Schema configuration loading utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class SchemaError(ValueError):
    """Raised when schema loading/parsing fails."""


@dataclass(frozen=True)
class SchemaConfig:
    """Container for parsed schema configuration."""

    raw: dict[str, Any]
    path: Path


def _load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SchemaError(f"Schema file not found: {path}") from exc
    except OSError as exc:
        raise SchemaError(f"Unable to read schema file: {path} ({exc})") from exc


def load_schema(schema_path: str | Path) -> SchemaConfig:
    """Load a schema definition from disk.

    Paths are resolved relative to the current working directory.
    """

    path = Path(schema_path).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()

    text = _load_text(path)

    loaded: Any
    try:
        import yaml

        loaded = yaml.safe_load(text)
    except ImportError as exc:
        try:
            loaded = json.loads(text)
        except json.JSONDecodeError as json_exc:
            raise SchemaError(
                "Schema requires PyYAML for non-JSON YAML files. "
                "Install dependencies with: pip install -r csv_generator/requirements.txt"
            ) from json_exc
        if path.suffix.lower() in {".yaml", ".yml"}:
            # Only a guidance warning path; JSON-formatted YAML still works.
            _ = exc
    except Exception as exc:
        raise SchemaError(f"Failed to parse schema file {path}: {exc}") from exc

    if not isinstance(loaded, dict):
        raise SchemaError(f"Schema at {path} must be a mapping/object")
    if "dataset" not in loaded or "tables" not in loaded:
        raise SchemaError("Schema requires top-level 'dataset' and 'tables' keys")
    if not isinstance(loaded["tables"], dict) or not loaded["tables"]:
        raise SchemaError("Schema 'tables' must be a non-empty mapping")

    loaded.setdefault("relationships", [])
    return SchemaConfig(raw=loaded, path=path)
