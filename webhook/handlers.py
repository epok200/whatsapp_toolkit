from colorstreak import Logger
from .dispatcher import EventDispatcher
from .schemas.message import MessageUpsert
from .services import download_media, speach_to_text
from .config import client_whatsapp, WHATSAPP_API_KEY
from .router import MessageRouter
from .message_type import MessageType


webhook_manager = EventDispatcher()
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
        
        real_apikey = event.apikey or WHATSAPP_API_KEY

        audio_bytes = await download_media(
            instance_id=event.instance_id or "main",
            message_data=event.raw, 
            api_key=real_apikey
        )
        
        Logger.info(f"Id del grupo/usuario: {event.remote_jid}")
        transcription = await speach_to_text(audio_bytes)
        
        
        await client_whatsapp.send_text(
            number=event.remote_jid,
            text=transcription
        )


@webhook_manager.on("messages.upsert", model=MessageUpsert)
async def handle_messages(event: MessageUpsert):
    """
    Handler para eventos de mensajes nuevos (upsert).
    """
    es_mi_mensaje = event.from_me is True or event.from_me == "true"
    
    if not es_mi_mensaje:
        return  
    
    await message_router.route(event)
    