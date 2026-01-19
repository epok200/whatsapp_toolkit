import io
from groq import AsyncGroq, RateLimitError
from colorstreak import Logger
from .config import WHATSAPP_SERVER_URL, GROQ_API_KEY



EVOLUTION_BASE_URL = WHATSAPP_SERVER_URL

groq_client = AsyncGroq(api_key=GROQ_API_KEY)



async def speech_to_text(audio_bytes: bytes) -> str:
    """
    Función ficticia para convertir audio a texto.
    En un caso real, aquí se integraría con un servicio de STT.
    """
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.ogg"
        
        transcription = await groq_client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
            prompt="El audio es en español. Transcríbelo tal cual. ponle emojis si hay emociones.",
        )
        
        return transcription.text
    
    except RateLimitError:
        Logger.error("🚦 Tráfico alto en Groq (Rate Limit). Esperando...")
        return "⚠️ El sistema está saturado, intenta de nuevo en un minuto."
        
    except Exception as e:
        Logger.error(f"❌ Error en STT: {e}")
        return "⚠️ Ocurrió un error al procesar el audio."
