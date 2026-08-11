#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "== 1/4 · Infraestructura local reproducible =="
./scripts/bootstrap.sh

echo
echo "== 2/4 · Carga inicial e incremental CO-PA =="
./scripts/run_demo.sh

echo
echo "== 3/4 · Controles de entrega =="
./scripts/check.sh

echo
echo "== 4/4 · Estimación de costos =="
python3 scripts/calculate_monthly_cost.py

echo
echo "Commit demostrado: $(git rev-parse --short HEAD 2>/dev/null || echo 'sin información Git')"
echo "Defensa lista: arquitectura, demo, controles y costos verificados."
