from contextlib import asynccontextmanager
from colorstreak import Logger
from fastapi import FastAPI, Request

# Imports de efectos secundarios (registran handlers y config)
from . import config  # noqa: F401
from . import handlers  # noqa: F401

# Importamos el manager y el cliente para cerrarlo
from .dispatcher import webhook_manager
from .config import client_whatsapp 

# ==========================================
# 🔄 LIFESPAN (Gestión de vida del servidor)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🟢 AL INICIAR:
    Logger.info("🚀 Webhook System: ONLINE")
    
    yield # Aquí es donde el servidor corre y recibe peticiones
    
    # 🔴 AL APAGAR:
    Logger.info("🔌 Cerrando conexión con WhatsApp...")
    await client_whatsapp.close() # <--- ¡ESTO ES LO IMPORTANTE!
    Logger.info("👋 Bye!")

# ==========================================
# 🚀 APP DEFINITION
# ==========================================
app = FastAPI(
    title="WhatsApp Webhook", 
    debug=True,
    lifespan=lifespan # Conectamos el lifespan aquí
)

@app.post("/evolution/webhook/{event_type}")
async def endpoint(event_type: str, request: Request):
    """
    Endpoint único de entrada.
    Filtra por URL antes de procesar el JSON (Fast Fail).
    """
    
    # 1. Filtro Rápido (URL)
    # webhook_manager.knows_event convierte "messages-upsert" -> "messages.upsert"
    if not webhook_manager.knows_event(event_type):
        return {"status": "ignored"}

    # 2. Procesamiento (Solo si pasó el filtro)
    Logger.info(f"✅ Procesando evento: {event_type}")
    payload = await request.json()
    
    # 3. Dispatch (Fuego y olvido - Fire and Forget)
    await webhook_manager.dispatch(payload)
        
    return {"status": "ack"}