#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

OK=0
WARN=0
pass() { echo "OK   $1"; OK=$((OK + 1)); }
warn() { echo "WARN $1"; WARN=$((WARN + 1)); }

docker compose config >/dev/null 2>&1 && pass "compose config válido" || warn "compose config inválido"

for script in scripts/*.py; do
  python3 -m py_compile "$script" 2>/dev/null && pass "$script sintaxis ok" || warn "$script tiene errores"
done

docker compose ps --services --filter status=running | grep -q postgres \
  && docker compose exec -T postgres pg_isready -U analytics_app -d analytics -q \
  && pass "postgres responde" || warn "postgres no responde"

docker compose ps --services --filter status=running | grep -q localstack \
  && curl -fsS http://localhost:4566/_localstack/health >/dev/null \
  && pass "localstack responde" || warn "localstack no responde"

python3 -m pytest -q && pass "pytest pasa" || warn "pytest falló"

echo "Resultado: ${OK} OK / ${WARN} WARN"
[[ "$WARN" == "0" ]]
