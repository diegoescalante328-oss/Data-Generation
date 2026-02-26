# Schema DSL Guide

Shared YAML DSL supports `dataset`, `seed`, `tables`, `relationships`.

## Column types
- id, integer, float, categorical, boolean, date, datetime, string, object.

## Constraints
- `unique`, `not_null`, `min`, `max`, `allowed`, `pattern`.

## Computed columns
Legacy CSV module supports computed expressions; shared engine currently focuses on explicit columns only.

## Profiles
- `fast`: no default corruption.
- `realistic`: light missingness/duplicates.
- `dirty`: stronger missingness and duplicates by default.

Schema-level values still take precedence when modules implement additional overrides.
