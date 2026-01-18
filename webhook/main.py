from contextlib import asynccontextmanager

from colorstreak import Logger
from fastapi import FastAPI, Request

from .config import client_whatsapp
from .manager import webhook_manager


# ==========================================
# 🔄 LIFESPAN (Gestión de vida del servidor)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):

    Logger.info("🚀 Webhook System: ONLINE")
    
    yield
    
    Logger.info("🔌 Cerrando conexión con WhatsApp...")
    await client_whatsapp.close() 
    Logger.info("👋 Bye!")

# ==========================================
# 🚀 APP DEFINITION
# ==========================================
app = FastAPI(
    title="WhatsApp Webhook", 
    debug=True,
    lifespan=lifespan
)

@app.post("/evolution/webhook/{event_type}")
async def endpoint(event_type: str, request: Request):
    """
    Endpoint único de entrada.
    Filtra por URL antes de procesar el JSON (Fast Fail).
    """
    
    if not webhook_manager.knows_event(event_type):
        return {"status": "ignored"}

    Logger.info(f"✅ Procesando evento: {event_type}")
    payload = await request.json()
    
    await webhook_manager.dispatch(payload)
        
    return {"status": "ack"}
