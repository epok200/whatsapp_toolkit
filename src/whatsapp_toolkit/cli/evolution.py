import typer
from whatsapp_toolkit import devtools


app = typer.Typer(
    add_completion=False,
    help="DevTools: stack local de Evolution API (Docker Compose)",
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
)


def _report_fatal_error(message: str, code: int = 1):
    """Muestra un mensaje de error y termina la ejecución."""
    typer.secho(message, fg=typer.colors.RED, err=True)
    raise typer.Exit(code=code)


def _require_docker() -> None:
    """Valida Docker antes de ejecutar comandos que dependen de Compose."""
    try:
        devtools.ensure_docker_daemon()
    except RuntimeError as e:
        _report_fatal_error(str(e))


@app.command("init", help="Inicializa un stack local de Evolution API")
def init(
    path: str = ".",
    overwrite: bool = typer.Option(False, "--overwrite", help="Sobrescribir archivos existentes"),
    version: str = typer.Option("2.3.7", "--version", help="Versión de Evolution API en el docker-compose"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Modo silencioso, sin salida por consola")
):
    devtools.init_local_evolution(
        path=path,
        overwrite=overwrite,
        version=version,
        verbose=not quiet
    )


@app.command("up", help="Inicia el stack local de Evolution API")
def up(
    path: str = ".",
    background: bool = typer.Option(True,"--bg/--no-bg", help="Iniciar docker en segundo plano"),
    build: bool = typer.Option(False, "--build", help="Forzar reconstrucción de imágenes de docker"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Menos salidas de la librería")
):
    _require_docker()
    try:
        stack = devtools.local_evolution(path=path)
        stack.start(
            detached=background,
            build=build,
            verbose=not quiet
        )
    except RuntimeError as e:
        _report_fatal_error(str(e))
    
    
@app.command("stop", help="Detiene el stack local de Evolution API")
def stop(
    path: str = ".",
    quiet: bool = typer.Option(False, "--quiet", help="Menos salidas de la librería")
):
    _require_docker()
    try:
        stack = devtools.local_evolution(path=path)
        stack.stop(verbose=not quiet)
    except RuntimeError as e:
        _report_fatal_error(str(e))


@app.command("down", help="Elimina el stack local de Evolution API")
def down(
    path: str =  ".",
    volumes: bool = typer.Option(False, "-v", "--volumes", help="Elimina volumenes"),
    quiet: bool = typer.Option(False, "--quiet", help="Menos salidas de la librería")
):
    _require_docker()
    try:
        stack = devtools.local_evolution(path=path)
        stack.down(volumes=volumes, verbose= not quiet)
    except RuntimeError as e:
        _report_fatal_error(str(e))
    
    
@app.command("logs", help="Muestra los logs del stack local de Evolution API |  nombre del servicio (evolution-api, evolution-postgres, evolution-redis)")
def logs(
    path: str = ".",
    services: str | None = typer.Option(None, "--services", help="Servicios (evolution-api | evolution-postgres | evolution-redis)"),
    follow: bool = typer.Option(True, "--follow/--no-follow", help="Seguir logs")
):
    _require_docker()
    try:
        args: list[str] = []
        if not services:
            all_services = ["evolution-api", "evolution-postgres", "evolution-redis"]
            args.extend(all_services)
        else:
            args.append(services)

        stack = devtools.local_evolution(path=path)
        stack.logs(service=args, follow=follow)
    except RuntimeError as e:
        _report_fatal_error(str(e))
    
