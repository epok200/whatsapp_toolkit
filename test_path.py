# pip/uv: uv add platformdirs
from platformdirs import user_cache_dir
from pathlib import Path

app_name = "whatsapp_toolkit"  # cámbialo si quieres
cache_dir = Path(user_cache_dir(app_name))
models_dir = cache_dir / "tts_models"

print("User cache dir:", cache_dir)
print("Models cache dir:", models_dir)
