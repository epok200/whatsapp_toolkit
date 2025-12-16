#!/usr/bin/env bash
set -euo pipefail

# Este script está pensado para macOS/Linux y para Windows vía Git Bash o WSL.
# NO intenta iniciar Docker Desktop/daemon por ti.

echo "[devtools] Iniciando el stack de Evolution API (Docker Compose)"
echo "[devtools] Abrir: http://localhost:8080/manager/"

docker compose down || true
docker compose up
