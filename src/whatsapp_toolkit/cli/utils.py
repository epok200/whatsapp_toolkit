import typer
from whatsapp_toolkit.devtools import ensure_docker_daemon


def report_fatal_error(message: str, code: int = 1):
    """Muestra un mensaje de error y termina la ejecución."""
    typer.secho(message, fg=typer.colors.RED, err=True)
    raise typer.Exit(code=code)


def require_docker() -> None:
    """Valida Docker antes de ejecutar comandos que dependen de Compose."""
    try:
        ensure_docker_daemon()
    except RuntimeError as e:
        report_fatal_error(str(e))