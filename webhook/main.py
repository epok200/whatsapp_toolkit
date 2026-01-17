from colorstreak import Logger
from fastapi import FastAPI, Request

from . import config  # noqa: F401
from . import handlers  # noqa: F401
from .dispatcher import webhook_manager

app = FastAPI(title="WhatsApp Webhook", debug=True)


WHITE_LIST = {
    "messages": {"upsert"},
}

def is_event_allowed(event_type: str) -> bool:
    """Valida solo con el string de la URL. Rápido y barato."""
    category,subcategory = event_type.split("-",1)
    
    if category in WHITE_LIST:
        allowed_category = WHITE_LIST[category]
        if subcategory in allowed_category or "*" in allowed_category:
            Logger.info(f"✅ Permitido -> {category}/{subcategory}")
            return True
    
    #Logger.warning(f"🚫 Ignorando -> {category}/{subcategory}") 
    return False



@app.post("/evolution/webhook/{event_type}")
async def endpoint(event_type: str, request: Request):
    
    if not is_event_allowed(event_type):
        return {"status": "ignored"}

    payload = await request.json()
    
    await webhook_manager.dispatch(payload)
        
    return {"status": "ack"}