import json

from generators.json_generator.generator.cli import main


def test_json_smoke(tmp_path, monkeypatch):
    out = tmp_path / "output"
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", "generators/json_generator/schemas/web_events_ndjson.yaml", "--out", str(out)])
    main()
    file = out / "web_events.ndjson"
    assert file.exists()
    first = json.loads(file.read_text().splitlines()[0])
    assert "user" in first and "event" in first
