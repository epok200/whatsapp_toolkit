import httpx
import base64
import io
from groq import AsyncGroq
from colorstreak import Logger
from .config import WHATSAPP_SERVER_URL, GROQ_API_KEY



EVOLUTION_BASE_URL = WHATSAPP_SERVER_URL

groq_client = AsyncGroq(api_key=GROQ_API_KEY)



async def speach_to_text(audio_bytes: bytes) -> str:
    """
    Función ficticia para convertir audio a texto.
    En un caso real, aquí se integraría con un servicio de STT.
    """
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.ogg"  
        
        # 2. Petición a la API
        transcription = await groq_client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3", 
            prompt="El audio es en español. Transcríbelo tal cual. ponle emojis si hay emociones.", 
        )
        
        return transcription.text
    
    except Exception as e:
        Logger.error(f"[STT Service] Error: {e}")
        return "Error al procesar el audio."





async def download_media(instance_id: str, message_data: dict, api_key: str, convert_to_mp4: bool = False) -> bytes:
    """
    Descarga media usando la URL base y la API Key que le pasemos dinámicamente.
    """
    # Limpieza de URL por si acaso tiene slash al final
    base_url = EVOLUTION_BASE_URL.rstrip("/")
    url = f"{base_url}/chat/getBase64FromMediaMessage/{instance_id}"
    
    # --- DEBUG VITAL: Esto nos dirá la verdad en los logs ---
    Logger.debug(f"[Media] URL destino: {url}")
    Logger.debug(f"[Media] Usando API Key: {api_key[:5]}...") # Solo muestra el inicio por seguridad
    # ------------------------------------------------------

    headers = {
        "apikey": api_key, # Usamos la que viene del webhook
        "Content-Type": "application/json"
    }

    payload = {
        "message": message_data,
        "convertToMp4": convert_to_mp4
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            base64_str = data.get("base64")
            
            if not base64_str:
                Logger.error("La API conectó pero no devolvió base64")
                raise ValueError("No se recibió base64 en la respuesta")

            return base64.b64decode(base64_str)

        except httpx.ConnectError:
            Logger.error(f"❌ ERROR DE RED: No se puede conectar a {url}")
            Logger.error("💡 TIP: ¿Estás en Docker? Asegúrate que EVOLUTION_URL sea 'http://host.docker.internal:8080'")
            raise ValueError("Error de conexión al servidor de media")
        except Exception as e:
            Logger.error(f"[Media Service] Error: {e}")
            raise ValueError("Error al descargar media")



