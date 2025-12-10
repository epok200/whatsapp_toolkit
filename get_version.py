# tools/get_version.py
import tomllib
from pathlib import Path




def get_version() -> str:
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    return data["project"]["version"]


if __name__ == "__main__":
    print(get_version())