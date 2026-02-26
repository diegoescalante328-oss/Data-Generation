from __future__ import annotations

import argparse
from datetime import datetime

from shared.io.reporting import write_validation_report
from shared.schema_dsl.parser import load_schema
from .ndjson_writer import write_ndjson
from .stream import generate_stream


def _cmd_generate(args):
    schema = load_schema(args.schema)
    seed = args.seed if args.seed is not None else schema.raw.get("seed", 0)
    rows = args.rows or schema.raw.get("rows", 100)
    late = schema.raw.get("late_events", False)
    events = generate_stream(rows, seed, late_events=late)
    write_ndjson(f"{args.out}/events.ndjson", events)


def _cmd_describe(args):
    schema = load_schema(args.schema)
    print(f"Dataset: {schema.raw['dataset']} rows={schema.raw.get('rows', 100)}")


def _cmd_validate(args):
    schema = load_schema(args.schema)
    seed = args.seed if args.seed is not None else schema.raw.get("seed", 0)
    rows = args.rows or schema.raw.get("rows", 100)
    late = schema.raw.get("late_events", False)
    events = generate_stream(rows, seed, late_events=late)
    errors = []
    non_decreasing = 0
    for i in range(1, len(events)):
        if datetime.fromisoformat(events[i]["event_time"]) >= datetime.fromisoformat(events[i - 1]["event_time"]):
            non_decreasing += 1
    ratio = non_decreasing / max(1, len(events) - 1)
    if not late and ratio < 1.0:
        errors.append("event_time not strictly ordered")
    if late and ratio < 0.9:
        errors.append("too many late events")
    for e in events:
        for req in ["event_id", "event_time", "user_id", "session_id", "event_type", "metadata", "source"]:
            if req not in e:
                errors.append(f"missing {req}")
                break
    report = write_validation_report(args.out, errors, {"events": len(events)})
    print(report)
    if errors:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description="Event stream generator")
    sub = parser.add_subparsers(dest="command", required=True)
    for n, fn in (("generate", _cmd_generate), ("describe", _cmd_describe), ("validate", _cmd_validate)):
        p = sub.add_parser(n)
        p.add_argument("--schema", required=True)
        p.add_argument("--seed", type=int, default=None)
        p.add_argument("--out", required=True)
        p.add_argument("--rows", type=int, default=None)
        p.add_argument("--profile", choices=["fast", "realistic", "dirty"], default="realistic")
        p.set_defaults(func=fn)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
