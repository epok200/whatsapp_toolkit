from colorstreak import Logger
from .services import download_media, speach_to_text
from .config import client_whatsapp
from whatsapp_toolkit.webhook import MessageRouter, MessageType


message_router = MessageRouter()


@message_router.text()
async def handler_text(event):
    key_word = "@rorro"
    message =  event.body.lower().split()
    
    if key_word in message:
        await client_whatsapp.send_text(
            number=event.remote_jid,
            text="Hola guapo, sacate el papoi"
        )
    Logger.info(f"💬 Mensaje de texto recibido: {event.body}")
        

@message_router.on(MessageType.AUDIO_MESSAGE)
async def handler_audio(event):
        Logger.info(f"🎙️ Procesando audio de {event.media_seconds} segundos...")
        
        audio_bytes = await download_media(
            instance_id=event.instance,
            message_data=event.raw, 
            api_key=event.apikey
        )
        
        transcription = await speach_to_text(audio_bytes)
        
        
        await client_whatsapp.send_text(
            number=event.remote_jid,
            text=transcription
        )