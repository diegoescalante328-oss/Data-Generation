# CSV Generator

A schema-driven synthetic dataset generator for analytics practice and testing.
It creates realistic CSV tables with configurable data types, distributions, constraints,
foreign-key relationships, computed columns, and optional dirty-data corruption.
The system is reproducible: use the same schema + seed and you get identical output.

## Option B local `.venv` workflow

Use the repository-local virtual environment (Option B) so dependencies stay local to the repo.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r csv_generator/requirements.txt
```

You can then run the generator directly via module execution:

```bash
python -m csv_generator.generator.cli describe --schema csv_generator/schemas/retail_basic.yaml
python -m csv_generator.generator.cli generate --schema csv_generator/schemas/retail_basic.yaml --rows 1000 --seed 42 --out csv_generator/output/retail_basic
python -m csv_generator.generator.cli validate --schema csv_generator/schemas/retail_basic.yaml --rows 100 --seed 42 --out csv_generator/output/retail_basic_validation.json
```

## CLI commands

The generator CLI supports:
- `describe`
- `generate`
- `validate`

Shared flags:
- `--schema PATH`
- `--out PATH` (required for `generate`, optional for `describe`, report path/dir for `validate`)
- `--seed INT`
- `--verbose` (prints full traceback on failures)

By default, errors are concise and do not print Python stack traces. Use `--verbose` (or set `DEBUG=1`) for full tracebacks.

Schema paths are resolved relative to your current working directory.

## Schema DSL (YAML/JSON)

Top-level keys:
- `dataset`: dataset name
- `seed`: optional default seed
- `tables`: mapping of table names to specs
- `relationships`: foreign keys and optional cardinality controls

Column fields:
- `name`, `type`
- distribution params (e.g., `distribution`, `min`, `max`, `mean`, `std`)
- `constraints` (`primary_key`, `unique`, `not_null`, `pattern`, `allowed_values`, `monotonic_increasing`)
- `computed` expression that references prior columns in the same row

Corruption toggles per table:
- `missing_rate` / `missing_by_column`
- `duplicate_rate`
- `outlier_rate`
- optional `type_noise`

Example relationship:

```yaml
relationships:
  - parent_table: customers
    parent_key: customer_id
    child_table: orders
    child_key: customer_id
    min_children: 0
    max_children: 8
```

## Dependency notes

- `faker` is optional at runtime; if unavailable, the generator uses a deterministic built-in fallback for name/email/city/state fields.
- `pyyaml` is recommended for YAML schema parsing. Without it, JSON-compatible schemas still work; non-JSON YAML will error with an actionable install message.

## Breaking changes

- Added new `validate` subcommand that emits a structured JSON validation report.
- CLI now catches common runtime/schema errors and returns concise error messages by default.
