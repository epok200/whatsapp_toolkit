import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
import sys
from colorstreak import Logger as log

from whatsapp_toolkit.devtools.templates import (
    _DOCKER_COMPOSE,
    _DOCKERFILE,
    _DOTENV_EXAMPLE,
    _MAIN_WEBHOOK_PY,
    _REQUIREMENTS_TXT,
    _WAKEUP_SH,
)



# -----------------------------
# API pública
# -----------------------------

@dataclass(frozen=True)
class LocalEvolutionPaths:
    root: Path
    compose_file: Path
    env_example_file: Path
    wakeup_sh: Path
    requirements_txt: Path
    # Archivos del webhook
    docker_file_webhook: Path
    main_webhook_py: Path
    env_webhook_dir: Path


def init_local_evolution(path: str | os.PathLike[str] = ".", overwrite: bool = False, verbose: bool = True, version: str = "2.3.7",) -> LocalEvolutionPaths:
    """Crea plantillas de desarrollo local en el directorio indicado.

    Crea (solo cuando faltan, a menos que overwrite=True):
    - docker-compose.yml
    - .env.example
    - wakeup_evolution.sh

    No crea `.env` para evitar subir secretos por accidente.
    """
    root = Path(path).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    # Archivos globales
    compose_file = root / "docker-compose.yml"
    env_example_file = root / ".env.example"
    wakeup_sh = root / "wakeup_evolution.sh"
    requirements_txt = root / "requirements.txt"
    
    
    # Archivos adicionales para el webhook
    docker_file_webhook = root / "Dockerfile"
    main_webhook_py = root /"webhook"/ "main_webhook.py"
    env_webhook_dir = root / "webhook"/ ".env"

    _write_text(compose_file, _DOCKER_COMPOSE.replace("{VERSION}", version), overwrite=overwrite)
    _write_text(env_example_file, _DOTENV_EXAMPLE, overwrite=overwrite)
    _write_text(wakeup_sh, _WAKEUP_SH.replace("${UP_ARGS}", ""), overwrite=overwrite)
    _write_text(requirements_txt, _REQUIREMENTS_TXT, overwrite=overwrite)
    
    # Archivos del webhook
    _write_text(docker_file_webhook, _DOCKERFILE, overwrite=overwrite)
    _write_text(main_webhook_py, _MAIN_WEBHOOK_PY, overwrite=overwrite)
    _write_text(env_webhook_dir, _DOTENV_EXAMPLE, overwrite=overwrite)

    # Hacer que el script .sh sea ejecutable en sistemas tipo Unix
    try:
        wakeup_sh.chmod(wakeup_sh.stat().st_mode | 0o111)
    except Exception:
            pass

    if verbose:
        log.info(f"[devtools] ✅ Plantillas listas en: {root}")
        log.info("[devtools] Archivos:")
        log.library(f"  - {compose_file.name}")
        log.library(f"  - {docker_file_webhook.name}    (Dockerfile para el webhook)")
        log.library(f"  - {env_example_file.name}  (cópialo a .env y completa los secretos)")
        log.library(f"  - {wakeup_sh.name}         (macOS/Linux; Windows vía Git Bash/WSL)")
        log.library(f"  - webhook/{main_webhook_py.name} (ejemplo de webhook)")
        log.library("  - webhook/.env              (configuración del webhook; copia y completa secretos)")
        log.library(f"  - {requirements_txt.name}   (dependencias del webhook)")
        log.info("[devtools] Requisitos:")
        log.info("  - Docker instalado y ejecutándose (daemon/desktop)")
        log.info("  - Ejecutar desde el directorio que contiene docker-compose.yml")

    return LocalEvolutionPaths(
        root=root,
        compose_file=compose_file,
        env_example_file=env_example_file,
        wakeup_sh=wakeup_sh,
        requirements_txt=requirements_txt,
        # Archivos del webhook
        docker_file_webhook=docker_file_webhook,
        main_webhook_py=main_webhook_py,
        env_webhook_dir=env_webhook_dir,
    )


def local_evolution(path: str | os.PathLike[str] = ".") -> "LocalEvolutionStack":
    """Devuelve un objeto controlador para el stack local de Evolution en `path`."""
    root = Path(path).expanduser().resolve()
    paths = LocalEvolutionPaths(
        root=root,
        compose_file=root / "docker-compose.yml",
        env_example_file=root / ".env.example",
        wakeup_sh=root / "wakeup_evolution.sh",
        requirements_txt=root / "requirements.txt",
        # Archivos del webhook
        docker_file_webhook=root / "Dockerfile",
        main_webhook_py=root / "webhook" / "main_webhook.py",
        env_webhook_dir=root / "webhook" / ".env",
    )
    return LocalEvolutionStack(paths)


class LocalEvolutionStack:
    """Pequeño wrapper alrededor de Docker Compose para el stack de Evolution."""

    def __init__(self, paths: LocalEvolutionPaths):
        self.paths = paths

    def start(self, detached: bool = True, build: bool = False, verbose: bool = True) -> None:
        """Inicia el stack (docker compose up)."""
        cmd = _compose_cmd()
        env_file, warn = _pick_env_file(self.paths.root)
        if warn and verbose:
            log.warning(warn)

        args = [*cmd, "--env-file", str(env_file), "up"]
        if build: # Reconstruye imágenes antes de iniciar
            args.append("--build")
        if detached: # Esto hace que Docker Compose se ejecute en segundo plano
            args.append("-d")

        if verbose:
            log.info("[devtools] Iniciando el stack de Evolution...")
        
        _run(args, cwd=self.paths.root)

        log.info("[devtools] Abrir: http://localhost:8080/manager/")
        if detached and verbose:
            log.info("[devtools] ✅ Stack iniciado (en segundo plano). Usa 'wtk evo logs' para ver logs.")


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


    def logs(self, service: list[str], follow: bool = True) -> None:
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
            args.extend(service)
            
        _run(args, cwd=self.paths.root, verbose=True)


# -----------------------------
# Internos
# -----------------------------


def _platform() -> str:
    """Devuelve el nombre del sistema operativo actual."""
    p = sys.platform.lower()
    if p.startswith("win"):
        return "windows"
    if p.startswith("linux"):
        return "linux"
    if p.startswith("darwin"):
        return "mac"
    return "unknown"


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
            "[devtools] ℹ️  No se encontró .env; usando .env.example."
            "[devtools]     Consejo: copia .env.example -> .env y configura AUTHENTICATION_API_KEY / POSTGRES_PASSWORD."
        )
        return example_path, warn

    return env_path, None


def _write_text(path: Path, content: str, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)  # Verificamos que el directorio exista
    if path.exists() and not overwrite:
            return
    path.write_text(content, encoding="utf-8")


def _run(args: list[str], cwd: Path, verbose: bool = True) -> None:
    try:
        subprocess.run(
            args, 
            cwd=str(cwd), 
            check=True,
            # Silenciamos salida si no es verbose
            stdout=None if verbose else subprocess.DEVNULL,
            stderr=None if verbose else subprocess.DEVNULL,
            # text para evitar problemas con encoding
            text=True,
        )
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




def ensure_docker_daemon() -> None:
    """Falla temprano si Docker está instalado pero el daemon no responde.

    No todos los setups tienen el binario `docker` disponible (p.ej. algunos `docker-compose` antiguos),
    así que este check es best-effort.
    """
    
    docker = shutil.which("docker")
    if not docker:
        return

    try:
        subprocess.run(
            [docker, "info"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        subprocess_docker_error = (e.stderr or "").strip()
        
        hint = (
            "Docker está instalado pero no parece estar corriendo (daemon inaccesible).\n"
            "- macOS: abre Docker Desktop y espera a que diga 'Running'.\n" if _platform() == "mac" else ""
            "- Linux: intenta 'sudo systemctl start docker' y 'sudo systemctl status docker'.\n" if _platform() == "linux" else ""
            "- Windows: abre Docker Desktop y espera a que diga 'Running'.\n" if _platform() == "windows" else ""
            "Luego vuelve a intentar el comando."
        )
        if subprocess_docker_error:
            hint += f"\nDetalle: {subprocess_docker_error}"
        raise RuntimeError(hint) from e
