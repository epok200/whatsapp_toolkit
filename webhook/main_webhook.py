import os
from colorstreak import Logger
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from .dispatcher import webhook_manager
from .schemas import MessageUpsert
from .services import download_media

load_dotenv()

app = FastAPI(title="WhatsApp Webhook", debug=True)



@webhook_manager.on("messages.upsert", model=MessageUpsert)
async def handle_messages(event: MessageUpsert):
    
    # Comentado para pruebas contigo mismo
    # if event.from_me:
    #     return

    if event.message_type == "audioMessage":
        Logger.info(f"🎙️ Procesando audio de {event.media_seconds} segundos...")
        
        # 1. Obtenemos la API Key real del evento
        real_apikey = event.apikey or os.getenv("WHATSAPP_API_KEY")

        # 2. Descargamos el media
        audio_bytes = await download_media(
            instance_id=event.instance_id or "main",
            
            # ✅ CORRECCIÓN FINAL:
            # Usamos event.raw (el objeto completo con 'key' y metadata)
            # en lugar de event.raw_message (que solo tenía el contenido).
            message_data=event.raw, 
            
            api_key=real_apikey
        )
        
        if audio_bytes:
            filename = f"audios/{event.wa_id}.ogg"
            os.makedirs("audios", exist_ok=True)
            with open(filename, "wb") as f:
                f.write(audio_bytes)
            
            Logger.info(f"✅ Audio guardado en: {filename}")

@app.post("/evolution/webhook/{event_type}")
async def endpoint(request: Request):
    payload = await request.json()
    #Logger.debug(f"📩 Webhook recibido: {payload}")
    await webhook_manager.dispatch(payload)
    return {"status": "ack"}