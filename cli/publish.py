# tools/publish.py
import os
import shutil
import subprocess
import tomllib
from pathlib import Path

import typer
from dotenv import load_dotenv
from colorstreak import Logger as log

app = typer.Typer(add_completion=False)


def repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in (p.parent, *p.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise typer.BadParameter(
        "No encuentro pyproject.toml hacia arriba; corre este comando dentro del repo."
    )


def uv_sync(root: Path) -> None:
    subprocess.run(["uv", "sync"], cwd=root, check=True)


def get_version(root: Path) -> str:
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return data["project"]["version"]


@app.command()
def publish(env_file: str = ".env.secret"):
    root = repo_root()
    # Load token from repo root/.env.secret
    load_dotenv(root / env_file)
    
    token = os.getenv("UV_PUBLISH_TOKEN", "").strip()
    if not token:
        raise typer.BadParameter("Missing UV_PUBLISH_TOKEN (check your .env.secret).")

    uv_sync(root)

    version = get_version(root)

    # Clean dist/
    shutil.rmtree(root / "dist", ignore_errors=True)

    # Build & publish (token via env, not CLI)
    env = os.environ.copy()
    env["UV_PUBLISH_TOKEN"] = token

    subprocess.run(["uv", "build"], cwd=root, check=True, env=env)
    subprocess.run(["uv", "publish"], cwd=root, check=True, env=env)

    log.info(
        f"✅ Published whatsapp-toolkit {version} to PyPI. link: https://pypi.org/project/whatsapp-toolkit/"
    )


if __name__ == "__main__":
    app()
