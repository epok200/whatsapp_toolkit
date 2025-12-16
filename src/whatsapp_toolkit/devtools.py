from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import subprocess
from typing import Optional, Tuple
from colorstreak import Logger as log


_DOTENV_EXAMPLE = """# =========================================
# WhatsApp Toolkit (Python) - configuración local/dev
# =========================================
# NOTA:
# - Este es un archivo de EJEMPLO. Cópialo a `.env` y completa tus secretos.
# - NO subas `.env` al repositorio.

# --- Ajustes del cliente Python ---
WHATSAPP_API_KEY=YOUR_EVOLUTION_API_KEY
WHATSAPP_INSTANCE=fer
WHATSAPP_SERVER_URL=http://localhost:8080/

# --- Secretos compartidos de Docker Compose ---
AUTHENTICATION_API_KEY=YOUR_EVOLUTION_API_KEY
POSTGRES_PASSWORD=change_me
"""

_DOCKER_COMPOSE = """services:
    evolution-api:
        image: evoapicloud/evolution-api:v{VERSION}
        restart: always
        ports:
            - "8080:8080"
        volumes:
            - evolution-instances:/evolution/instances

        environment:
            # =========================
            # Identidad principal del servidor
            # =========================
            - SERVER_URL=localhost
            - LANGUAGE=en
            - CONFIG_SESSION_PHONE_CLIENT=Evolution API
            - CONFIG_SESSION_PHONE_NAME=Chrome

            # =========================
            # Telemetría (apagada por defecto)
            # =========================
            - TELEMETRY=false
            - TELEMETRY_URL=

            # =========================
            # Autenticación (el secreto permanece en .env / --env-file)
            # =========================
            - AUTHENTICATION_TYPE=apikey
            - AUTHENTICATION_API_KEY=${AUTHENTICATION_API_KEY}
            - AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES=true

            # =========================
            # Base de datos (configuración interna del stack)
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
            # Caché Redis (configuración interna del stack)
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

# Este script está pensado para macOS/Linux y para Windows vía Git Bash o WSL.
# NO intenta iniciar Docker Desktop/daemon por ti.

echo "[devtools] Iniciando el stack de Evolution API (Docker Compose)"
echo "[devtools] Abrir: http://localhost:8080/manager/"

docker compose down || true
docker compose up${UP_ARGS}
"""


# -----------------------------
# API pública
# -----------------------------

@dataclass(frozen=True)
class LocalEvolutionPaths:
        root: Path
        compose_file: Path
        env_example_file: Path
        wakeup_sh: Path


def init_local_evolution(
        path: str | os.PathLike[str] = ".",
        overwrite: bool = False,
        verbose: bool = True,
        version: str = "2.3.7",
) -> LocalEvolutionPaths:
        """Crea plantillas de desarrollo local en el directorio indicado.

        Crea (solo cuando faltan, a menos que overwrite=True):
        - docker-compose.yml
        - .env.example
        - wakeup_evolution.sh

        No crea `.env` para evitar subir secretos por accidente.
        """
        root = Path(path).expanduser().resolve()
        root.mkdir(parents=True, exist_ok=True)

        compose_file = root / "docker-compose.yml"
        env_example_file = root / ".env.example"
        wakeup_sh = root / "wakeup_evolution.sh"

        _write_text(compose_file, _DOCKER_COMPOSE.replace("{VERSION}", version), overwrite=overwrite)
        _write_text(env_example_file, _DOTENV_EXAMPLE, overwrite=overwrite)
        _write_text(wakeup_sh, _WAKEUP_SH.replace("${UP_ARGS}", ""), overwrite=overwrite)

        # Hacer que el script .sh sea ejecutable en sistemas tipo Unix
        try:
                wakeup_sh.chmod(wakeup_sh.stat().st_mode | 0o111)
        except Exception:
                pass

        if verbose:
                log.info(f"[devtools] ✅ Plantillas listas en: {root}")
                log.info("[devtools] Archivos:")
                log.library(f"  - {compose_file.name}")
                log.library(f"  - {env_example_file.name}  (cópialo a .env y completa los secretos)")
                log.library(f"  - {wakeup_sh.name}         (macOS/Linux; Windows vía Git Bash/WSL)")
                log.info("[devtools] Requisitos:")
                log.info("  - Docker instalado y ejecutándose (daemon/desktop)")
                log.info("  - Ejecutar desde el directorio que contiene docker-compose.yml")

        return LocalEvolutionPaths(
                root=root,
                compose_file=compose_file,
                env_example_file=env_example_file,
                wakeup_sh=wakeup_sh,
        )


def local_evolution(path: str | os.PathLike[str] = ".") -> "LocalEvolutionStack":
        """Devuelve un objeto controlador para el stack local de Evolution en `path`."""
        root = Path(path).expanduser().resolve()
        paths = LocalEvolutionPaths(
                root=root,
                compose_file=root / "docker-compose.yml",
                env_example_file=root / ".env.example",
                wakeup_sh=root / "wakeup_evolution.sh",
        )
        return LocalEvolutionStack(paths)


class LocalEvolutionStack:
        """Pequeño wrapper alrededor de Docker Compose para el stack de Evolution."""

        def __init__(self, paths: LocalEvolutionPaths):
                self.paths = paths

        def start(self, detached: bool = False, build: bool = False, verbose: bool = True) -> None:
                """Inicia el stack (docker compose up)."""
                cmd = _compose_cmd()
                env_file, warn = _pick_env_file(self.paths.root)
                if warn and verbose:
                        log.info(warn)

                args = [*cmd, "--env-file", str(env_file), "up"]
                if build: # Reconstruye imágenes antes de iniciar
                        args.append("--build")
                if detached: # Esto hace que Docker Compose se ejecute en segundo plano
                        args.append("-d")

                if verbose:
                        log.info("[devtools] Iniciando el stack de Evolution...")
                        log.info("[devtools] Abrir: http://localhost:8080/manager/")

                _run(args, cwd=self.paths.root)

                if detached and verbose:
                        log.info("[devtools] ✅ Stack iniciado (en segundo plano). Usa .logs(follow=True) para ver logs.")

        def stop(self, verbose: bool = True) -> None:
                """Detiene contenedores sin eliminar volúmenes (docker compose stop)."""
                cmd = _compose_cmd()
                env_file, warn = _pick_env_file(self.paths.root)
                if warn and verbose:
                        log.info(warn)

                if verbose:
                        log.info("[devtools] Deteniendo el stack de Evolution...")
                _run([*cmd, "--env-file", str(env_file), "stop"], cwd=self.paths.root)

        def down(self, volumes: bool = False, verbose: bool = True) -> None:
                """Desmonta el stack (docker compose down)."""
                cmd = _compose_cmd()
                env_file, warn = _pick_env_file(self.paths.root)
                if warn and verbose:
                        log.info(warn)

                args = [*cmd, "--env-file", str(env_file), "down"]
                if volumes:
                        args.append("-v")

                if verbose:
                        log.info("[devtools] Bajando el stack de Evolution...")
                _run(args, cwd=self.paths.root)

        def logs(self, service: Optional[str] = None, follow: bool = True) -> None:
                """Muestra logs (docker compose logs).
                args:
                    service: nombre del servicio (evolution-api, evolution-postgres, evolution-redis)
                    follow: si True, sigue mostrando logs en tiempo real (como `tail -f`)
                """
                
                cmd = _compose_cmd()
                env_file, warn = _pick_env_file(self.paths.root)
                if warn:
                        log.info(warn)

                args = [*cmd, "--env-file", str(env_file), "logs"]
                if follow:
                        args.append("-f")
                if service:
                        args.append(service)
                _run(args, cwd=self.paths.root)


# -----------------------------
# Internos
# -----------------------------

def _looks_like_env_file(text: str) -> bool:
        """Heurística: un .env válido contiene mayormente líneas CLAVE=VALOR (se permiten comentarios)."""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        if not lines:
                return True
        ok = 0
        for ln in lines[:50]:
                if "=" in ln and not ln.startswith('"""') and not ln.startswith("from ") and not ln.startswith("import "):
                        ok += 1
        return ok >= max(1, min(3, len(lines)))


def _pick_env_file(root: Path) -> Tuple[Path, Optional[str]]:
        """Selecciona un archivo env para docker compose.

        Prefiere `.env` cuando existe y parece válido. Si `.env` existe pero parece incorrecto,
        usa `.env.example` y devuelve un mensaje de advertencia.
        """
        env_path = root / ".env"
        example_path = root / ".env.example"

        if env_path.exists():
                try:
                        sample = env_path.read_text(encoding="utf-8", errors="ignore")[:4000]
                except Exception:
                        sample = ""
                if _looks_like_env_file(sample):
                        return env_path, None

                warn = (
                        "[devtools] ⚠️  Se encontró un archivo .env pero no parece contener líneas CLAVE=VALOR. "
                        "Docker Compose puede fallar al parsearlo.\n"
                        "[devtools]     Solución: renombra/elimina ese .env y crea uno real a partir de .env.example."
                )
                if example_path.exists():
                        return example_path, warn
                return env_path, warn

        if example_path.exists():
                warn = (
                        "[devtools] ℹ️  No se encontró .env; usando .env.example.\n"
                        "[devtools]     Consejo: copia .env.example -> .env y configura AUTHENTICATION_API_KEY / POSTGRES_PASSWORD."
                )
                return example_path, warn

        return env_path, None


def _write_text(path: Path, content: str, overwrite: bool) -> None:
        if path.exists() and not overwrite:
                return
        path.write_text(content, encoding="utf-8")


def _run(args: list[str], cwd: Path) -> None:
        try:
                subprocess.run(args, cwd=str(cwd), check=True)
        except FileNotFoundError as e:
                raise RuntimeError(
                        "Docker no está instalado o no está en PATH. Instala Docker Desktop (macOS/Windows) o Docker Engine (Linux)."
                ) from e
        except subprocess.CalledProcessError as e:
                raise RuntimeError(
                        f"El comando de Docker Compose falló (exit={e.returncode}).\n"
                        f"Comando: {' '.join(args)}\n"
                        "Consejo: si el error menciona el parseo de .env, abre tu .env y asegúrate de que contenga solo líneas CLAVE=VALOR.\n"
                        "También puedes eliminar/renombrar un .env roto y copiar .env.example -> .env."
                ) from e


def _compose_cmd() -> list[str]:
        """Devuelve el mejor comando compose disponible.

        Prefiere: `docker compose ...`
        Alternativa: `docker-compose ...`
        """
        docker = shutil.which("docker")
        if docker:
                try:
                        subprocess.run(
                                [docker, "compose", "version"],
                                check=True,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                        )
                        return [docker, "compose"]
                except Exception:
                        pass

        docker_compose = shutil.which("docker-compose")
        if docker_compose:
                return [docker_compose]

        return ["docker", "compose"]