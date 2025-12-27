import typer
from whatsapp_toolkit import devtools


app = typer.Typer(
    add_completion=False,
    help="DevTools: stack local de Evolution API (Docker Compose)"
)

@app.command("init")
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


@app.command("up")
def up(
    path: str = ".",
    detached: bool = typer.Option(False, "-d", "--detached", help="Ejecutar en segundo plano"),
    build: bool = typer.Option(False, "--build", help="Forzar reconstrucción de imágenes"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Menos saldas"   )
):
    stack = devtools.local_evolution(path=path)
    stack.start(
        detached=detached,
        build=build,
        verbose=not quiet
    )
    
@app.command("stop")
def stop(
    path: str = ".",
    quiet: bool = typer.Option(False, "--quiet", help="Menos salidas")
):
    stack = devtools.local_evolution(path=path)
    stack.stop(verbose=not quiet)


@app.command("down")
def down(
    path: str =  ".",
    volumes: bool = typer.Option(False, "-v", "--volumes", help="Elimina volumenes"),
    quiet: bool = typer.Option(False, "--quiet", "Menos salidas")
):
    stack = devtools.local_evolution(path=path)
    stack.down(volumes=volumes, verbose= not quiet)
    
@app.command("logs")
def logs(
    path: str = ".",
    services: str | None = typer.Option(None, "--services", help="Servicios (evolution-api | evolution-postgres | evolution-redis)"),
    follow: bool = typer.Option(False, "--follow/--no-follow", "Seguir logs")
):
    stack = devtools.local_evolution(path=path)
    stack.logs(service=services, follow=follow)
    
