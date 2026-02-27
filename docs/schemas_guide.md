# Schema DSL Guide

This guide documents the schema formats currently used in this repository.

## Important: there are two active schema tracks

1. **Shared engine schemas** (used by `json_generator`, `parquet_generator`, `sqlite_seed`; and base parser utilities).
2. **CSV legacy engine schemas** (used by `csv_generator/` and the `generators/csv_generator` wrapper), with richer features such as computed columns and detailed corruption controls.

Both are loaded from YAML/JSON files, and both use top-level `dataset`, `seed`, `tables`, and optional `relationships`.

---

## Top-level keys

Common keys you will see:

- `dataset` *(string, required)*: dataset identifier.
- `seed` *(int, optional but recommended)*: deterministic default seed.
- `tables` *(mapping, required for table generators)*: table definitions.
- `relationships` *(list, optional)*: parent/child key mappings.

Additional keys may exist in generator-specific schemas (for example `output_mode` in JSON schemas, or `rows`/`late_events` for event-stream schemas).

---

## Table definition structure

Typical table block:

```yaml
tables:
  users:
    rows: 100
    columns:
      - name: user_id
        type: id
        constraints:
          unique: true
```

Table keys currently used in code:

- `rows`: per-table row count.
- `columns`: ordered list of column specs.
- `partition_by`: parquet writer partition columns (parquet frontend).
- `indexes`: sqlite DDL indexes (sqlite frontend).
- `corruption`: legacy CSV engine corruption configuration.

---

## Column types currently supported

### Shared engine (`shared/distributions/generators.py`)

- `id`
- `integer`
- `float`
- `categorical`
- `boolean`
- `datetime`
- `date`
- `string`
- `object` (nested fields list)
- fallback via `value` (for unknown types)

### Legacy CSV engine (`csv_generator/generator/core.py`)

- `id` (`id_mode: int|uuid`, optional `start`)
- `integer` (supports distributions)
- `float` (supports distributions + rounding)
- `categorical` (with `categories` + `weights`)
- `boolean` (`true_probability`)
- `date`
- `datetime`
- `string_pattern` (`prefix`, `width`)
- `name`, `email`, `city`, `state`
- `constant` (`value`)
- `computed` expression columns (`computed: <expression>`) 

---

## Constraints currently supported

### Shared constraints (`shared/constraints/rules.py`)

- `not_null`
- `allowed`
- `min`
- `max`
- `pattern`
- `unique` (enforced during generation when tracked)

### Legacy CSV constraints (`csv_generator/generator/constraints.py`)

- `not_null`
- `allowed_values`
- `min`
- `max`
- `pattern`
- `unique`
- `primary_key` (used by uniqueness tracking and corruption exclusions)
- `monotonic_increasing` (validated post-generation)

---

## Relationships format

All table generators use parent/child FK mapping:

```yaml
relationships:
  - parent_table: customers
    parent_key: customer_id
    child_table: orders
    child_key: customer_id
```

Legacy CSV engine supports additional relationship options:

- `min_children`
- `max_children`
- `lookup_columns` (copy parent columns onto child rows)

Example:

```yaml
relationships:
  - parent_table: parents
    parent_key: parent_id
    child_table: children
    child_key: parent_id
    min_children: 1
    max_children: 3
    lookup_columns:
      created_on: created_on
```

---

## Computed columns and distributions

### Computed columns (legacy CSV engine)

Supported via `computed: ...` expression strings, evaluated with row-local context.
Built-in helpers used by schemas include:

- `normal(mean, std)`
- `rand_days_after(start_iso, min_days, max_days)`
- basic `round`, `min`, `max`, `float`, `int`

### Numeric distributions

Legacy CSV engine supports:

- `uniform`
- `normal`
- `lognormal`
- `poisson`

Shared engine currently uses simple type-driven generation for `integer`/`float` and does not expose the full legacy distribution surface.

---

## Corruption / noise configuration

### Shared engine profile noise

Controlled by CLI/profile (`fast`, `realistic`, `dirty`) through `shared/corruption/profiles.py`:

- missingness injection
- optional duplicates/outlier knobs in profile defaults

### Legacy CSV table-level corruption

`table.corruption` supports:

- `missing_rate`
- `missing_by_column`
- `outlier_rate`
- `type_noise` (`rate`, `value`)
- `duplicate_rate`

---

## Schema library organization

Primary schema catalog lives at `csv_generator/schemas/` and includes:

- scale variants: `*_tiny.yaml`, `*_small.yaml`, `*_medium.yaml`, `*_large.yaml`
- baseline schemas (for example `retail_basic.yaml`, `hr_employees.yaml`, `web_events.yaml`)
- minimal CI schemas (for example `single_table_10_rows.yaml`, `two_tables_fk_minimal.yaml`, `constraints_minimal.yaml`, `computed_minimal.yaml`, `corruption_minimal.yaml`)

Generator-specific schema examples also exist under each module, such as:

- `generators/json_generator/schemas/web_events_ndjson.yaml`
- `generators/sqlite_seed/schemas/retail_basic_sqlite.yaml`
- `generators/parquet_generator/schemas/retail_basic_parquet.yaml`
- `generators/event_stream_generator/schemas/clickstream_stream.yaml`

### Choosing a schema by purpose

- **CI / unit smoke tests**: use minimal schemas (`single_table_10_rows`, `two_tables_fk_minimal`).
- **Demo / local iteration**: use `*_tiny` or `*_small` variants.
- **Performance / stress testing**: use `*_medium` or `*_large` variants.

---

## Worked example 1 (minimal FK schema)

```yaml
dataset: two_tables_fk_minimal
seed: 102
tables:
  parents:
    rows: 12
    columns:
      - name: parent_id
        type: id
        constraints:
          primary_key: true
          unique: true
      - name: created_on
        type: date
        start: '2024-01-01'
        end: '2024-01-15'
  children:
    rows: 24
    columns:
      - name: child_id
        type: id
        constraints:
          primary_key: true
          unique: true
      - name: parent_id
        type: integer
      - name: created_on
        type: date
        start: '2024-01-01'
        end: '2024-01-15'
relationships:
  - parent_table: parents
    parent_key: parent_id
    child_table: children
    child_key: parent_id
    min_children: 1
    max_children: 3
    lookup_columns:
      created_on: created_on
```

## Worked example 2 (single table, deterministic, weighted categorical)

```yaml
dataset: single_table_10_rows
seed: 101
tables:
  users:
    rows: 10
    columns:
      - name: user_id
        type: id
        constraints:
          primary_key: true
          unique: true
      - name: age
        type: integer
        distribution: normal
        mean: 35
        std: 8
        min: 18
        max: 70
      - name: country
        type: categorical
        categories: [US, CA, UK]
        weights: [0.6, 0.25, 0.15]
relationships: []
```

---

## Troubleshooting

### YAML vs JSON confusion

- The loaders accept YAML via `pyyaml`.
- JSON-formatted files are also accepted (including `.yaml` files that contain JSON objects).
- Prefer standard YAML syntax for readability and comments.

### Common schema errors

- Missing top-level `dataset` or `tables`.
- `tables` is empty or not a mapping.
- Relationship references a table/key that does not exist.
- Constraint names mismatch the engine track (`allowed` vs `allowed_values`).

### Validation failures you may see

- row-count mismatch between generated output and expected schema rows / `--rows` override,
- FK violations in child tables,
- parse errors in output files (invalid JSON/NDJSON, missing output artifact),
- deterministic checks failing when validating with a different seed than generation.
