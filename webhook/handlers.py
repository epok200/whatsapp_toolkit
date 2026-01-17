from colorstreak import Logger
from .dispatcher import webhook_manager
from .schemas import MessageUpsert
from .services import download_media
from .config import client_whatsapp, WHATSAPP_API_KEY



def speach_to_text() -> str:
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
        
        # Simular conversión de audio a texto
        Logger.info(f"Id del grupo/usuario: {event.remote_jid}")
        transcription = speach_to_text()
        
        
        client_whatsapp.send_text(
            number=event.remote_jid,
            text=transcription
        )
        