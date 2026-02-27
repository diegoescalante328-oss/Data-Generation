# Architecture

This repository uses a **shared engine + format frontends** architecture, with a bootstrap runner as the default execution path (**Option B**).

## High-level layout

- `shared/`
  - Cross-generator components:
    - schema loading/parsing (`shared/schema_dsl/parser.py`)
    - table generation engine (`shared/schema_dsl/engine.py`)
    - value generation/distributions (`shared/distributions/`)
    - constraints and dataset checks (`shared/constraints/`)
    - relationship handling/FK assignment (`shared/relationships/`)
    - deterministic RNG derivation (`shared/io/rng.py`)
    - profile-based corruption/noise (`shared/corruption/profiles.py`)
    - validation report writer (`shared/cli/common.py`, `shared/io/reporting.py`)
- `generators/`
  - Format-specific CLIs and I/O adapters, each following `describe | generate | validate`:
    - `generators/csv_generator` (wrapper frontend)
    - `generators/json_generator` (JSON/NDJSON)
    - `generators/parquet_generator`
    - `generators/sqlite_seed`
    - `generators/event_stream_generator`
- `csv_generator/`
  - Legacy richer engine (schema + generation features beyond shared core).
  - `generators/csv_generator` is a thin compatibility wrapper that delegates to this legacy package.
- `all-in-one/datagen_bootstrap.py`
  - Recommended runner that provisions `.venv`, installs dependencies, and dispatches to generator CLIs.

## Execution model (Option B bootstrap)

Recommended command surface:

```bash
python3 all-in-one/datagen_bootstrap.py <describe|generate|validate> --format ... --schema ... [--out ...]
```

Why this exists:

- avoids global package installation,
- keeps dependency management local and reproducible (`<repo>/.venv`),
- centralizes routing/flags across generators,
- supports multiple backends without per-module environment setup.

## Data flow

```text
schema file (YAML/JSON)
        |
        v
schema parser (shared/schema_dsl/parser.py)
        |
        v
generation engine (shared or csv legacy engine)
  - RNG derivation
  - constraints checks
  - relationship assignment
  - optional corruption profile
        |
        v
in-memory tables/events
        |
        v
format writer (CSV / JSON / NDJSON / Parquet / SQLite / stream NDJSON)
        |
        v
output artifact(s)
        |
        v
validator command
  - parseability checks
  - row-count checks
  - FK/integrity checks (format dependent)
  - deterministic regeneration checks (where implemented)
        |
        v
validation_report.json
```

## Shared engine responsibilities

The shared engine (`shared/schema_dsl/engine.py`) handles:

- table-by-table generation using deterministic derived RNGs,
- per-column value generation by declared type,
- basic constraint checks (required/non-null, min/max, allowed/pattern, uniqueness),
- foreign key population from parent tables,
- profile-driven data dirtiness (`fast`, `realistic`, `dirty`).

## Format frontends and validators

Each generator CLI provides:

- `describe`: schema summary,
- `generate`: produce format-specific outputs,
- `validate`: inspect outputs and emit `validation_report.json`.

Validator behavior is format-aware, for example:

- `sqlite_seed`: SQLite FK checks via `PRAGMA foreign_key_check`, table row counts.
- `json_generator`: output parseability + row count checks against regenerated tables.
- `parquet_generator`: file/dataset parseability + row count checks.
- `event_stream_generator`: ordering + required keys + deterministic replay checks.
- `csv_generator` wrapper: CSV row count and schema checks using legacy engine output.

## Determinism strategy

- Schema-level `seed` defines default reproducibility.
- CLI `--seed` overrides schema seed.
- Shared engine derives per-table RNG streams from `(seed, table_name)` to avoid cross-table coupling.
- Some validators regenerate expected data from the same seed and compare invariants (or full event sequences).

## Validation philosophy

Validation is designed to be:

- **artifact-aware**: confirm files/tables actually exist and parse,
- **schema-aware**: verify required columns and basic constraint/FK consistency,
- **reproducibility-aware**: use seed-based regeneration where useful,
- **report-first**: always write machine-readable `validation_report.json` for CI/automation.

## Non-goals (explicit)

- **Not targeting Option A**: no stdlib-only single-file architecture as primary workflow.
- **No embedding third-party source code** into the repo to avoid dependency installs.

Instead, the project standard is Option B bootstrap with local `.venv` dependency management.
