# Quickstart

## Install

```bash
pip install -r requirements-dev.txt
```

Project uses per-module `requirements.txt` files plus root `requirements-dev.txt` for testing.

## Run each module

```bash
python -m generators.csv_generator.generator.cli generate --schema csv_generator/schemas/retail_basic.yaml --out csv_generator/output
python -m generators.parquet_generator.generator.cli generate --schema generators/parquet_generator/schemas/retail_basic_parquet.yaml --out generators/parquet_generator/output
python -m generators.json_generator.generator.cli generate --schema generators/json_generator/schemas/web_events_ndjson.yaml --out generators/json_generator/output
python -m generators.sqlite_seed.generator.cli generate --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml --out generators/sqlite_seed/output/retail_basic.db
python -m generators.event_stream_generator.generator.cli generate --schema generators/event_stream_generator/schemas/clickstream_stream.yaml --out generators/event_stream_generator/output
```
