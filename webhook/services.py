#import io

import qrcode
from colorstreak import Logger
#from groq import AsyncGroq, RateLimitError

from .config import  WHATSAPP_SERVER_URL, client_whatsapp #, GROQ_API_KEY,

EVOLUTION_BASE_URL = WHATSAPP_SERVER_URL

# groq_client = AsyncGroq(api_key=GROQ_API_KEY)



# async def speech_to_text(audio_bytes: bytes) -> str:
#     """
#     Función ficticia para convertir audio a texto.
#     En un caso real, aquí se integraría con un servicio de STT.
#     """
#     try:
#         audio_file = io.BytesIO(audio_bytes)
#         audio_file.name = "audio.ogg"
        
#         transcription = await groq_client.audio.transcriptions.create(
#             file=audio_file,
#             model="whisper-large-v3",
#             prompt="El audio es en español. Transcríbelo tal cual. ponle emojis si hay emociones.",
#         )
        
#         return transcription.text
    
#     except RateLimitError:
#         Logger.error("🚦 Tráfico alto en Groq (Rate Limit). Esperando...")
#         return "⚠️ El sistema está saturado, intenta de nuevo en un minuto."
        
#     except Exception as e:
#         Logger.error(f"❌ Error en STT: {e}")
#         return "⚠️ Ocurrió un error al procesar el audio."




async def get_qr()-> None:
    """ Obtiene y muestra el código QR para la autenticación de WhatsApp. """
    Logger.info("✨ Solicitando QR...")
    try:
        qr_string = await client_whatsapp.get_qr()
        
        if qr_string:
            Logger.success("📸 ESCANEA ESTE CÓDIGO:")
            
            qr = qrcode.QRCode()
            qr.add_data(qr_string)
            
            print("\n\n") 
            qr.print_ascii(invert=True) 
            print("\n\n")
            # TODO: IMPLEMENTAR REFRESCAR AUTOMÁTICO SI CADUCA
        else:
            Logger.error("❌ No se pudo obtener el código QR.")
    except Exception as e:
        Logger.error(f"❌ Error al obtener QR: {e}")

    