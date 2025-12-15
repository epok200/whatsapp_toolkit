#!/usr/bin/env bash
set -euo pipefail

# This script is intended for macOS/Linux and for Windows via Git Bash or WSL.
# It does NOT try to start Docker Desktop/daemon for you.

echo "[devtools] Starting Evolution API stack (Docker Compose)"
echo "[devtools] Open: http://localhost:8080/manager/"

docker compose down || true
docker compose up
