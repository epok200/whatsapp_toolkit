from colorstreak import Logger
from .services import speech_to_text
from .config import client_whatsapp
from whatsapp_toolkit.webhook import MessageRouter, MessageType
from whatsapp_toolkit.webhook.schemas import MessageUpsert


message_router = MessageRouter()


reporte_n = 0

@message_router.on(MessageType.REACTION_MESSAGE)
async def handler_reaction(event: MessageUpsert):
    global reporte_n
    
    emoji = event.reaction_text
    
    if emoji == "🪲":
        
        mensaje = f"[Reporte # {reporte_n}] Generando reporte "
        await client_whatsapp.send_text(
                number=event.remote_jid,
                text=mensaje
            )
        reporte_n += 1


@message_router.on(MessageType.REACTION_MESSAGE)
async def handler_reaction_love(event: MessageUpsert):
    """ Detecta reacciones de amor y responde con un mensaje cariñoso"""
    emoji = event.reaction_text
    
    if emoji == "❤️":
        mensaje_id = event.reaction_target_id
        mensaje_reaccionado =  await client_whatsapp.get_message_content(mensaje_id)
        
        mensaje = f"Te gusto el mensaje _'{mensaje_reaccionado}'_"
        await client_whatsapp.send_text(
                number=event.remote_jid,
                text=mensaje
            )
        


@message_router.text()
async def handler_text(event: MessageUpsert):
    key_word = "@rorro"
    message =  event.body.lower().split()
    
    if key_word in message:
        await client_whatsapp.send_text(
            number=event.remote_jid,
            text="Hola guapo, sacate el papoi"
        )
    Logger.info(f"💬 Mensaje de texto recibido: {event.body}")


@message_router.on(MessageType.AUDIO_MESSAGE)
async def handler_audio(event: MessageUpsert):
        Logger.info(f"🎙️ Procesando audio de {event.media_seconds} segundos...")
        
        try:
            audio_bytes = await client_whatsapp.download_media(
                message_data=event.raw, 
            )
            
            transcription = await speech_to_text(audio_bytes)
            
            
            await client_whatsapp.send_text(
                number=event.remote_jid,
                text=transcription
            )
            
        except Exception as e:
            Logger.error(f"❌ Error al procesar audio: {e}")
            await client_whatsapp.send_text(
                number=event.remote_jid,
                text="⚠️ Ocurrió un error al procesar el audio."
            )
 

@message_router.on(MessageType.IMAGE_MESSAGE)
async def handler_image(event: MessageUpsert):
    Logger.info(f"🖼️ Imagen recibida con caption: {event.body}")
    
    await client_whatsapp.send_text(
        number=event.remote_jid,
        text=f"¡Gracias por la imagen! Has dicho: {event.body}"
    )


