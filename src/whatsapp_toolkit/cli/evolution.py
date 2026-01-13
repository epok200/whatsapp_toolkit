import typer

from whatsapp_toolkit.devtools import (
    init_evolution,
    stack_evolution,
)

from .utils import report_fatal_error, require_docker


# =========================
# Evolution CLI
# =========================
app = typer.Typer(
    add_completion=False,
    help="DevTools: stack local de Evolution API  en Docker Compose",
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
)



@app.command("init", help="Inicializa un stack local de Evolution API")
def init(
    path: str = ".",
    overwrite: bool = typer.Option(False, "--overwrite", help="Sobrescribir archivos existentes"),
    version: str = typer.Option("2.3.7", "--version", help="Versión de Evolution API en el docker-compose"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Modo silencioso, sin salida por consola"),
    api_key: str = typer.Option("YOUR_WHATSAPP_API_KEY", "--api-key", help="API Key para Evolution"),
    instance: str = typer.Option("main", "--instance", help="Instancia de Evolution"),
    webhook_url: str = typer.Option("http://host.docker.internal:8000/evolution/webhook", "--webhook-url", help="URL del webhook de Evolution"),
):
    init_evolution(
        path=path,
        overwrite=overwrite,
        version=version,
        verbose=not quiet,
        api_key=api_key,
        instance=instance,
        webhook_url=webhook_url,
    )


@app.command("up", help="Inicia el stack local de Evolution API")
def up(
    path: str = ".",
    background: bool = typer.Option(True,"--bg/--no-bg", help="Iniciar docker en segundo plano"),
    build: bool = typer.Option(False, "--build", help="Forzar reconstrucción de imágenes de docker"),
):
    require_docker()
    try:
        stack = stack_evolution(path=path)
        stack.up(
            background=background,
            build=build,
        )
    except RuntimeError as e:
        report_fatal_error(str(e))
    
    
@app.command("stop", help="Detiene el stack local de Evolution API")
def stop(
    path: str = ".",
):
    require_docker()
    try:
        stack = stack_evolution(path=path)
        stack.stop()
    except RuntimeError as e:
        report_fatal_error(str(e))


@app.command("down", help="Elimina el stack local de Evolution API")
def down(
    path: str =  ".",
    volumes: bool = typer.Option(False, "-v", "--volumes", help="Elimina volumenes"),
):
    require_docker()
    try:
        stack = stack_evolution(path=path)
        stack.down(volumes=volumes)
    except RuntimeError as e:
        report_fatal_error(str(e))
    
    
@app.command("logs", help="Muestra los logs del stack local de Evolution API |  nombre del servicio (evolution-api, evolution-postgres, evolution-redis)")
def logs(
    path: str = ".",
    services: str | None = typer.Option(None, "--services", help="Servicios (evolution-api | evolution-postgres | evolution-redis)"),
    follow: bool = typer.Option(True, "--follow/--no-follow", help="Seguir logs")
):
    require_docker()
    try:
        args: list[str] = []
        if not services:
            all_services = ["evolution-api", "evolution-postgres", "evolution-redis"]
            args.extend(all_services)
        else:
            args.append(services)

        stack = stack_evolution(path=path)
        stack.logs(services=args, follow=follow)
    except RuntimeError as e:
        report_fatal_error(str(e))
    
