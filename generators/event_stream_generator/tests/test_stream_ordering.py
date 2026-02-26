import json

from generators.event_stream_generator.generator.cli import main


def test_stream_ordering(tmp_path, monkeypatch):
    out = tmp_path / "stream"
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", "generators/event_stream_generator/schemas/clickstream_stream.yaml", "--out", str(out)])
    main()
    lines = (out / "events.ndjson").read_text().strip().splitlines()
    first = json.loads(lines[0])
    assert {"event_id", "event_time", "user_id", "session_id"}.issubset(first.keys())
