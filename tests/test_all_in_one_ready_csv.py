import csv
import importlib.util
from pathlib import Path


def _load_module():
    module_path = Path("all-in-one/csv_generator_ready.py")
    spec = importlib.util.spec_from_file_location("ready_gen", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_all_in_one_csv_generation(tmp_path):
    mod = _load_module()
    out = tmp_path / "generated.csv"
    path = mod.generate_csv(rows=50, seed=11, out=str(out))
    assert path.exists()

    with path.open("r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) == 50
    expected_cols = {
        "event_id",
        "event_time",
        "user_id",
        "session_id",
        "event_type",
        "country",
        "source",
        "device",
        "amount",
        "is_premium_user",
    }
    assert expected_cols.issubset(reader[0].keys())
