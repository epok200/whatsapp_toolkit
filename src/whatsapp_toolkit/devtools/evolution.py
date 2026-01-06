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
from .templates import evo_templates


# =========================
# StackSpec + Initializer para Evolution
# =========================

@dataclass(frozen=True)
class EvolutionInitOptions(BaseInitOptions):
    version: str = "2.3.7"  # Versión de Evolution a usar
    api_key: str = "YOUR_EVOLUTION_API_KEY"  # API Key para Evolution
    instance: str = "main"  # Instancia de Evolution



# =========================
# Evolution StackSpec
# =========================

EVOLUTION = BaseStackSpec(
    name="evolution",
    command_name="evo",
    default_port=8080,
    compose_filename="docker-compose.yml",
    env_filename=".env",
    required_files=("docker-compose.yml", ".env"),
    services=("evolution-api", "evolution-postgres", "evolution-redis"),
    route_postfix="/manager"
)



# =========================
# Evolution StackInitializer
# =========================

class EvolutionStackInitializer(BaseStackInitializer):
    def __init__(self, spec: BaseStackSpec, paths: PathConfig, writer: TemplateWriter | None = None):
        super().__init__(spec, paths, writer)
    
    
    def init(self, options: EvolutionInitOptions) -> None:
        stack_dir = self.stack_dir()
        stack_dir.mkdir(parents=True, exist_ok=True)

        # Archivos de evolution
        compose_path = stack_dir / EVOLUTION.compose_filename
        env_path = stack_dir / EVOLUTION.env_filename
        
        port = self.port()

        compose = (
            evo_templates._DOCKER_COMPOSE_EVOLUTION
            .replace("{VERSION}", options.version)
            .replace("{PORT}", str(port))
        )
        
        dotenv = (
            evo_templates._DOTENV_EVOLUTION
            .replace("{API_KEY}", options.api_key)
            .replace("{INSTANCE}", options.instance)
            .replace("{SERVER_URL}", f"http://localhost:{port}/")
        )

        self.writer.write(compose_path, compose, overwrite=options.overwrite)
        self.writer.write(env_path, dotenv, overwrite=options.overwrite)
        
        if options.verbose:
            log.info(f"[whatsapp-toolkit] ✅ Stack '{EVOLUTION.name}' listo en: {stack_dir}")
            log.library(f"  - {compose_path.name}")
            log.library(f"  - {env_path.name}")



# =========================
# Funciones de conveniencia para Evolution
# =========================

def init_evolution(path: str = ".", overwrite: bool = False, version: str = "2.3.7", verbose: bool = True, api_key: str = "YOUR_EVOLUTION_API_KEY", instance: str = "main") -> None:
    path_conf = PathConfig.from_path(path)
    (EvolutionStackInitializer(EVOLUTION, path_conf)
     .init(EvolutionInitOptions(
         overwrite=overwrite, 
         verbose=verbose, 
         version=version,
         api_key=api_key,
         instance=instance,
    )))
    
def stack_evolution(path: str = ".") -> Stack:
    path_conf = PathConfig.from_path(path)
    return Stack(EVOLUTION, path_conf)