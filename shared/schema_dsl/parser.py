from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Schema:
    raw: dict[str, Any]
    path: Path


def load_schema(path: str | Path) -> Schema:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    try:
        import yaml

        data = yaml.safe_load(text)
    except ImportError:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Optional dependency 'pyyaml' is required for non-JSON schema files. "
                "Install with: pip install -r requirements-dev.txt"
            ) from exc
    if not isinstance(data, dict):
        raise ValueError("Schema must be a mapping")
    if "dataset" not in data:
        raise ValueError("Schema requires dataset")
    return Schema(raw=data, path=p)


def describe_schema(schema: Schema) -> str:
    lines = [f"Dataset: {schema.raw['dataset']}"]
    for table_name, spec in schema.raw.get("tables", {}).items():
        lines.append(f"- {table_name} rows={spec.get('rows', 'n/a')}")
        for col in spec.get("columns", []):
            lines.append(f"    * {col['name']}: {col.get('type', 'computed')}")
    return "\n".join(lines)
