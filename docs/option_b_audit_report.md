# Option B Local-Only Methodology Audit Report

## A) Executive Summary

**Coherence status:** **Mostly** (core bootstrap path is solid, but several conflicting/legacy surfaces remain).

### Top 5 risk areas
1. **Legacy “single-file” runners still present and tested** (`datagen_onefile.py`, `all-in-one/csv_generator.py`), which conflicts with Option B-only direction.
2. **Docs/README drift**: multiple generator READMEs and root README still present direct module CLI usage without clear “optional/advanced only” framing.
3. **Dependency strategy is over-broad**: bootstrap always installs `requirements-dev.txt` (including heavy optional deps like `pyarrow`) for every format.
4. **Schema format/documentation mismatch**: several `*.yaml` files are JSON payloads; docs frame schemas as YAML-first and this can cause confusion.
5. **Path/root-detection inconsistency**: bootstrap uses robust marker-based detection, but sibling scripts (e.g., `run_examples.py`) still hardcode `parents[1]`.

---

## B) Findings

| Severity | Category | Location | Symptom | Why it matters for Option B local-only | Fix recommendation |
|---|---|---|---|---|---|
| **Blocker** | Entrypoint | `datagen_onefile.py`; `tests/test_onefile_runner_smoke.py` | A separate one-file runner is still active, tested, and branded as “Single-file Data-Generation runner”. It also uses `--system-site-packages`. | Conflicts with non-negotiable “Option B only” and risks leaking global packages into `.venv`. | Remove `datagen_onefile.py` and its smoke test, or deprecate hard (non-default, clearly unsupported). If kept temporarily, remove `--system-site-packages`, add root auto-detection, and mark as deprecated in help text. |
| **High** | Entrypoint / Docs | `all-in-one/csv_generator.py` | Script explicitly describes itself as “single-file, dependency-free generator”. | Reintroduces Option A style workflow and contradicts current execution methodology. | Remove file or move to `archive/` with deprecation notice; ensure no docs point to it. |
| **High** | Docs | `README.md`; `generators/*/README.md`; `csv_generator/schemas/README.md` | Multiple docs show direct `python -m generators...` usage as primary examples, not clearly labeled optional relative to bootstrap. | Users can bypass bootstrap and hit local env drift / import errors. | Standardize docs to: bootstrap first; direct module execution only in an “Advanced/Optional” section with explicit prerequisites and caveats. |
| **High** | Pathing | `all-in-one/run_examples.py` | Uses `Path(__file__).resolve().parents[1]` instead of shared root detection utility. | Brittle layout assumption diverges from required marker-based detection strategy. | Import and use `REPO_ROOT` from `bootstrap_lib` (or `find_repo_root`) and remove manual `parents[1]`. |
| **High** | Dependencies | `all-in-one/bootstrap_lib.py`; `requirements-dev.txt` | Bootstrap always includes `requirements-dev.txt`, which currently includes `pyarrow` for all formats. | Non-parquet runs can fail or become slow due to unnecessary optional dependency install. | Split runtime base deps from dev deps (e.g., `requirements-base.txt`), install base + format-specific only; keep `pyarrow` parquet-only. |
| **Medium** | Dependencies | `all-in-one/bootstrap_lib.py`; `shared/distributions/generators.py` | Bootstrap requires `faker` for json/sqlite/event_stream imports check, but shared engine for those formats does not import/use faker. | False-negative bootstrap validation and avoidable dependency burden in constrained environments. | Reduce `REQUIRED_IMPORTS` per format to actual runtime imports (`yaml` for schema loaders, `pyarrow` for parquet). |
| **Medium** | Dependencies / Isolation | `datagen_onefile.py` | Fallback dependency check imports modules in the launcher interpreter (`importlib.import_module`) rather than venv python. | Can incorrectly pass due to globally installed packages, violating local-only determinism. | Run import probes using `.venv` interpreter subprocess (same pattern as `bootstrap_lib.have_required_imports`). |
| **Medium** | Schemas | `generators/json_generator/schemas/web_events_ndjson.yaml`; `generators/sqlite_seed/schemas/retail_basic_sqlite.yaml`; `generators/parquet_generator/schemas/retail_basic_parquet.yaml`; `generators/event_stream_generator/schemas/clickstream_stream.yaml` | Files have `.yaml` extension but contain JSON objects. | Tooling/editor assumptions and docs expectations around YAML may confuse contributors and reviewers. | Convert to true YAML syntax (preferred) or explicitly document “JSON-in-YAML accepted” + optionally rename to `.json`. |
| **Medium** | Docs / Schemas | `docs/schemas_guide.md` | Guide says both tracks are YAML/JSON but does not call out that multiple “YAML” examples are actually JSON text in `.yaml` files. | Mismatch between stated conventions and on-disk examples erodes trust and onboarding clarity. | Add explicit subsection for accepted encodings and enforce one convention in CI (lint check). |
| **Medium** | Tests | `tests/test_onefile_runner_smoke.py` | CI coverage still validates deprecated onefile path. | Reinforces unsupported methodology and preserves drift over time. | Replace with stronger bootstrap contract tests (root detection, per-format dependency selection, venv isolation assertions). |
| **Low** | Pathing | `all-in-one/bootstrap_lib.py`; `datagen_onefile.py` | Both set `PYTHONPATH` explicitly. Works, but is a mutable env hack. | Can mask packaging/import issues and differ from installed package behavior. | Prefer `pip install -e .` (if package metadata exists) and run modules without `PYTHONPATH`; keep as fallback only with comment/rationale. |
| **Low** | Notebooks | `all-in-one/README.md` (troubleshooting note only) | Repo has no notebooks, but docs acknowledge kernel mismatch risk without a canonical setup command sequence. | Future notebook users may still hit `ModuleNotFoundError` if kernel is system Python. | Add explicit stable recipe: `./.venv/bin/python -m pip install ipykernel && ./.venv/bin/python -m ipykernel install --user --name data-generation-venv`, and tell users to launch Jupyter from `.venv`. |

---

## C) Must Fix Before Release

1. **Remove or hard-deprecate non-Option-B entrypoints** (`datagen_onefile.py`, `all-in-one/csv_generator.py`) and stop testing onefile runner.
2. **Normalize documentation** so bootstrap runner is the single default path everywhere; move direct module commands under clearly optional/advanced sections.
3. **Refactor dependency install plan** in bootstrap so non-required optional packages (notably `pyarrow`) are not installed for all formats.
4. **Unify root detection across all helper scripts** (especially `all-in-one/run_examples.py`) using marker-based detection from `bootstrap_lib`.
5. **Resolve schema convention drift** by converting JSON-in-`.yaml` samples to true YAML or documenting/renaming clearly.

---

## D) Nice to Have Improvements

- Add a CI lint step to detect `Path(__file__).parents[n]` in runtime scripts (allow in tests only).
- Add CI docs check to flag unqualified `pip install` snippets that are not within `.venv` context.
- Create `requirements-base.txt` + per-format lockfiles for faster deterministic local bootstrap.
- Add a docs style rule: every generator README starts with a bootstrap-run example, then optional direct-module examples.
- Add a short “Notebook Quick Setup” doc and link it from quickstart.
