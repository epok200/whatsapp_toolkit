"""Developer tools for spinning up a local Evolution API stack.

Design goals:
- **Zero side-effects on import** (nothing is created or executed unless explicitly called).
- Cross-platform: works on macOS/Linux/Windows by using Python + Docker CLI.
- Safe by default: generates `.env.example` (NOT `.env`) so secrets don't get committed by accident.

Typical usage:

    from whatsapp_toolkit import devtools

    devtools.init_local_evolution(path=".")
    stack = devtools.local_evolution(path=".")
    stack.start(detached=False)

"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import subprocess
from typing import Optional


# -----------------------------
# Templates (written on demand)
# -----------------------------

_DOTENV_EXAMPLE = """# =========================================
# WhatsApp Toolkit (Python) - local/dev config
# =========================================
# NOTE:
# - This is an EXAMPLE file. Copy it to `.env` and fill your secrets.
# - Do NOT commit `.env`.

# --- Python client settings ---
WHATSAPP_API_KEY=YOUR_EVOLUTION_API_KEY
WHATSAPP_INSTANCE=fer
# WHATSAPP_SERVER_URL=https://evo.apps.tu-dominio.com/   # remote server (optional)
WHATSAPP_SERVER_URL=http://localhost:8080/

# --- Docker Compose shared secrets ---
AUTHENTICATION_API_KEY=YOUR_EVOLUTION_API_KEY
POSTGRES_PASSWORD=change_me
"""

_DOCKER_COMPOSE = """services:
  evolution-api:
    image: evoapicloud/evolution-api:v2.3.7
    restart: always
    ports:
      - "8080:8080"
    volumes:
      - evolution-instances:/evolution/instances

    environment:
      # =========================
      # Core server identity
      # =========================
      - SERVER_URL=localhost
      - LANGUAGE=en
      - CONFIG_SESSION_PHONE_CLIENT=Evolution API
      - CONFIG_SESSION_PHONE_NAME=Chrome

      # =========================
      # Telemetry (off by default)
      # =========================
      - TELEMETRY=false
      - TELEMETRY_URL=

      # =========================
      # Auth (secret stays in .env)
      # =========================
      - AUTHENTICATION_TYPE=apikey
      - AUTHENTICATION_API_KEY=${AUTHENTICATION_API_KEY}
      - AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES=true

      # =========================
      # Database (internal stack config)
      # =========================
      - DATABASE_ENABLED=true
      - DATABASE_PROVIDER=postgresql
      - DATABASE_CONNECTION_URI=postgresql://postgresql:${POSTGRES_PASSWORD}@evolution-postgres:5432/evolution
      - DATABASE_SAVE_DATA_INSTANCE=true
      - DATABASE_SAVE_DATA_NEW_MESSAGE=true
      - DATABASE_SAVE_MESSAGE_UPDATE=true
      - DATABASE_SAVE_DATA_CONTACTS=true
      - DATABASE_SAVE_DATA_CHATS=true
      - DATABASE_SAVE_DATA_LABELS=true
      - DATABASE_SAVE_DATA_HISTORIC=true

      # =========================
      # Redis cache (internal stack config)
      # =========================
      - CACHE_REDIS_ENABLED=true
      - CACHE_REDIS_URI=redis://evolution-redis:6379
      - CACHE_REDIS_PREFIX_KEY=evolution
      - CACHE_REDIS_SAVE_INSTANCES=true

  evolution-postgres:
    image: postgres:16-alpine
    restart: always
    volumes:
      - evolution-postgres-data:/var/lib/postgresql/data

    environment:
      # Database credentials for the internal Postgres container
      - POSTGRES_DB=evolution
      - POSTGRES_USER=postgresql
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

  evolution-redis:
    image: redis:alpine
    restart: always
    volumes:
      - evolution-redis-data:/data


volumes:
  evolution-instances:
  evolution-postgres-data:
  evolution-redis-data:
"""

_WAKEUP_SH = """#!/usr/bin/env bash
set -euo pipefail

clear || true
clear || true

echo "Levantando el servicio de Evolution API (Docker Compose)"

docker compose down || true

echo "Servicio levantándose... abre: http://localhost:8080/manager/"

docker compose up${UP_ARGS}

echo "✅ Stack listo (si estás en modo detached)."
"""

_WAKEUP_PS1 = """#requires -Version 5.1
$ErrorActionPreference = 'Stop'

Write-Host "Levantando el servicio de Evolution API (Docker Compose)" -ForegroundColor Cyan

try { docker compose down | Out-Null } catch { }

Write-Host "Servicio levantándose... abre: http://localhost:8080/manager/" -ForegroundColor Yellow

docker compose up ${UP_ARGS}

Write-Host "✅ Stack listo (si estás en modo detached)." -ForegroundColor Green
"""


# -----------------------------
# Public API
# -----------------------------

@dataclass(frozen=True)
class LocalEvolutionPaths:
    root: Path
    compose_file: Path
    env_example_file: Path
    wakeup_sh: Path
    wakeup_ps1: Path


def init_local_evolution(
    path: str | os.PathLike[str] = ".",
    overwrite: bool = False,
    verbose: bool = True,
) -> LocalEvolutionPaths:
    """Create local-dev templates in the given directory.

    Creates (only when missing unless overwrite=True):
    - docker-compose.yml
    - .env.example
    - wakeup_evolution.sh
    - wakeup_evolution.ps1

    It **does NOT** create `.env` to avoid accidentally committing secrets.
    """

    root = Path(path).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    compose_file = root / "docker-compose.yml"
    env_example_file = root / ".env.example"
    wakeup_sh = root / "wakeup_evolution.sh"
    wakeup_ps1 = root / "wakeup_evolution.ps1"

    _write_text(compose_file, _DOCKER_COMPOSE, overwrite=overwrite)
    _write_text(env_example_file, _DOTENV_EXAMPLE, overwrite=overwrite)

    # scripts: we leave UP_ARGS placeholder so user can choose detached/build
    _write_text(wakeup_sh, _WAKEUP_SH.replace("${UP_ARGS}", ""), overwrite=overwrite)
    _write_text(wakeup_ps1, _WAKEUP_PS1.replace("${UP_ARGS}", ""), overwrite=overwrite)

    # Make sh executable on unix-ish systems
    try:
        wakeup_sh.chmod(wakeup_sh.stat().st_mode | 0o111)
    except Exception:
        pass

    if verbose:
        print(f"[devtools] ✅ Templates ready in: {root}")
        print("[devtools] Files:")
        print(f"  - {compose_file.name}")
        print(f"  - {env_example_file.name}  (copy to .env and fill secrets)")
        print(f"  - {wakeup_sh.name}         (macOS/Linux convenience)")
        print(f"  - {wakeup_ps1.name}        (Windows PowerShell convenience)")
        print("[devtools] Requirements:")
        print("  - Docker Desktop / Docker Engine installed")
        print("  - Run from the directory containing docker-compose.yml")

    return LocalEvolutionPaths(
        root=root,
        compose_file=compose_file,
        env_example_file=env_example_file,
        wakeup_sh=wakeup_sh,
        wakeup_ps1=wakeup_ps1,
    )


def local_evolution(path: str | os.PathLike[str] = ".") -> "LocalEvolutionStack":
    """Return a controller object for the local Evolution stack in `path`."""
    paths = LocalEvolutionPaths(
        root=Path(path).expanduser().resolve(),
        compose_file=Path(path).expanduser().resolve() / "docker-compose.yml",
        env_example_file=Path(path).expanduser().resolve() / ".env.example",
        wakeup_sh=Path(path).expanduser().resolve() / "wakeup_evolution.sh",
        wakeup_ps1=Path(path).expanduser().resolve() / "wakeup_evolution.ps1",
    )
    return LocalEvolutionStack(paths)


class LocalEvolutionStack:
    """Small wrapper around Docker Compose for the Evolution stack."""

    def __init__(self, paths: LocalEvolutionPaths):
        self.paths = paths

    def start(self, detached: bool = False, build: bool = False, verbose: bool = True) -> None:
        """Start the stack (docker compose up)."""
        cmd = _compose_cmd()
        args = [*cmd, "up"]
        if build:
            args.append("--build")
        if detached:
            args.append("-d")

        if verbose:
            print("[devtools] Starting Evolution stack...")
            print("[devtools] Open: http://localhost:8080/manager/")

        _run(args, cwd=self.paths.root)

        if detached and verbose:
            print("[devtools] ✅ Stack started (detached). Use .logs(follow=True) to tail logs.")

    def stop(self, verbose: bool = True) -> None:
        """Stop containers without removing volumes (docker compose stop)."""
        cmd = _compose_cmd()
        if verbose:
            print("[devtools] Stopping Evolution stack...")
        _run([*cmd, "stop"], cwd=self.paths.root)

    def down(self, volumes: bool = False, verbose: bool = True) -> None:
        """Tear down stack (docker compose down)."""
        cmd = _compose_cmd()
        args = [*cmd, "down"]
        if volumes:
            args.append("-v")
        if verbose:
            print("[devtools] Bringing down Evolution stack...")
        _run(args, cwd=self.paths.root)

    def logs(self, service: Optional[str] = None, follow: bool = True) -> None:
        """Show logs (docker compose logs)."""
        cmd = _compose_cmd()
        args = [*cmd, "logs"]
        if follow:
            args.append("-f")
        if service:
            args.append(service)
        _run(args, cwd=self.paths.root)


# -----------------------------
# Internals
# -----------------------------


def _write_text(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def _run(args: list[str], cwd: Path) -> None:
    try:
        subprocess.run(args, cwd=str(cwd), check=True)
    except FileNotFoundError as e:
        raise RuntimeError(
            "Docker is not installed or not on PATH. Install Docker Desktop (macOS/Windows) or Docker Engine (Linux)."
        ) from e


def _compose_cmd() -> list[str]:
    """Return the best available compose command.

    Prefers: `docker compose ...`
    Fallback: `docker-compose ...`
    """
    docker = shutil.which("docker")
    if docker:
        # Test whether `docker compose` is supported
        try:
            subprocess.run([docker, "compose", "version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return [docker, "compose"]
        except Exception:
            pass

    docker_compose = shutil.which("docker-compose")
    if docker_compose:
        return [docker_compose]

    # Nothing found
    return ["docker", "compose"]
