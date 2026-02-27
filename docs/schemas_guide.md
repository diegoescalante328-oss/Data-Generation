# Schema DSL Guide

For the complete CSV schema catalog (tiny/small/medium/large variants, CI-focused schemas, and Option B command examples), see:

- `csv_generator/schemas/README.md`

This guide documents core DSL primitives shared by generators.

## Top-level keys

- `dataset`: dataset name
- `seed`: deterministic default seed
- `tables`: mapping of table names to table specs
- `relationships`: list of FK/cardinality specs (optional)

## Table shape

Each table uses:

- `rows`
- `columns` (list of column dictionaries)
- optional table-level settings (`corruption`, etc.) when supported

## Column types

- `id`, `integer`, `float`, `categorical`, `boolean`, `date`, `datetime`, `string_pattern`, `name`, `email`, `city`, `state`, `constant`

## Distributions

Supported numeric distributions:

- `uniform`
- `normal`
- `lognormal`
- `poisson`

## Constraints

Common constraints include:

- `primary_key`
- `unique`
- `not_null`
- `monotonic_increasing`

## Computed columns

Use `computed` expressions for readable, row-local derived fields.

## Corruption

Optional table-level knobs:

- `missing_rate` / `missing_by_column`
- `duplicate_rate`
- `outlier_rate`
- `type_noise`
