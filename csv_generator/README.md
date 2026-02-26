# CSV Generator

A schema-driven synthetic dataset generator for analytics practice and testing.
It creates realistic CSV tables with configurable data types, distributions, constraints,
foreign-key relationships, computed columns, and optional dirty-data corruption.
The system is reproducible: use the same schema + seed and you get identical output.

## Install

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r csv_generator/requirements.txt
```

## CLI usage

```bash
python -m csv_generator.generator.cli generate --schema csv_generator/schemas/retail_basic.yaml --rows 1000 --seed 42 --out csv_generator/output/retail_basic
python -m csv_generator.generator.cli describe --schema csv_generator/schemas/web_events.yaml
```

## Schema DSL (YAML)

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

## Add a new schema

1. Create a new YAML file under `csv_generator/schemas/`.
2. Define tables, columns, and optional relationships/corruption.
3. Run `describe` to validate structure.
4. Run `generate` to produce CSVs in your chosen output folder.

## Notes on realism

- Weighted categorical values model skewed behavior.
- Numeric distributions support uniform, normal, lognormal, and poisson.
- Faker-backed fields (name/email/city/state) gracefully fall back if Faker is unavailable.
- Corruption controls let you simulate missing values, duplicates, outliers, and type noise.
