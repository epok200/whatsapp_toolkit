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
        File.from_path("main_webhook", "main.py", webhook_dir),
        File.from_path("config_webhook", "config.py", webhook_dir),
        File.from_path("services_webhook", "services.py", webhook_dir),
        File.from_path("handlers_webhook", "handlers.py", webhook_dir),
        File.from_path("manager_webhook", "manager.py", webhook_dir),
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
        files = self.spec.paths(self.paths)

        # Directorios base (source of truth)
        stack_dir = self.paths.stack_dir("webhook")
        webhook_dir = self.paths.root_dir("webhook")

        # paths (server)
        compose_path = files.get_path("compose")
        dockerfile_path = files.get_path("dockerfile")
        env_compose_path = files.get_path("env_compose")
        requirements_path = files.get_path("requirements")

        # paths (programming)
        env_webhook_path = files.get_path("env_webhook")
        main_webhook_path = files.get_path("main_webhook")
        config_webhook_path = files.get_path("config_webhook")
        services_webhook_path = files.get_path("services_webhook")
        handlers_webhook_path = files.get_path("handlers_webhook")
        manager_webhook_path = files.get_path("manager_webhook")

        port = str(self.port())

        # Relativos desde el contexto del stack (.wtk/webhook/) hacia /webhook del user
        webhook_dir_rel = str(self.paths.rel(webhook_dir, start=stack_dir) )       # Path("../../webhook")
        webhook_env_rel = str(self.paths.rel(env_webhook_path, start=stack_dir))   # Path("../../webhook/.env")

        # =========================
        # server files
        # =========================

        compose_file = temp._DOCKER_COMPOSE_WEBHOOK

        dockerfile_file = temp._DOCKERFILE_WEBHOOK

        # Este es el env que usa el runner con --env-file (control del stack)
        env_compose_file = (
            temp._DOTENV_COMPOSE_WEBHOOK
            .replace("{PORT}", port)
            .replace("{PYTHON_VERSION}", options.python_version)
            .replace("{WEBHOOK_DIR_REL}", webhook_dir_rel)
            .replace("{WEBHOOK_ENV_REL}", webhook_env_rel)
        )

        requirements_file = temp._REQUIREMENTS_WEBHOOK

        # =========================
        # programming files
        # =========================
        dotenv_webhook_file = temp._DOTENV_WEBHOOK.replace("{API_KEY}", options.api_key)
        main_webhook_py_file = temp._MAIN_WEBHOOK_PY
        config_webhook_file = temp._CONFIG_WEBHOOK_PY
        services_webhook_file = temp._SERVICES_WEBHOOK_PY
        handlers_webhook_file = temp._HANDLERS_WEBHOOK_PY
        manager_webhook_file = temp._MANAGER_WEBHOOK_PY

        files_and_paths_list = [
            # server files
            (compose_file, compose_path),
            (dockerfile_file, dockerfile_path),
            (env_compose_file, env_compose_path),
            (requirements_file, requirements_path),
            # programming files
            (dotenv_webhook_file, env_webhook_path),
            (main_webhook_py_file, main_webhook_path),
            (config_webhook_file, config_webhook_path),
            (services_webhook_file, services_webhook_path),
            (handlers_webhook_file, handlers_webhook_path),
            (manager_webhook_file, manager_webhook_path),
        ]

        for content, path in files_and_paths_list:
            self.writer.write(path, content, overwrite=options.overwrite)

        if options.verbose:
            log.info(f"[whatsapp-toolkit] ✅ Stack '{self.spec.name}' listo en: {stack_dir}")
            for _, p in files_and_paths_list:
                log.library(f"  - {p.name}")



# =========================
# Funciones de conveniencia para Webhook
# =========================
def init_webhook(path: str = ".", overwrite: bool = False, verbose: bool = True, python_version: str = "3.13.11", api_key: str = "YOUR_WHATSAPP_API_KEY") -> None:
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