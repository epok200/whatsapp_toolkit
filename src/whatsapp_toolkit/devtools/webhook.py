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
from .templates import webhook_templates  as temp


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
def _webhook_required_paths(paths: PathConfig) -> Files:
    stack_dir = paths.stack_dir("webhook")  # ./project/.wtk/webhook/
    webhook_dir = paths.root_dir("webhook") # ./project/webhook/

    list_file: list[File] = [
        # Server files
        File.from_path("compose", "docker-compose.yml", stack_dir),
        File.from_path("dockerfile", "Dockerfile", stack_dir),
        File.from_path("env_compose", ".env", stack_dir),
        File.from_path("requirements", "requirements.txt", stack_dir),
        # Programming files
        File.from_path("env_webhook", ".env", webhook_dir),
        File.from_path("main_webhook", "main_webhook.py", webhook_dir),
    ]
    return Files.from_list(list_file)





WEBHOOK = BaseStackSpec(
    name="webhook",
    command_name="webhook",
    default_port=8000,
    services=("whatsapp-webhook",),
    route_postfix="/doc",
    paths=_webhook_required_paths,
)



# =========================
# Webhook StackInitializer
# =========================

class WebhookStackInitializer(BaseStackInitializer):
    def __init__(self, spec: BaseStackSpec, paths: PathConfig, writer: TemplateWriter | None = None):
        super().__init__(spec, paths, writer)
    
    
    def init(self, options: WebhookInitOptions) -> None:
        paths = self.spec.paths(self.paths)
        stack_dir = self.paths.stack_dir("webhook")
        webhook_dir = self.paths.root_dir("webhook")

        # paths (server)
        compose_path = paths.get_path("compose")
        dockerfile_path = paths.get_path("dockerfile")
        env_compose_path = paths.get_path("env_compose")
        requirements_path = paths.get_path("requirements")
        
        # paths (programming)
        env_webhook_path = paths.get_path("env_webhook")
        main_webhook_path = paths.get_path("main_webhook")
        
        
        # webhook files (server)
        port = self.port()
        compose_file = (
            temp._DOCKER_COMPOSE_WEBHOOK
            .replace("{PORT}", str(port))
            .replace("{ENV_DIR}", str(env_compose_path.parent) )
        )
        dockerfile_file = (
            temp._DOCKERFILE_WEBHOOK
            .replace("{PYTHON_VERSION}", options.python_version)
            .replace("{REQUIREMENTS_DIR}", str(requirements_path))
            .replace("{WEBHOOK_DIR}", str(webhook_dir))
            .replace("{PORT}", str(port))
        )
        env_compose_file = (
            temp._DOTENV_COMPOSE_WEBHOOK
            .replace("{PORT}", str(port))
        )
        requirements_file = temp._REQUIREMENTS_WEBHOOK
        
        # webhook files (programming)
        dotenv_webhook_file = (
            temp._DOTENV_WEBHOOK
            .replace("{API_KEY}", options.api_key )
        )
        main_webhook_py_file = temp._MAIN_WEBHOOK_PY
    
        file_and_paths_list = [
            # server files
            (compose_file, compose_path),
            (dockerfile_file, dockerfile_path),
            (env_compose_file, env_compose_path),
            (requirements_file, requirements_path),
            # programming files
            (dotenv_webhook_file, env_webhook_path),
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