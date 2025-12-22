import json
from pathlib import Path
from whatsapp_toolkit.types import Groups
from colorstreak import Logger as log


BASE_DIR = Path(__file__).resolve().parent.parent
grupo_json = BASE_DIR / "grupos_obtenidos.json"


with open(grupo_json, "r", encoding="utf-8") as f:
    grupos_raw: list[dict] = json.load(f)
    
    
    
grupos = Groups()
grupos.upload_groups(grupos_raw)
print(f"Se cargaron {len(grupos.groups)} grupos.")
print(f"Fallos: {len(grupos.fails)}")

grupos_encontrados = grupos.search_group("club")
log.info("Grupos encontrados con 'bot':")
for grupo in grupos_encontrados:
    log.debug(grupo)
    
id = "120363405715130432@g.us"
grupo = grupos.get_group_by_id(id)
log.info(f"Buscando grupo por ID: {id}")
if grupo:
    log.info(grupo)