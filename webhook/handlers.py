from colorstreak import Logger
#from .services import speech_to_text
from .config import client_whatsapp
from whatsapp_toolkit.webhook import MessageRouter, MessageType
from whatsapp_toolkit.webhook.schemas import MessageUpsert
#import base64


message_router = MessageRouter()


reporte_n = 0

@message_router.on(MessageType.REACTION_MESSAGE)
async def bug_reporter(event: MessageUpsert):
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
async def like(event: MessageUpsert):
    """ Handler para reaccionar a un mensaje con un corazón. """
    emoji = event.reaction_text
    
    if emoji == "❤️":
        
        mensaje_id = event.reaction_target_id
        if not mensaje_id:
            Logger.error("❌ No se encontró el ID del mensaje reaccionado.")
            return
        
        mensaje_reaccionado =  await client_whatsapp.get_message_content(mensaje_id)
        
        mensaje = f"Te gusto el mensaje _'{mensaje_reaccionado}'_"
        await client_whatsapp.send_text(
                number=event.remote_jid,
                text=mensaje
            )


@message_router.text()
async def handler_text(event: MessageUpsert):
    key_word = "@bot"
    message =  event.body.lower().split()
    
    if key_word in message:
        await client_whatsapp.send_text(
            number=event.remote_jid,
            text="🤖 ¡Hola! ¿En qué puedo ayudarte hoy?"
        )
    Logger.info(f"💬 Mensaje de texto recibido: {event.body}")


@message_router.on(MessageType.AUDIO_MESSAGE)
async def handler_audio(event: MessageUpsert):
        Logger.info(f"🎙️ Procesando audio de {event.media_seconds} segundos...")
        
        # try:
        #     audio_bytes = await client_whatsapp.download_media(
        #         message_data=event.raw, 
        #     )
            
        #     transcription = await speech_to_text(audio_bytes)
            
            
        #     await client_whatsapp.send_text(
        #         number=event.remote_jid,
        #         text=transcription
        #     )
            
        # except Exception as e:
        #     Logger.error(f"❌ Error al procesar audio: {e}")
        #     await client_whatsapp.send_text(
        #         number=event.remote_jid,
        #         text="⚠️ Ocurrió un error al procesar el audio."
        #     )
 

@message_router.on(MessageType.IMAGE_MESSAGE)
async def handler_image(event: MessageUpsert):
    Logger.info(f"🖼️ Imagen recibida con caption: {event.body}")
    
    # try:
    #     image_bytes = await client_whatsapp.download_media(
    #         message_data=event.raw, 
    #     )
    #     image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    #     await client_whatsapp.send_media(
    #         number=event.remote_jid,
    #         media_b64=image_b64,
    #         filename="imagen_recibida.jpg",
    #         caption="Aquí está la imagen que enviaste."
    #     )
        
    # except Exception as e:
    #     Logger.error(f"❌ Error al procesar imagen: {e}")
    #     await client_whatsapp.send_text(
    #         number=event.remote_jid,
    #         text="⚠️ Ocurrió un error al procesar la imagen."
    #     )


