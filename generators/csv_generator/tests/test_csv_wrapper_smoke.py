import json

from generators.csv_generator.generator.cli import main


def test_csv_wrapper_generate_and_validate(tmp_path, monkeypatch):
    out = tmp_path / "csv"
    schema = "csv_generator/schemas/retail_basic.yaml"
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", schema, "--out", str(out), "--rows", "10", "--seed", "42"])
    main()
    assert (out / "customers.csv").exists()

    monkeypatch.setattr("sys.argv", ["prog", "validate", "--schema", schema, "--out", str(out), "--rows", "10", "--seed", "42"])
    main()
    report = json.loads((out / "validation_report.json").read_text())
    assert report["ok"] is True
