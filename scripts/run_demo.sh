#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "== Demostración SAP ECC -> SLT -> AWS Analytics =="

"$PYTHON_BIN" scripts/generate_copa_data.py

"$PYTHON_BIN" scripts/simulate_slt_extract.py data/source/copa_initial.csv --load-type initial
"$PYTHON_BIN" scripts/etl_copa.py --load-type initial
"$PYTHON_BIN" scripts/load_postgres.py data/processed/copa_initial_curated.csv

"$PYTHON_BIN" scripts/simulate_slt_extract.py data/source/copa_delta_001.csv --load-type delta
"$PYTHON_BIN" scripts/etl_copa.py --load-type delta
"$PYTHON_BIN" scripts/load_postgres.py data/processed/copa_delta_001_curated.csv

"$PYTHON_BIN" scripts/query_analytics.py

echo
echo "Demostración completada: carga inicial + delta sin información productiva."
