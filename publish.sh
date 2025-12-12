#!/usr/bin/env bash
set -e

export $(grep -v '^#' .env.secret | xargs)

# Leer versión desde pyproject.toml
VERSION=$(uv run python get_version.py)

rm -rf dist
uv build
uv publish

echo "✅ Published whatsapp-toolkit ${VERSION} to PyPI."