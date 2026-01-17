# handlers.py
import os
from colorstreak import Logger
from .dispatcher import webhook_manager
from .schemas import MessageUpsert
from .services import download_media
from .config import client_whatsapp, WHATSAPP_API_KEY



def speach_to_text(audio_bytes: bytes) -> str:
    """
    Función ficticia para convertir audio a texto.
    En un caso real, aquí se integraría con un servicio de STT.
    """
    # Simulación de conversión
    return "Transcripción simulada del audio."




@webhook_manager.on("messages.upsert", model=MessageUpsert)
async def handle_messages(event: MessageUpsert):
    
    if event.message_type == "audioMessage":
        Logger.info(f"🎙️ Procesando audio de {event.media_seconds} segundos...")
        
        real_apikey = event.apikey or WHATSAPP_API_KEY

        audio_bytes = await download_media(
            instance_id=event.instance_id or "main",
            message_data=event.raw, 
            api_key=real_apikey
        )
        
        if audio_bytes:
            filename = f"audios/{event.wa_id}.ogg"
            os.makedirs("audios", exist_ok=True)
            with open(filename, "wb") as f:
                f.write(audio_bytes)
            
            Logger.info(f"✅ Audio guardado en: {filename}")