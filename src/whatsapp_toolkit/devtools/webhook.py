from dataclasses import dataclass
from colorstreak import Logger as log

from whatsapp_toolkit import __version__
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
from .templates import render_template


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

        # Docs
        File.from_path("readme_webhook", "README.md", webhook_dir),
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

        # Relativos desde el contexto del stack (.wtk/webhook/) hacia /webhook del user
        webhook_dir_rel = str(self.paths.rel(webhook_dir, start=stack_dir))
        webhook_env_rel = str(self.paths.rel(files.get_path("env_webhook"), start=stack_dir))

        port = str(self.port())

        # Contexto compartido para templates con variables
        ctx = dict(
            port=port,
            python_version=options.python_version,
            webhook_dir_rel=webhook_dir_rel,
            webhook_env_rel=webhook_env_rel,
            api_key=options.api_key,
            version=__version__,
        )

        # Mapeo: (key en Files) -> (template .j2, variables necesarias)
        template_map = [
            # Server files
            ("compose",          "docker-compose.yml.j2", {}),
            ("dockerfile",       "Dockerfile.j2",         {}),
            ("env_compose",      "dotenv-compose.j2",     ctx),
            ("requirements",     "requirements.txt.j2",   ctx),
            # Programming files
            ("env_webhook",      "dotenv-webhook.j2",     ctx),
            ("main_webhook",     "main.py.j2",            {}),
            ("config_webhook",   "config.py.j2",          {}),
            ("services_webhook", "services.py.j2",        {}),
            ("handlers_webhook", "handlers.py.j2",        {}),
            ("manager_webhook",  "manager.py.j2",         {}),
            # Docs
            ("readme_webhook",   "README.md.j2",          ctx),
        ]

        for file_key, template_name, template_ctx in template_map:
            content = render_template("webhook", template_name, **template_ctx)
            path = files.get_path(file_key)
            self.writer.write(path, content, overwrite=options.overwrite)

        if options.verbose:
            log.info(f"[whatsapp-toolkit] ✅ Stack '{self.spec.name}' listo en: {stack_dir}")
            for file_key, _, _ in template_map:
                log.library(f"  - {files.get_path(file_key).name}")



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
