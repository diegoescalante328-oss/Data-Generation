from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP_LIB_PATH = REPO_ROOT / "all-in-one" / "bootstrap_lib.py"


spec = importlib.util.spec_from_file_location("bootstrap_lib", BOOTSTRAP_LIB_PATH)
assert spec and spec.loader
bootstrap_lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap_lib)


find_repo_root = bootstrap_lib.find_repo_root
BootstrapError = bootstrap_lib.BootstrapError


@pytest.mark.parametrize(
    "start",
    [
        REPO_ROOT / "all-in-one",
        REPO_ROOT,
    ],
)
def test_find_repo_root_detects_repository_from_multiple_start_locations(start: Path) -> None:
    found = find_repo_root(start)
    assert found == REPO_ROOT


def test_find_repo_root_raises_when_layout_markers_are_missing(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()

    with pytest.raises(BootstrapError) as exc:
        find_repo_root(outside)

    message = str(exc.value)
    assert "Could not auto-detect repository root" in message
    assert "required directories" in message
