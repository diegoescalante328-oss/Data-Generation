#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parent
VENV_DIR = REPO_ROOT / ".venv"
BOOTSTRAP_MARKER = VENV_DIR / ".datagen_bootstrap.json"

FORMAT_ROUTES = {
    "csv": ["generators.csv_generator.generator.cli", "csv_generator.generator.cli"],
    "json": ["generators.json_generator.generator.cli"],
    "ndjson": ["generators.json_generator.generator.cli"],
    "sqlite": ["generators.sqlite_seed.generator.cli"],
    "parquet": ["generators.parquet_generator.generator.cli"],
    "event_stream": ["generators.event_stream_generator.generator.cli"],
}

MODULE_REQUIREMENT_FILES = {
    "csv": [REPO_ROOT / "generators/csv_generator/requirements.txt", REPO_ROOT / "csv_generator/requirements.txt"],
    "json": [REPO_ROOT / "generators/json_generator/requirements.txt"],
    "ndjson": [REPO_ROOT / "generators/json_generator/requirements.txt"],
    "sqlite": [REPO_ROOT / "generators/sqlite_seed/requirements.txt"],
    "parquet": [REPO_ROOT / "generators/parquet_generator/requirements.txt"],
    "event_stream": [REPO_ROOT / "generators/event_stream_generator/requirements.txt"],
}

REQUIRED_IMPORTS = {
    "csv": ["yaml", "faker"],
    "json": ["yaml", "faker"],
    "ndjson": ["yaml", "faker"],
    "sqlite": ["yaml", "faker"],
    "parquet": ["yaml", "faker", "pyarrow"],
    "event_stream": ["yaml", "faker"],
}

EXTRA_PIP_PACKAGES = {
    "parquet": ["pyarrow"],
    "yaml": ["pyyaml"],
    "faker": ["faker"],
}

SUPPORTED_FLAGS = {
    "csv": {"schema", "out", "seed", "profile", "rows", "verbose"},
    "json": {"schema", "out", "seed", "profile", "rows", "verbose"},
    "ndjson": {"schema", "out", "seed", "profile", "rows", "verbose"},
    "sqlite": {"schema", "out", "seed", "profile", "rows", "verbose"},
    "parquet": {"schema", "out", "seed", "profile", "rows", "verbose"},
    "event_stream": {"schema", "out", "seed", "profile", "rows", "verbose"},
}


def _is_windows() -> bool:
    return platform.system().lower().startswith("win")


def _venv_python() -> Path:
    if _is_windows():
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _run(cmd: Sequence[str], verbose: bool = True, check: bool = True) -> subprocess.CompletedProcess[str]:
    if verbose:
        print(f"[datagen-onefile] $ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, check=check)


def _requirements_hash(paths: Sequence[Path]) -> str:
    hasher = hashlib.sha256()
    for path in sorted(paths):
        hasher.update(str(path.relative_to(REPO_ROOT)).encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(path.read_bytes())
        hasher.update(b"\0")
    return hasher.hexdigest()


def _collect_requirement_files(fmt: str, extras: Sequence[str]) -> list[Path]:
    files: list[Path] = []
    dev = REPO_ROOT / "requirements-dev.txt"
    if dev.exists():
        files.append(dev)
    for req in MODULE_REQUIREMENT_FILES.get(fmt, []):
        if req.exists() and req not in files:
            files.append(req)
    for extra in extras:
        extra_req = REPO_ROOT / "generators" / extra / "requirements.txt"
        if extra_req.exists() and extra_req not in files:
            files.append(extra_req)
    return files


def _load_marker() -> dict[str, object]:
    if not BOOTSTRAP_MARKER.exists():
        return {}
    try:
        return json.loads(BOOTSTRAP_MARKER.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _write_marker(marker: dict[str, object]) -> None:
    BOOTSTRAP_MARKER.write_text(json.dumps(marker, indent=2, sort_keys=True), encoding="utf-8")


def _create_venv_if_needed(verbose: bool) -> None:
    if _venv_python().exists():
        return
    print("[datagen-onefile] Creating virtual environment in .venv")
    _run([sys.executable, "-m", "venv", "--system-site-packages", str(VENV_DIR)], verbose=verbose)




def _have_required_imports(fmt: str, extras: Sequence[str]) -> bool:
    modules = set(REQUIRED_IMPORTS.get(fmt, []))
    for extra in extras:
        if extra == "parquet":
            modules.add("pyarrow")
        if extra == "yaml":
            modules.add("yaml")
        if extra == "faker":
            modules.add("faker")
    for module in modules:
        try:
            importlib.import_module(module)
        except Exception:
            return False
    return True


def _safe_run_install(cmd: Sequence[str], verbose: bool) -> bool:
    try:
        _run(cmd, verbose=verbose)
        return True
    except subprocess.CalledProcessError as exc:
        print(f"[datagen-onefile] Warning: install step failed ({exc.returncode}) for: {' '.join(cmd)}")
        return False

def _install_dependencies(args: argparse.Namespace) -> None:
    fmt = args.format
    requested_extras = list(args.extras or [])
    if fmt == "parquet" and "parquet" not in requested_extras:
        requested_extras.append("parquet")

    req_files = _collect_requirement_files(fmt, requested_extras)
    marker = {
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "requirements_hash": _requirements_hash(req_files) if req_files else "",
        "format": fmt,
        "extras": sorted(requested_extras),
    }

    current = _load_marker()
    if not args.reinstall and current == marker:
        if args.verbose:
            print("[datagen-onefile] Dependency set unchanged; skipping reinstall")
        return

    pip_python = str(_venv_python())
    _safe_run_install([pip_python, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], verbose=args.verbose)

    install_ok = True
    if req_files:
        for req in req_files:
            install_ok = _safe_run_install([pip_python, "-m", "pip", "install", "-r", str(req)], verbose=args.verbose) and install_ok
    else:
        print("[datagen-onefile] No requirements files discovered; installing minimal dependencies")
        install_ok = _safe_run_install([pip_python, "-m", "pip", "install", "pyyaml", "faker"], verbose=args.verbose) and install_ok

    package_markers = [REPO_ROOT / "pyproject.toml", REPO_ROOT / "setup.cfg", REPO_ROOT / "setup.py"]
    if any(p.exists() for p in package_markers):
        install_ok = _safe_run_install([pip_python, "-m", "pip", "install", "-e", "."], verbose=args.verbose) and install_ok

    for extra in requested_extras:
        for pkg in EXTRA_PIP_PACKAGES.get(extra, []):
            install_ok = _safe_run_install([pip_python, "-m", "pip", "install", pkg], verbose=args.verbose) and install_ok

    if not install_ok and not _have_required_imports(fmt, requested_extras):
        raise SystemExit("Dependency installation failed and required modules are unavailable in the environment.")

    _write_marker(marker)


def _module_exists(module_name: str) -> bool:
    path = REPO_ROOT / (module_name.replace(".", "/") + ".py")
    return path.exists()


def _resolve_module(fmt: str) -> str:
    for module in FORMAT_ROUTES[fmt]:
        if _module_exists(module):
            return module
    raise SystemExit(f"No generator CLI module found for format '{fmt}'. Tried: {', '.join(FORMAT_ROUTES[fmt])}")


def _ensure_supported_flags(args: argparse.Namespace) -> None:
    provided_optional = set()
    if args.seed is not None:
        provided_optional.add("seed")
    if args.profile is not None:
        provided_optional.add("profile")
    if args.rows is not None:
        provided_optional.add("rows")
    if args.table is not None:
        provided_optional.add("table")
    if args.verbose:
        provided_optional.add("verbose")

    unsupported = sorted(provided_optional - SUPPORTED_FLAGS[args.format])
    if unsupported:
        raise SystemExit(
            f"Format '{args.format}' does not support option(s): {', '.join('--' + u for u in unsupported)}"
        )


def _build_downstream_command(args: argparse.Namespace, module: str) -> list[str]:
    cmd = [str(_venv_python()), "-m", module, args.command, "--schema", args.schema]
    if args.command != "describe":
        if args.out is None:
            raise SystemExit("--out is required for generate/validate")
        cmd.extend(["--out", args.out])

    if args.seed is not None:
        cmd.extend(["--seed", str(args.seed)])
    if args.rows is not None:
        cmd.extend(["--rows", str(args.rows)])
    if args.profile is not None:
        cmd.extend(["--profile", args.profile])

    if args.format in {"json", "ndjson"}:
        mode = "ndjson" if args.format == "ndjson" else "json"
        cmd.extend(["--output-mode", mode])

    return cmd


def _bootstrap_and_run(args: argparse.Namespace) -> int:
    _create_venv_if_needed(args.verbose)
    _install_dependencies(args)
    _ensure_supported_flags(args)
    module = _resolve_module(args.format)
    cmd = _build_downstream_command(args, module)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    if args.verbose:
        print(f"[datagen-onefile] Routing '{args.format}' to module '{module}'")
        print(f"[datagen-onefile] Running from repo root: {REPO_ROOT}")
    result = subprocess.run(cmd, cwd=REPO_ROOT, env=env)
    return result.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Single-file Data-Generation runner. Bootstraps .venv, installs dependencies, "
            "and routes to the correct generator CLI."
        )
    )
    parser.add_argument("--reinstall", action="store_true", help="Force dependency reinstall in .venv")
    parser.add_argument("--extras", nargs="*", default=[], help="Optional dependency extras (e.g. parquet)")

    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser, need_out: bool) -> None:
        p.add_argument("--schema", required=True, help="Path to schema file")
        p.add_argument(
            "--format",
            required=True,
            choices=["csv", "json", "ndjson", "sqlite", "parquet", "event_stream"],
            help="Output generator format",
        )
        p.add_argument("--out", required=need_out, help="Output directory/file path")
        p.add_argument("--seed", type=int, default=None, help="Seed override")
        p.add_argument("--profile", choices=["fast", "realistic", "dirty"], default=None, help="Corruption profile")
        p.add_argument("--rows", type=int, default=None, help="Row count override")
        p.add_argument("--table", default=None, help="Optional single-table target (if supported)")
        p.add_argument("--verbose", action="store_true", help="Verbose bootstrap and routing logs")

    add_common(sub.add_parser("describe", help="Describe a schema"), need_out=False)
    add_common(sub.add_parser("generate", help="Generate synthetic data"), need_out=True)
    add_common(sub.add_parser("validate", help="Validate generated output"), need_out=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return _bootstrap_and_run(args)
    except subprocess.CalledProcessError as exc:
        print(f"[datagen-onefile] Command failed with exit code {exc.returncode}: {exc.cmd}", file=sys.stderr)
        return exc.returncode
    except KeyboardInterrupt:
        print("[datagen-onefile] Interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
