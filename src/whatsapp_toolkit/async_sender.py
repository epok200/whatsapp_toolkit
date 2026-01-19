import base64
from typing import Any, Dict, Optional

import httpx
from colorstreak import Logger

from .async_instance import AsyncWhatsAppInstance


class AsyncWhatsAppSender:
    def __init__(self, instance: AsyncWhatsAppInstance):
        # Composición: El sender "vive" gracias a la info de la instancia
        self.instance_name = instance.name_instance
        self.base_url = instance.server_url
        self.headers = instance.headers
        
        # Cliente HTTP persistente (Mejora brutalmente el rendimiento)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=20.0,
            verify=False # Evolution a veces usa certificados self-signed
        )

    async def close(self):
        """Cierra la sesión HTTP al apagar la app."""
        await self.client.aclose()

    async def _post(self, endpoint: str, payload: Dict[str, Any]) -> Optional[httpx.Response]:
        """Método interno para manejar todas las peticiones POST de forma segura."""
        try:
            resp = await self.client.post(endpoint, json=payload)
            # Logger.debug(f"📡 API Response [{resp.status_code}]: {endpoint}")
            return resp
        except httpx.TimeoutException:
            Logger.error(f"⏳ Timeout conectando a: {endpoint}")
        except Exception as e:
            Logger.error(f"❌ Error de red en sender: {e}")
        return None

    # --- MÉTODOS PÚBLICOS DE ENVÍO ---

    async def send_text(self, number: str, text: str, delay_ms: int = 0) -> bool:
        payload = {
            "number": number,
            "text": text,
            "delay": delay_ms,
            "linkPreview": True
        }
        resp = await self._post(f"/message/sendText/{self.instance_name}", payload)
        return resp is not None and 200 <= resp.status_code < 300

    async def send_media(self, number: str, media_b64: str, filename: str, caption: str = "", mimetype: str = "application/pdf") -> bool:
        payload = {
            "number": number,
            "media": media_b64,
            "fileName": filename,
            "caption": caption,
            "mimetype": mimetype,
            "mediatype": "document" # Evolution suele autodetectar, pero "document" es seguro
        }
        resp = await self._post(f"/message/sendMedia/{self.instance_name}", payload)
        return resp is not None and 200 <= resp.status_code < 300

    async def send_audio(self, number: str, audio_b64: str, delay: int = 0, ptt: bool = True) -> bool:
        payload = {
            "number": number,
            "audio": audio_b64,
            "delay": delay,
            "mimetype": "audio/ogg; codecs=opus", # Estándar de WhatsApp
            "ptt": ptt # True = Nota de voz, False = Archivo de audio
        }
        resp = await self._post(f"/message/sendWhatsAppAudio/{self.instance_name}", payload)
        return resp is not None and 200 <= resp.status_code < 300

    async def send_sticker(self, number: str, sticker_b64: str) -> bool:
        payload = {
            "number": number,
            "sticker": sticker_b64
        }
        resp = await self._post(f"/message/sendSticker/{self.instance_name}", payload)
        return resp is not None and 200 <= resp.status_code < 300

    async def send_location(self, number: str, lat: float, long: float, address: str = "", name: str = "") -> bool:
        payload = {
            "number": number,
            "latitude": lat,
            "longitude": long,
            "address": address,
            "name": name
        }
        resp = await self._post(f"/message/sendLocation/{self.instance_name}", payload)
        return resp is not None and 200 <= resp.status_code < 300
    
    async def find_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca y limpia la respuesta. Devuelve el mensaje RAW limpio o None.
        """
        payload = {"where": {"key": {"id": message_id}}}
        
        resp = await self._post(f"/chat/findMessages/{self.instance_name}", payload)

        if resp is not None and 200 <= resp.status_code < 300:
            data = resp.json()

            # Estructura detectada en tus logs:
            # {'messages': {'records': [{'message': ...}]}}
            
            if isinstance(data, dict):
                msgs_container = data.get("messages", {})
                
                # Caso A: Estructura anidada con 'records' (Tu caso actual)
                if isinstance(msgs_container, dict) and "records" in msgs_container:
                    records = msgs_container["records"]
                    if isinstance(records, list) and len(records) > 0:
                        return records[0]
                
                # Caso B: Estructura de lista directa (Versiones viejas de Evo)
                elif isinstance(msgs_container, list) and len(msgs_container) > 0:
                    return msgs_container[0]

        return None
    
    
    async def download_media(self, message_data: dict, convert_to_mp4: bool = False) -> bytes:
        """
        Descarga media reutilizando la conexión persistente del sender.
        """
        # Endpoint de Evolution para recuperar el Base64
        url = f"/chat/getBase64FromMediaMessage/{self.instance_name}"
        
        payload = {
            "message": message_data,
            "convertToMp4": convert_to_mp4
        }

        try:
            # Reutilizamos _post para aprovechar el manejo de errores
            response = await self._post(url, payload)
            
            if response is None or not (200 <= response.status_code < 300):
                Logger.error(f"❌ ERROR API Media. Code: {response.status_code if response else 'None'}")
                raise ValueError("Error en respuesta de API Media")
            
            data = response.json()
            base64_str = data.get("base64")
            
            if not base64_str:
                Logger.error("La API conectó pero no devolvió base64")
                raise ValueError("No se recibió base64")

            return base64.b64decode(base64_str)

        except Exception as e:
            Logger.error(f"[Media Download] Error: {e}")
            # Devolvemos bytes vacíos o re-lanzamos según prefieras. 
            # Aquí re-lanzamos para que el handler sepa que falló.
            raise e
