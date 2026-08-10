#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "== SAP Analytics Migration bootstrap =="

command -v docker >/dev/null 2>&1 || { echo "ERROR: Docker no está disponible."; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "ERROR: Docker Compose no está disponible."; exit 1; }

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Creado .env desde .env.example"
fi

mkdir -p data/source data/processed logs
docker compose config >/dev/null
docker compose up -d

echo "Esperando servicios saludables..."
for attempt in {1..30}; do
  unhealthy="$(docker compose ps --format json | grep -c 'unhealthy\|starting' || true)"
  [[ "$unhealthy" == "0" ]] && break
  sleep 2
done

echo "Bootstrap completo. Ejecutá: ./scripts/run_demo.sh"
