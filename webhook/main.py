from colorstreak import Logger
from fastapi import FastAPI, Request

from . import config  # noqa: F401
from . import handlers  # noqa: F401
from .dispatcher import webhook_manager

# Instala haciendo: 
# pip install fastapi uvicorn python-dotenv whatsapp-toolkit
# O usa (SUGERIDO): 
# uv add  fastapi uvicorn python-dotenv whatsapp-toolkit

app = FastAPI(title="WhatsApp Webhook", debug=True)





@app.post("/evolution/webhook/{event_type}")
async def endpoint(event_type: str, request: Request):
    
    if not webhook_manager.knows_event(event_type):
        # Logger.debug(f"🚫 Ignorando evento sin handler: {event_type}")
        return {"status": "ignored"}

    Logger.info(f"✅ Procesando: {event_type}")
    payload = await request.json()
    await webhook_manager.dispatch(payload)
        
    return {"status": "ack"}

