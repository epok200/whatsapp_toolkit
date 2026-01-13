from dataclasses import dataclass

from colorstreak import Logger as log

from .main import (
    BaseInitOptions,
    BaseStackInitializer,
    BaseStackSpec,
    PathConfig,
    File,
    Files,
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
    webhook_url: str = "http://host.docker.internal:8000/evolution/webhook"

def _evolution_required_paths(paths: PathConfig) -> "Files":
    stack_dir = paths.stack_dir("evolution")  # ./project/.wtk/evolution/
    
    list_file: list[File] = [
        # Server files
        File.from_path("compose", "docker-compose.yml", stack_dir),
        File.from_path("env_compose", ".env", stack_dir),
    ]
    return Files.from_list(list_file)


# =========================
# Evolution StackSpec
# =========================

EVOLUTION = BaseStackSpec(
    name="evolution",
    command_name="evo",
    default_port=8080,
    services=("evolution-api", "evolution-postgres", "evolution-redis"),
    paths=_evolution_required_paths,
    route_postfix="/manager"
)



# =========================
# Evolution StackInitializer
# =========================

class EvolutionStackInitializer(BaseStackInitializer):
    def __init__(self, spec: BaseStackSpec, paths: PathConfig, writer: TemplateWriter | None = None):
        super().__init__(spec, paths, writer)
    
    
    def init(self, options: EvolutionInitOptions) -> None:
        files = self.spec.paths(self.paths)
        
        # Directorio base
        stack_dir = self.stack_dir()

        # Archivos de evolution
        compose_path = files.get_path("compose")
        env_path = files.get_path("env_compose")
        
        port = self.port()

        compose_file = (
            evo_templates._DOCKER_COMPOSE_EVOLUTION
            .replace("{VERSION}", options.version)
            .replace("{PORT}", str(port))
            .replace("{WEBHOOK_URL}", options.webhook_url)
        )
        
        dotenv_file = (
            evo_templates._DOTENV_EVOLUTION
            .replace("{API_KEY}", options.api_key)
            .replace("{INSTANCE}", options.instance)
            .replace("{SERVER_URL}", f"http://localhost:{port}/")
        )
        
        
        files_and_paths_list =[
            (compose_file, compose_path),
            (dotenv_file, env_path),
        ]
        

        for content, path in files_and_paths_list:
            self.writer.write(path, content, overwrite=options.overwrite)
        
        if options.verbose:
            log.info(f"[whatsapp-toolkit] ✅ Stack '{self.spec.name}' listo en: {stack_dir}")
            for _, p in files_and_paths_list:
                log.library(f"  - {p.name}")



# =========================
# Funciones de conveniencia para Evolution
# =========================

def init_evolution(
        path: str = ".", 
        overwrite: bool = False, 
        version: str = "2.3.7", 
        verbose: bool = True, 
        api_key: str = "YOUR_EVOLUTION_API_KEY", 
        instance: str = "main",
        webhook_url: str = "http://host.docker.internal:8000/evolution/webhook",
    ) -> None:
    path_conf = PathConfig.from_path(path)
    (EvolutionStackInitializer(EVOLUTION, path_conf).init(EvolutionInitOptions(
        overwrite=overwrite, 
        verbose=verbose, 
        version=version,
        api_key=api_key,
        instance=instance,
        webhook_url=webhook_url
    )))
    
def stack_evolution(path: str = ".") -> Stack:
    path_conf = PathConfig.from_path(path)
    return Stack(EVOLUTION, path_conf)