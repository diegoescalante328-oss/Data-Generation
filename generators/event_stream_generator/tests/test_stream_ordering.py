import hashlib
import json

from generators.event_stream_generator.generator.cli import main


def test_stream_generate_and_validate(tmp_path, monkeypatch):
    out = tmp_path / "stream"
    schema = "generators/event_stream_generator/schemas/clickstream_stream.yaml"
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", schema, "--out", str(out), "--rows", "10", "--seed", "77"])
    main()
    lines = (out / "events.ndjson").read_text().strip().splitlines()
    first = json.loads(lines[0])
    assert {"event_id", "event_time", "user_id", "session_id"}.issubset(first.keys())

    monkeypatch.setattr("sys.argv", ["prog", "validate", "--schema", schema, "--out", str(out), "--rows", "10", "--seed", "77"])
    main()
    report = json.loads((out / "validation_report.json").read_text())
    assert report["ok"] is True


def test_stream_deterministic_seed(tmp_path, monkeypatch):
    schema = "generators/event_stream_generator/schemas/clickstream_stream.yaml"
    out1 = tmp_path / "a"
    out2 = tmp_path / "b"
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", schema, "--out", str(out1), "--rows", "10", "--seed", "33"])
    main()
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", schema, "--out", str(out2), "--rows", "10", "--seed", "33"])
    main()
    h1 = hashlib.sha256((out1 / "events.ndjson").read_bytes()).hexdigest()
    h2 = hashlib.sha256((out2 / "events.ndjson").read_bytes()).hexdigest()
    assert h1 == h2
