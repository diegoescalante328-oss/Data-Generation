import hashlib
import json

from generators.json_generator.generator.cli import main


def _hash_path(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_json_smoke_generate_and_validate(tmp_path, monkeypatch):
    out = tmp_path / "output"
    schema = "generators/json_generator/schemas/web_events_ndjson.yaml"

    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", schema, "--out", str(out), "--rows", "10", "--seed", "123"])
    main()
    file = out / "web_events.ndjson"
    assert file.exists()
    first = json.loads(file.read_text().splitlines()[0])
    assert "user" in first and "event" in first

    monkeypatch.setattr("sys.argv", ["prog", "validate", "--schema", schema, "--out", str(out), "--rows", "10", "--seed", "123"])
    main()
    report = json.loads((out / "validation_report.json").read_text())
    assert report["ok"] is True


def test_json_deterministic_seed(tmp_path, monkeypatch):
    schema = "generators/json_generator/schemas/web_events_ndjson.yaml"
    out1 = tmp_path / "a"
    out2 = tmp_path / "b"

    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", schema, "--out", str(out1), "--rows", "10", "--seed", "999"])
    main()
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", schema, "--out", str(out2), "--rows", "10", "--seed", "999"])
    main()

    assert _hash_path(out1 / "web_events.ndjson") == _hash_path(out2 / "web_events.ndjson")
