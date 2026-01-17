from colorstreak import Logger
from .dispatcher import webhook_manager
from .schemas.message import MessageUpsert
from .services import download_media, speach_to_text
from .config import client_whatsapp, WHATSAPP_API_KEY






@webhook_manager.on("messages.upsert", model=MessageUpsert)
async def handle_messages(event: MessageUpsert):
    """
    Handler para eventos de mensajes nuevos (upsert).
    """
    
    if not event.from_me:
        return  
    
    if event.message_type == "audioMessage":
        Logger.info(f"🎙️ Procesando audio de {event.media_seconds} segundos...")
        
        real_apikey = event.apikey or WHATSAPP_API_KEY

        audio_bytes = await download_media(
            instance_id=event.instance_id or "main",
            message_data=event.raw, 
            api_key=real_apikey
        )
        
        Logger.info(f"Id del grupo/usuario: {event.remote_jid}")
        transcription = await speach_to_text(audio_bytes)
        
        
        client_whatsapp.send_text(
            number=event.remote_jid,
            text=transcription
        )
        