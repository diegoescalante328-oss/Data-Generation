#!/usr/bin/env bash
set -euo pipefail

python -m csv_generator.generator.cli generate \
  --schema csv_generator/schemas/retail_basic.yaml \
  --rows 1000 \
  --seed 42 \
  --out csv_generator/output/retail_basic
