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
# StackSpec + Initializer para Webhook
# =========================

@dataclass(frozen=True)
class WebhookInitOptions(BaseInitOptions):
    python_version: str = "3.13.11"  # Versión de Python a usar
    api_key: str  = " YOUR_WEBHOOK_API_KEY"  # API Key para el Webhook



# =========================
# Webhook StackSpec
# =========================

WEBHOOK = BaseStackSpec(
    name="webhook",
    command_name="webhook",
    default_port=8000,
    compose_filename="docker-compose.yml",
    env_filename=".env",
    required_files=("docker-compose.yml", ".env", "Dockerfile", "requirements.txt","main_webhook.py"),
    services=("whatsapp-webhook",),
    route_postfix="/doc"
)



# =========================
# Webhook StackInitializer
# =========================

class WebhookStackInitializer(BaseStackInitializer):
    def __init__(self, spec: BaseStackSpec, paths: PathConfig, writer: TemplateWriter | None = None):
        super().__init__(spec, paths, writer)
    
    
    def init(self, options: WebhookInitOptions) -> None:
        stack_dir = self.stack_dir()
        stack_dir.mkdir(parents=True, exist_ok=True)
        # Client webhook dir (for coding and testing)
        project_dir = self.paths.project_root
        webhook_dir = project_dir / "webhook"

        # paths (server)
        compose_path = stack_dir / WEBHOOK.compose_filename
        dockerfile_path = stack_dir / "Dockerfile"
        requirements_path = stack_dir / "requirements.txt"
        
        # paths (programming)
        env_path = webhook_dir / WEBHOOK.env_filename
        main_webhook_path = webhook_dir / "main_webhook.py"
        
        
        # webhook files (server)
        port = self.port()
        compose_file = (
            templates._DOCKER_COMPOSE_WEBHOOK
            .replace("{PORT}", str(port))
            .replace("{ENV_DIR}", str(env_path))
        )
        dockerfile_file = (
            templates._DOCKERFILE_WEBHOOK
            .replace("{PYTHON_VERSION}", options.python_version)
            .replace("{REQUIREMENTS_DIR}", str(requirements_path))
            .replace("{WEBHOOK_DIR}", str(webhook_dir))
            .replace("{PORT}", str(port))
        )
        requirements_file = templates._REQUIREMENTS_WEBHOOK
        
        # webhook files (programming)
        dotenv_file = (
            templates._DOTENV_WEBHOOK
            .replace("{API_KEY}", options.api_key )
        )
        main_webhook_py_file = templates._MAIN_WEBHOOK_PY
    
        file_and_paths_list = [
            # server files
            (compose_file, compose_path),
            (dotenv_file, env_path),
            (dockerfile_file, dockerfile_path),
            # programming files
            (requirements_file, requirements_path),
            (main_webhook_py_file, main_webhook_path),
        ]

        for file_content, file_path in file_and_paths_list:
            self.writer.write(file_path, file_content, overwrite=options.overwrite)
            
        if options.verbose:
            log.info(f"[whatsapp-toolkit] ✅ Stack '{WEBHOOK.name}' listo en: {stack_dir}")
            for _, paths in file_and_paths_list:            
                log.library(f"  - {paths.name}")



# =========================
# Funciones de conveniencia para Webhook
# =========================
def init_webhook(path: str = ".", overwrite: bool = False, verbose: bool = True, python_version: str = "3.13.11", api_key: str = "YOUR_WEBHOOK_API_KEY") -> None:
    path_conf = PathConfig.from_path(path)
    (WebhookStackInitializer(WEBHOOK, path_conf)
     .init(WebhookInitOptions(
         overwrite=overwrite, 
         verbose=verbose, 
         python_version=python_version,
         api_key=api_key,
    )))

def stack_webhook(path: str = ".") -> Stack:
    path_conf = PathConfig.from_path(path)
    return Stack(WEBHOOK, path_conf)