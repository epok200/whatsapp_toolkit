from typing import Any

def pluck(source: dict, path: str, default: Any = None) -> Any:
    """
    Navega en un diccionario usando "dot.notation".add()
    Ej: plick(data, "data.key.remoteJid") -> "12345..."
    """
    try:
        keys = path.split(".")
        value = source
        for key in keys:
            if isinstance(value,dict):
                value = value.get(key)
            else:
                return default
        return value if value is not None else default
    except Exception:
        return default
    