from dataclasses import dataclass

from colorstreak import Logger as log

from .main import (
    BaseInitOptions,
    BaseStackInitializer,
    BaseStackSpec,
    PathConfig,
    Stack,
    TemplateWriter,
)
from .templates import templates


# =========================
# StackSpec + Initializer para Evolution
# =========================
@dataclass(frozen=True)
class EvolutionInitOptions(BaseInitOptions):
    version: str = "2.3.7"  # Versión de Evolution a usar

# =========================
# Evolution StackSpec
# =========================
EVOLUTION = BaseStackSpec(
    name="evolution",
    compose_filename="docker-compose.yml",
    env_filename=".env",
    wakeup_filename="wakeup_evolution.sh",
    required_files=("docker-compose.yml", ".env","wakeup_evolution.sh"),
    services=("evolution-api", "evolution-postgres", "evolution-redis"),
)



# =========================
# Evolution StackInitializer
# =========================
class EvolutionStackInitializer(BaseStackInitializer):
    def __init__(self, paths: PathConfig, writer: TemplateWriter | None = None):
        super().__init__(paths, writer)
    
    
    def init(self, options: EvolutionInitOptions) -> None:
        stack_dir = EVOLUTION.dir(self.paths)
        stack_dir.mkdir(parents=True, exist_ok=True)

        # Archivos de evolution
        compose_path = EVOLUTION.compose_path(self.paths)
        env_path = EVOLUTION.env_path(self.paths)
        wakeup_path = EVOLUTION.wakeup_path(self.paths)
        req_path = stack_dir / "requirements.txt"
        dockerfile_path = stack_dir / "Dockerfile"

        # Importante: aquí todavía usamos .replace, luego lo migras a Jinja.
        compose = templates._DOCKER_COMPOSE.replace("{VERSION}", options.version)
        wakeup = templates._WAKEUP_SH.replace("${UP_ARGS}", "")

        self.writer.write(compose_path, compose, overwrite=options.overwrite)
        self.writer.write(env_path, templates._DOTENV_EXAMPLE, overwrite=options.overwrite)

        if wakeup_path:
            self.writer.write(wakeup_path, wakeup, overwrite=options.overwrite)
            try:
                wakeup_path.chmod(wakeup_path.stat().st_mode | 0o111)
            except Exception:
                pass

        # Si por ahora ya NO quieres webhook, no lo escribas. Punto.
        # self.writer.write(dockerfile_path, templates._DOCKERFILE, overwrite=opts.overwrite)
        # self.writer.write(req_path, templates._REQUIREMENTS_TXT, overwrite=opts.overwrite)

        if options.verbose:
            log.info(f"[whatsapp-toolkit] ✅ Stack '{EVOLUTION.name}' listo en: {stack_dir}")
            log.library(f"  - {compose_path.name}")
            log.library(f"  - {env_path.name}")
            if wakeup_path:
                log.library(f"  - {wakeup_path.name}")



# =========================
# Funciones de conveniencia para Evolution
# =========================

def init_evolution(path: str = ".", overwrite: bool = False, version: str = "2.3.7", verbose: bool = True) -> None:
    cfg = PathConfig.from_path(path)
    EvolutionStackInitializer(cfg).init(EvolutionInitOptions(overwrite=overwrite, version=version, verbose=verbose))
    
def stack_evolution(path: str = ".") -> Stack:
    cfg = PathConfig.from_path(path)
    return Stack(EVOLUTION, cfg)