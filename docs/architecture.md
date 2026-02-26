# Architecture

- `shared/` contains reusable schema parsing, RNG, distributions, constraints, corruption, relationships, and validation reporting.
- `generators/*` modules provide format-specific CLIs and writers while reusing `shared.schema_dsl.engine.generate_tables`.
- Existing `csv_generator/` remains intact; `generators/csv_generator/` is a thin compatibility wrapper.

## Add a new generator
1. Create `generators/<module>/generator/cli.py` with `generate/describe/validate`.
2. Reuse `shared/schema_dsl/parser.py` and `shared/schema_dsl/engine.py`.
3. Add schema examples and smoke tests under module `tests/`.

## Tests
- Module-level smoke tests under each generator.
- Shared reproducibility test under `shared/tests`.
