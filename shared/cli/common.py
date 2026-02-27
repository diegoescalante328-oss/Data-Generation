from __future__ import annotations

import argparse
import json
import os
import traceback
from pathlib import Path
from typing import Any, Callable

REPORT_FILENAME = "validation_report.json"


def add_common_arguments(parser: argparse.ArgumentParser, *, include_profile: bool = True, require_out: bool = True) -> None:
    parser.add_argument("--schema", required=True, help="Path to schema file")
    parser.add_argument("--out", required=require_out, help="Output directory or file path")
    parser.add_argument("--seed", type=int, default=None, help="Seed for deterministic generation")
    parser.add_argument("--rows", type=int, default=None, help="Optional row count override")
    if include_profile:
        parser.add_argument("--profile", choices=["fast", "realistic", "dirty"], default="realistic")
    parser.add_argument("--verbose", action="store_true", help="Show verbose errors")


def build_parser(description: str, command_map: dict[str, Callable[[argparse.Namespace], int | None]], *, include_profile: bool = True) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fn in command_map.items():
        cmd = sub.add_parser(name)
        add_common_arguments(cmd, include_profile=include_profile, require_out=(name != "describe"))
        cmd.set_defaults(func=fn)
    return parser


def ensure_path_exists(path: Path, *, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{description} not found: {path}")


def optional_dependency_error(package: str, install_hint: str) -> RuntimeError:
    return RuntimeError(f"Optional dependency '{package}' is required. Install with: {install_hint}")


def write_validation_report(
    out_path: str | Path,
    *,
    generator: str,
    schema_path: str | Path,
    output_path: str | Path,
    seed: int | None,
    checks: list[dict[str, Any]],
    errors: list[str],
    stats: dict[str, Any],
) -> Path:
    out = Path(out_path)
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "ok": not errors and all(check.get("ok", False) for check in checks),
        "generator": generator,
        "schema_path": str(Path(schema_path)),
        "out_path": str(Path(output_path)),
        "seed": seed,
        "checks": checks,
        "errors": errors,
        "stats": stats,
    }
    report_path = out / REPORT_FILENAME
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report_path


def command_main(parser: argparse.ArgumentParser) -> int:
    args = parser.parse_args()
    try:
        result = args.func(args)
    except Exception as exc:
        if getattr(args, "verbose", False) or os.getenv("DEBUG"):
            traceback.print_exc()
        else:
            print(f"Error: {exc}")
        raise SystemExit(1) from exc
    code = int(result) if result is not None else 0
    if code:
        raise SystemExit(code)
    return 0
