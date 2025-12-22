import json
from pathlib import Path
from whatsapp_toolkit.types import GroupBase, Groups, Participant
from colorstreak import Logger as log


BASE_DIR = Path(__file__).resolve().parent.parent
grupo_json = BASE_DIR / "grupos_obtenidos.json"


with open(grupo_json, "r", encoding="utf-8") as f:
    grupos_raw: list[dict] = json.load(f)
    
    
    
grupos = Groups()
grupos.upload_groups(grupos_raw)
print(f"Se cargaron {len(grupos.groups)} grupos.")
print(f"Fallos: {len(grupos.fails)}")

# grupos_encontrados = grupos.search_group("bot")
# for grupo in grupos_encontrados:
#     print(f"[ENCONTRADO] ID: {grupo.id} | Asunto: {grupo.subject} | Tipo: {grupo.kind} | ")
    
id = "120363405715130432@g.us"
grupo = grupos.get_group_by_id(id)
if grupo:
    log.debug(grupo)