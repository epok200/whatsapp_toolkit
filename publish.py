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

REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = REPO_ROOT / "pyproject.toml"
DIST_DIR = REPO_ROOT / "dist"


def uv_sync():
    subprocess.run(["uv", "sync"], cwd=REPO_ROOT, check=True)


def get_version() -> str:
    uv_sync()
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return data["project"]["version"]


@app.command()
def publish(env_file: str = ".env.secret"):
    # Load token from repo root/.env.secret
    load_dotenv(REPO_ROOT / env_file)

    token = os.getenv("UV_PUBLISH_TOKEN", "").strip()
    if not token:
        raise typer.BadParameter("Missing UV_PUBLISH_TOKEN (check your .env.secret).")

    version = get_version()

    # Clean dist/
    shutil.rmtree(DIST_DIR, ignore_errors=True)

    # Build & publish (token via env, not CLI)
    env = os.environ.copy()
    env["UV_PUBLISH_TOKEN"] = token

    subprocess.run(["uv", "build"], cwd=REPO_ROOT, check=True, env=env)
    subprocess.run(["uv", "publish"], cwd=REPO_ROOT, check=True, env=env)

    log.info(
        f"✅ Published whatsapp-toolkit {version} to PyPI. link: https://pypi.org/project/whatsapp-toolkit/"
    )


if __name__ == "__main__":
    app()
