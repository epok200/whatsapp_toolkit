import shutil
import subprocess
import sys



def _platform() -> str:
    """Devuelve el nombre del sistema operativo actual."""
    p = sys.platform.lower()
    if p.startswith("win"):
        return "windows"
    if p.startswith("linux"):
        return "linux"
    if p.startswith("darwin"):
        return "mac"
    return "unknown"





def ensure_docker_daemon() -> None:
    """Falla temprano si Docker está instalado pero el daemon no responde.

    No todos los setups tienen el binario `docker` disponible (p.ej. algunos `docker-compose` antiguos),
    así que este check es best-effort.
    """
    
    docker = shutil.which("docker")
    if not docker:
        return

    try:
        subprocess.run(
            [docker, "info"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        subprocess_docker_error = (e.stderr or "").strip()
        
        hint = (
            "Docker está instalado pero no parece estar corriendo (daemon inaccesible).\n"
            "- macOS: abre Docker Desktop y espera a que diga 'Running'.\n" if _platform() == "mac" else ""
            "- Linux: intenta 'sudo systemctl start docker' y 'sudo systemctl status docker'.\n" if _platform() == "linux" else ""
            "- Windows: abre Docker Desktop y espera a que diga 'Running'.\n" if _platform() == "windows" else ""
            "Luego vuelve a intentar el comando."
        )
        if subprocess_docker_error:
            hint += f"\nDetalle: {subprocess_docker_error}"
        raise RuntimeError(hint) from e