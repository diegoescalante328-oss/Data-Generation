from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from shared.cli.common import build_parser, command_main, ensure_path_exists, write_validation_report
from shared.schema_dsl.parser import load_schema

from .ndjson_writer import write_ndjson
from .stream import generate_stream

GENERATOR_NAME = "event_stream_generator"
REQUIRED_EVENT_KEYS = ["event_id", "event_time", "user_id", "session_id", "event_type", "metadata", "source"]


def _resolve_seed(schema_raw: dict, seed: int | None) -> int:
    return seed if seed is not None else int(schema_raw.get("seed", 0))


def _resolve_rows(schema_raw: dict, rows: int | None) -> int:
    return rows if rows is not None else int(schema_raw.get("rows", 100))


def _output_path(out_dir: str | Path) -> Path:
    return Path(out_dir) / "events.ndjson"


def _cmd_generate(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    seed = _resolve_seed(schema.raw, args.seed)
    rows = _resolve_rows(schema.raw, args.rows)
    late = bool(schema.raw.get("late_events", False))
    out_file = write_ndjson(_output_path(args.out), generate_stream(rows, seed, late_events=late))
    print(f"Generated event stream at {out_file}")
    return 0


def _cmd_describe(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    print(f"Dataset: {schema.raw['dataset']} rows={schema.raw.get('rows', 100)}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    seed = _resolve_seed(schema.raw, args.seed)
    rows = _resolve_rows(schema.raw, args.rows)
    late = bool(schema.raw.get("late_events", False))
    path = _output_path(args.out)
    ensure_path_exists(path, description="NDJSON output")

    checks: list[dict] = []
    errors: list[str] = []
    parsed_events: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                parsed_events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                errors.append(f"Line {line_no} is invalid JSON: {exc}")

    checks.append({"name": "output_parseable", "ok": not errors, "details": {"path": str(path), "rows": len(parsed_events)}})

    non_decreasing = 0
    for i in range(1, len(parsed_events)):
        if datetime.fromisoformat(parsed_events[i]["event_time"]) >= datetime.fromisoformat(parsed_events[i - 1]["event_time"]):
            non_decreasing += 1
    ratio = non_decreasing / max(1, len(parsed_events) - 1)
    ordered_ok = ratio == 1.0 if not late else ratio >= 0.9
    checks.append({"name": "event_order", "ok": ordered_ok, "details": {"ratio": ratio, "late_events": late}})
    if not ordered_ok:
        errors.append("Event ordering check failed")

    missing_key_count = 0
    for event in parsed_events:
        for req in REQUIRED_EVENT_KEYS:
            if req not in event:
                missing_key_count += 1
                break
    keys_ok = missing_key_count == 0
    checks.append({"name": "required_keys", "ok": keys_ok, "details": {"missing_events": missing_key_count}})
    if not keys_ok:
        errors.append("Some events are missing required keys")

    row_ok = len(parsed_events) == rows
    checks.append({"name": "row_count_match", "ok": row_ok, "details": {"expected": rows, "actual": len(parsed_events)}})
    if not row_ok:
        errors.append(f"Row count mismatch: expected {rows}, got {len(parsed_events)}")

    # deterministic generation check
    expected_events = generate_stream(rows, seed, late_events=late)
    deterministic_ok = parsed_events == expected_events
    checks.append({"name": "deterministic_seed", "ok": deterministic_ok, "details": {"seed": seed}})
    if not deterministic_ok:
        errors.append("Output does not match deterministic generation for schema+seed")

    report = write_validation_report(
        args.out,
        generator=GENERATOR_NAME,
        schema_path=schema.path,
        output_path=path,
        seed=seed,
        checks=checks,
        errors=errors,
        stats={"event_count": len(parsed_events)},
    )
    print(f"Validation report: {report}")
    return 1 if errors else 0


def main() -> None:
    command_main(
        build_parser(
            "Event stream generator",
            {"describe": _cmd_describe, "generate": _cmd_generate, "validate": _cmd_validate},
        )
    )


if __name__ == "__main__":
    main()
