import typer

from whatsapp_toolkit.devtools import (
    init_webhook,
    stack_webhook,
)

from .utils import report_fatal_error, require_docker


# =========================
# Webhook CLI
# =========================
app = typer.Typer(
    add_completion=False,
    help="DevTools: stack local de Webhook en Docker Compose",
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
)



@app.command("init", help="Inicializa un stack local de Webhook")
def init(
    path: str = ".",
    overwrite: bool = typer.Option(False, "--overwrite", help="Sobrescribir archivos existentes"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Modo silencioso, sin salida por consola"),
    python_version: str = typer.Option("3.13.11", "--python-version", help="Versión de Python para el Webhook"),
    api_key: str = typer.Option("YOUR_WHATSAPP_API_KEY", "--api-key", help="API Key para el Webhook"),
):
    init_webhook(
        path=path,
        overwrite=overwrite,
        verbose=not quiet,
        python_version=python_version,
        api_key=api_key,
    )

@app.command("up", help="Inicia el stack local de Webhook")
def up(
    path: str = ".",
    background: bool = typer.Option(True,"--bg/--no-bg", help="Iniciar docker en segundo plano"),
    build: bool = typer.Option(False, "--build", help="Forzar reconstrucción de imágenes de docker"),
):
    require_docker()
    try:
        stack = stack_webhook(path=path)
        stack.up(
            background=background,
            build=build,
        )
    except RuntimeError as e:
        report_fatal_error(str(e))

@app.command("stop", help="Detiene el stack local de Webhook")
def stop(
    path: str = ".",
):
    require_docker()
    try:
        stack = stack_webhook(path=path)
        stack.stop()
    except RuntimeError as e:
        report_fatal_error(str(e))

@app.command("down", help="Detiene y elimina el stack local de Webhook")
def down(
    path: str = ".",
    volumes: bool = typer.Option(False, "-v", "--volumes", help="Elimina volumenes"),
):
    require_docker()
    try:
        stack = stack_webhook(path=path)
        stack.down(volumes=volumes)
    except RuntimeError as e:
        report_fatal_error(str(e))


@app.command("logs", help="Muestra los logs del stack local de Webhook")
def logs(
    path: str = ".",
    follow: bool = typer.Option(True, "--follow/--no-follow", help="Seguir logs")
):
    require_docker()
    try:
        stack = stack_webhook(path=path)
        stack.logs(follow=follow)
    except RuntimeError as e:
        report_fatal_error(str(e))
    
