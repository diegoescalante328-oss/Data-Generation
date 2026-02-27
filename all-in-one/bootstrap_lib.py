from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = REPO_ROOT / ".venv"
MARKER_PATH = VENV_DIR / ".datagen_bootstrap.json"

FORMAT_MODULE_CANDIDATES: dict[str, list[str]] = {
    "csv": ["generators.csv_generator.generator.cli", "csv_generator.generator.cli"],
    "json": ["generators.json_generator.generator.cli"],
    "ndjson": ["generators.json_generator.generator.cli"],
    "sqlite": ["generators.sqlite_seed.generator.cli"],
    "parquet": ["generators.parquet_generator.generator.cli"],
    "event_stream": ["generators.event_stream_generator.generator.cli"],
}

FORMAT_REQUIREMENTS: dict[str, list[Path]] = {
    "csv": [REPO_ROOT / "generators/csv_generator/requirements.txt", REPO_ROOT / "csv_generator/requirements.txt"],
    "json": [REPO_ROOT / "generators/json_generator/requirements.txt"],
    "ndjson": [REPO_ROOT / "generators/json_generator/requirements.txt"],
    "sqlite": [REPO_ROOT / "generators/sqlite_seed/requirements.txt"],
    "parquet": [REPO_ROOT / "generators/parquet_generator/requirements.txt"],
    "event_stream": [REPO_ROOT / "generators/event_stream_generator/requirements.txt"],
}




REQUIRED_IMPORTS: dict[str, list[str]] = {
    "csv": ["yaml", "faker"],
    "json": ["yaml", "faker"],
    "ndjson": ["yaml", "faker"],
    "sqlite": ["yaml", "faker"],
    "parquet": ["yaml", "faker", "pyarrow"],
    "event_stream": ["yaml", "faker"],
}


class BootstrapError(RuntimeError):
    pass


def is_windows() -> bool:
    return platform.system().lower().startswith("win")


def venv_python() -> Path:
    return VENV_DIR / ("Scripts/python.exe" if is_windows() else "bin/python")


def run_command(cmd: Sequence[str], *, env: dict[str, str] | None = None, verbose: bool = False) -> subprocess.CompletedProcess[str]:
    if verbose:
        print(f"[bootstrap] $ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=REPO_ROOT, env=env, text=True, check=True)


def run_command_capture(cmd: Sequence[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=REPO_ROOT, env=env, text=True, check=True, capture_output=True)


def module_exists(module: str) -> bool:
    module_path = REPO_ROOT / f"{module.replace('.', '/')}.py"
    return module_path.exists()


def resolve_module(fmt: str) -> str:
    candidates = FORMAT_MODULE_CANDIDATES.get(fmt, [])
    for candidate in candidates:
        if module_exists(candidate):
            return candidate
    raise BootstrapError(f"No CLI module found for --format {fmt}. Tried: {', '.join(candidates)}")


def collect_requirements(fmt: str) -> list[Path]:
    reqs: list[Path] = []
    requirements_dev = REPO_ROOT / "requirements-dev.txt"
    if requirements_dev.exists():
        reqs.append(requirements_dev)

    for req in FORMAT_REQUIREMENTS.get(fmt, []):
        if req.exists() and req not in reqs:
            reqs.append(req)
    return reqs


def requirements_fingerprint(requirement_files: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    for req in sorted(requirement_files):
        digest.update(str(req.relative_to(REPO_ROOT)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(req.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_marker(fmt: str, requirement_files: Sequence[Path]) -> dict:
    return {
        "python_version": sys.version,
        "python_executable": str(sys.executable),
        "format": fmt,
        "requirements": [str(p.relative_to(REPO_ROOT)) for p in requirement_files],
        "requirements_hash": requirements_fingerprint(requirement_files),
    }


def marker_matches(expected: dict) -> bool:
    if not MARKER_PATH.exists():
        return False
    try:
        found = json.loads(MARKER_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False

    for key in ("python_version", "format", "requirements_hash"):
        if found.get(key) != expected.get(key):
            return False
    return True


def _safe_install(cmd: Sequence[str], *, verbose: bool) -> bool:
    try:
        run_command(cmd, verbose=verbose)
        return True
    except subprocess.CalledProcessError:
        return False


def have_required_imports(fmt: str) -> bool:
    py = str(venv_python())
    modules = REQUIRED_IMPORTS.get(fmt, [])
    for module in modules:
        probe = subprocess.run(
            [py, "-c", f"import {module}"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        if probe.returncode != 0:
            return False
    return True


def ensure_venv(*, verbose: bool) -> None:
    py = venv_python()
    if py.exists():
        return
    run_command([sys.executable, "-m", "venv", str(VENV_DIR)], verbose=verbose)


def install_deps_if_needed(fmt: str, *, reinstall: bool, verbose: bool) -> None:
    requirement_files = collect_requirements(fmt)
    marker = build_marker(fmt, requirement_files)
    if not reinstall and marker_matches(marker):
        if verbose:
            print("[bootstrap] Existing install cache is valid; skipping dependency reinstall")
        return

    py = str(venv_python())
    install_ok = _safe_install([py, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], verbose=verbose)

    if requirement_files:
        for req in requirement_files:
            install_ok = _safe_install([py, "-m", "pip", "install", "-r", str(req)], verbose=verbose) and install_ok
    else:
        install_ok = _safe_install([py, "-m", "pip", "install", "pyyaml", "faker"], verbose=verbose) and install_ok

    if any((REPO_ROOT / p).exists() for p in ("pyproject.toml", "setup.cfg", "setup.py")):
        install_ok = _safe_install([py, "-m", "pip", "install", "-e", "."], verbose=verbose) and install_ok

    if not install_ok and not have_required_imports(fmt):
        raise BootstrapError(
            "Dependency installation failed and required packages are unavailable in .venv. "
            "Configure pip access (proxy/index) and rerun with --reinstall."
        )

    VENV_DIR.mkdir(parents=True, exist_ok=True)
    MARKER_PATH.write_text(json.dumps(marker, indent=2), encoding="utf-8")


def bootstrap(fmt: str, *, reinstall: bool, verbose: bool) -> None:
    ensure_venv(verbose=verbose)
    install_deps_if_needed(fmt, reinstall=reinstall, verbose=verbose)


def build_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return env


def build_generator_command(args: argparse.Namespace, module: str) -> list[str]:
    cmd = [str(venv_python()), "-m", module, args.command, "--schema", args.schema]

    if args.command in {"generate", "validate"}:
        if not args.out:
            raise BootstrapError("--out is required for generate and validate")
        cmd.extend(["--out", args.out])

    if args.seed is not None:
        cmd.extend(["--seed", str(args.seed)])
    if args.rows is not None:
        cmd.extend(["--rows", str(args.rows)])
    if args.profile:
        cmd.extend(["--profile", args.profile])
    if args.verbose:
        cmd.append("--verbose")

    if args.format in {"json", "ndjson"}:
        output_mode = "ndjson" if args.format == "ndjson" else "json"
        cmd.extend(["--output-mode", output_mode])

    return cmd
