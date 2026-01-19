import asyncio
from contextlib import asynccontextmanager

import qrcode
from colorstreak import Logger
from fastapi import FastAPI, Request

from .config import client_whatsapp
from .manager import webhook_manager


# ==========================================
# 🔄 TAREA DE ARRANQUE (Background)
# ==========================================
async def startup_task():
    await asyncio.sleep(3)
    Logger.info("🔄 [Background] Verificando conexión...")
    
    try:
        status = await client_whatsapp.initialize()
        
        if status in ["created", "close"]:
            Logger.info("✨ Solicitando QR...")
            
            qr_string = await client_whatsapp.get_qr()
            
            if qr_string:
                Logger.success("📸 ESCANEA ESTE CÓDIGO:")
                
                qr = qrcode.QRCode()
                qr.add_data(qr_string)
                
                print("\n\n") 
                qr.print_ascii(invert=True) 
                print("\n\n")
                # ------------------------------------------
            else:
                Logger.error("❌ No se pudo obtener el código.")
                
        elif status == "open":
            Logger.success("🚀 Sistema ONLINE.")
            
    except Exception as e:
        Logger.error(f"❌ Error en arranque: {e}")
        
# ==========================================
# 🔄 LIFESPAN (Gestión de vida del servidor)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):

    Logger.info("🚀 Webhook System: ONLINE")
    
    asyncio.create_task(startup_task())
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
