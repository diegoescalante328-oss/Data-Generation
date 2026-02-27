from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "all-in-one/datagen_bootstrap.py"
SQLITE_SCHEMA = REPO_ROOT / "generators/sqlite_seed/schemas/retail_basic_sqlite.yaml"


def _can_create_venv() -> bool:
    probe = REPO_ROOT / ".tmp_venv_probe"
    if probe.exists():
        shutil.rmtree(probe)
    try:
        result = subprocess.run([sys.executable, "-m", "venv", str(probe)], cwd=REPO_ROOT, capture_output=True, text=True)
        return result.returncode == 0
    finally:
        shutil.rmtree(probe, ignore_errors=True)


pytestmark = pytest.mark.skipif(not _can_create_venv(), reason="Python venv creation unavailable in this environment")


def test_bootstrap_help() -> None:
    proc = subprocess.run([sys.executable, str(RUNNER), "--help"], cwd=REPO_ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "Option B bootstrap runner" in proc.stdout


def test_bootstrap_generate_then_validate_sqlite(tmp_path: Path) -> None:
    out_db = tmp_path / "smoke.db"

    generate = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "generate",
            "--schema",
            str(SQLITE_SCHEMA),
            "--out",
            str(out_db),
            "--format",
            "sqlite",
            "--rows",
            "10",
            "--seed",
            "17",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if generate.returncode != 0 and "Dependency installation failed" in (generate.stderr + generate.stdout):
        pytest.skip("Dependency installation unavailable in this environment")
    assert generate.returncode == 0, generate.stderr + "\n" + generate.stdout
    assert out_db.exists()

    validate = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "validate",
            "--schema",
            str(SQLITE_SCHEMA),
            "--out",
            str(out_db),
            "--format",
            "sqlite",
            "--rows",
            "10",
            "--seed",
            "17",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert validate.returncode == 0, validate.stderr + "\n" + validate.stdout
    assert "Validation passed" in validate.stdout
