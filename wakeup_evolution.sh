#!/usr/bin/env bash
set -euo pipefail

clear
clear

echo "Levantando el servicio de Evolution-API-CLI"

# Detener stack previo (si existe)
docker compose down

# Levantar en background
echo "Servicio levantado en http://localhost:8080/manager/ "

docker compose up --build

# Esperar a que el HTTP de Evolution esté listo (best-effort)
# for i in {1..60}; do
#   if curl -fsS "http://localhost:8080" >/dev/null 2>&1; then
#     echo "✅ Evolution API está respondiendo."
#     exit 0
#   fi
#   sleep 1
# done

# echo "⚠️  Evolution API tardó más de lo esperado en responder. Revisa logs con: docker compose logs -f evolution-api"
# exit 1
