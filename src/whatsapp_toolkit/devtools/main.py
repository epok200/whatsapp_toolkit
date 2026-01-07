from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Generic, Mapping, TypeVar, Callable, Iterator

from colorstreak import Logger as log

InitT = TypeVar("InitT", bound="BaseInitOptions")

# =========================
# PathConfig: una sola fuente de verdad
# =========================

@dataclass(frozen=True)
class PathConfig:
    project_root: Path

    @staticmethod
    def from_path(path: str | os.PathLike[str] = ".") -> "PathConfig":
        root = Path(path).expanduser().resolve()
        return PathConfig(project_root=root)

    @property
    def stack_root(self) -> Path:
        return self.project_root / ".wtk"

    def stack_dir(self, name: str) -> Path:
        """./project/.wtk/{name}/"""
        return self.stack_root / name
    
    def root_dir(self, name: str) -> Path:
        """./project/{name}/"""
        return self.project_root / name
    
    def rel(self, a: Path, start: Path) -> Path:
        return Path(os.path.relpath(a, start=start))



# =========================
# ParhFile: representa un archivo en un stack
# =========================
@dataclass(frozen=True)
class File:
    key: str
    filename: str
    parent: Path
    
    @classmethod
    def from_path(cls, key: str, filename: str, path: Path) -> "File":
        return cls(key=key, filename=filename, parent=path)
    
    @property
    def path(self) -> Path:
        return self.parent / self.filename

    def exists(self) -> bool:
        return self.path.exists()


# =========================
# Files: mapa de archivos en un stack    
# =========================    
@dataclass(frozen=True)
class Files(Mapping[str, File]):
    _items: dict[str, File]
    
    @classmethod
    def from_list(cls, files: Iterable[File]) -> "Files":
        items: dict[str, File] = {file.key: file for file in files}
        return cls(items)
    
    def __getitem__(self, key: str) -> File:
        return self._items[key]
    
    def __iter__(self) -> Iterator[str]:
        return iter(self._items)
    
    def __len__(self) -> int:
        return len(self._items)
    
    def get_path(self, key: str, default: Path | None = None) -> Path:
        f = self._items.get(key)
        if f:
            return f.path
        if default is None:
            raise KeyError(f"File with key '{key}' not found.")
        return default



# =========================
#  BaseStackSpec: define QUÉ archivos y QUÉ comandos
# =========================
PathBuilder = Callable[["PathConfig"], Files]

@dataclass(frozen=True)
class BaseStackSpec:
    name: str                  # "evolution", "webhook", etc.
    command_name: str          # "evo", "webhook", etc.
    default_port: int          # puerto default (0 = sin puerto)
    services: tuple[str, ...]  # para logs default
    paths: PathBuilder         # paths adicionales requeridos
    route_postfix: str = ""    # para healthcheck simple
    


# =========================
# BaseInitOptions: opciones para inicializar un stack
# =========================

@dataclass(frozen=True)
class BaseInitOptions:
    overwrite: bool = False
    verbose: bool = True



# ========================
# TemplateWriter: escribe archivos con overwrite
# ========================

class TemplateWriter:
    """Responsabilidad única: escribir archivos con overwrite."""
    @staticmethod
    def write(path: Path, content: str, overwrite: bool) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not overwrite:
            return
        path.write_text(content, encoding="utf-8")



# ========================
# BaseStackInitializer: crea layout + escribe templates
# ========================

class BaseStackInitializer(Generic[InitT]):
    """Responsabilidad única: crear layout + escribir templates para un stack."""
    def __init__(self, spec: BaseStackSpec, paths: PathConfig, writer: TemplateWriter | None = None):
        self.spec = spec
        self.paths = paths
        self.writer = writer or TemplateWriter()

    def stack_dir(self) -> Path:
        return self.paths.stack_dir(self.spec.name)
    
    def port(self) -> int:
        return self.spec.default_port
    
    def init(self, options: InitT) -> None:
        raise NotImplementedError()



# =========================
# 4) ComposeRunner: solo ejecuta docker compose
# =========================

class ComposeRunner:
    def __init__(self):
        self.cmd = self._compose_cmd()

    def up(self, cwd: Path, env_file: Path, background: bool, build: bool) -> None:
        args = [*self.cmd, "--env-file", str(env_file), "up"]
        if build:
            args.append("--build")
        if background:
            args.append("-d")
        self._run(args, cwd=cwd)

    def stop(self, cwd: Path, env_file: Path) -> None:
        self._run([*self.cmd, "--env-file", str(env_file), "stop"], cwd=cwd)

    def down(self, cwd: Path, env_file: Path, volumes: bool) -> None:
        args = [*self.cmd, "--env-file", str(env_file), "down"]
        if volumes:
            args.append("-v")
        self._run(args, cwd=cwd)

    def logs(self, cwd: Path, env_file: Path, services: Iterable[str], follow: bool) -> None:
        args = [*self.cmd, "--env-file", str(env_file), "logs"]
        if follow:
            args.append("-f")
        args.extend(list(services))
        self._run(args, cwd=cwd)

    @staticmethod
    def _run(args: list[str], cwd: Path) -> None:
        try:
            subprocess.run(args, cwd=str(cwd), check=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Docker Compose falló (exit={e.returncode}).\n"
                f"Comando: {' '.join(args)}"
            ) from e

    @staticmethod
    def _compose_cmd() -> list[str]:
        docker = shutil.which("docker")
        if docker:
            try:
                subprocess.run([docker, "compose", "version"], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return [docker, "compose"]
            except Exception:
                pass
        docker_compose = shutil.which("docker-compose")
        if docker_compose:
            return [docker_compose]
        return ["docker", "compose"]


# =========================
# 5) Stack (orquestador): une spec + runner + healthchecks simples
# =========================

class Stack:
    def __init__(self, spec: BaseStackSpec, paths: PathConfig, runner: ComposeRunner | None = None):
        self.spec = spec
        self.paths = paths
        self.runner = runner or ComposeRunner()

    @property
    def cwd(self) -> Path:
        return self.paths.stack_dir(self.spec.name)

    @property
    def env_file(self) -> Path:
        paths: Files = self.spec.paths(self.paths)
        env_file = paths.get_path("env_compose")
        return env_file

    def _health_check(self) -> None:
        missing: list[str] = []
        required: Files = self.spec.paths(self.paths)
        for key, file in required.items():
            if not file.exists():
                missing.append(f"{key}: {file.filename} (expected at {file.path})")
        if missing:
            raise RuntimeError(
                f"Faltan archivos del stack. Ejecuta primero el 'wtk {self.spec.command_name} init'.\n" +
                "\n".join(missing)
            )

    def up(self, background: bool = True, build: bool = False) -> None:
        self._health_check()
        
        log.info(f"[whatsapp-toolkit] Iniciando stack '{self.spec.name.upper()}' ...")
        log.info(f"[whatsapp-toolkit] Servicio levantado en 👉 [ http://localhost:{self.spec.default_port}{self.spec.route_postfix} ]")
        log.info(f"[whatsapp-toolkit] Para ver logs, usa: 'wtk {self.spec.command_name} logs'")
        
        self.runner.up(cwd=self.cwd, env_file=self.env_file, background=background, build=build)

    def stop(self) -> None:
        self._health_check()
        self.runner.stop(cwd=self.cwd, env_file=self.env_file)

    def down(self, volumes: bool = False) -> None:
        self._health_check()
        self.runner.down(cwd=self.cwd, env_file=self.env_file, volumes=volumes)

    def logs(self, services: list[str] | None = None, follow: bool = True) -> None:
        self._health_check()
        svc = services or list(self.spec.services)
        self.runner.logs(cwd=self.cwd, env_file=self.env_file, services=svc, follow=follow)


