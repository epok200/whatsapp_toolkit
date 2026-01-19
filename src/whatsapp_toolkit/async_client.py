from typing import Optional
from .async_instance import AsyncWhatsAppInstance
from .async_sender import AsyncWhatsAppSender
from colorstreak import Logger

class AsyncWhatsappClient:
    """
    Cliente principal Asíncrono.
    Fachada que unifica la gestión de la instancia y el envío de mensajes.
    """
    def __init__(self, api_key: str, server_url: str, instance_name: str = "con"):
        # 1. Configuración e Identidad
        self._instance = AsyncWhatsAppInstance(api_key, instance_name, server_url)
        
        # 2. Capacidad de Envío (Inyección de la instancia)
        self._sender = AsyncWhatsAppSender(self._instance)

    # --- CICLO DE VIDA (LifeCycle) ---

    async def initialize(self) -> str:
        """
        Inicialización Inteligente (Healthcheck + Auto-Create).
        Retorna el estado final: 'open', 'created', 'close' (requiere QR).
        """
        Logger.info(f"🔄 Verificando instancia '{self._instance.name_instance}'...")
        
        state = await self._instance.get_state()
        
        if state == "not_found":
            Logger.warning("⚠️ Instancia no encontrada. Creando nueva...")
            result = await self.create()
            if "error" in result:
                Logger.error("❌ Fallo crítico creando instancia.")
                return "error"
            Logger.success("✅ Instancia creada correctamente.")
            return "created" # Probablemente necesite QR ahora
            
        elif state == "open":
            Logger.success("🚀 Instancia ONLINE y lista.")
            return "open"
            
        elif state == "close":
            Logger.warning("⚠️ Instancia existe pero está DESCONECTADA.")
            return "close" # El usuario debe pedir el QR
            
        return state
    
    async def close(self):
        """Libera recursos del cliente HTTP."""
        await self._sender.close()

    # --- GESTIÓN DE INSTANCIA (Delegación) ---

    async def create(self):
        return await self._instance.create()

    async def delete(self):
        return await self._instance.delete()

    async def get_qr(self) -> Optional[str]:
        return await self._instance.get_connection_code()

    # --- MENSAJERÍA (Delegación al Sender) ---

    async def send_text(self, number: str, text: str, delay_ms: int = 0) -> bool:
        return await self._sender.send_text(number, text, delay_ms)

    async def send_media(self, number: str, media_b64: str, filename: str, caption: str = "") -> bool:
        return await self._sender.send_media(number, media_b64, filename, caption)

    async def send_audio(self, number: str, audio_b64: str, ptt: bool = True) -> bool:
        return await self._sender.send_audio(number, audio_b64, ptt=ptt)

    async def send_sticker(self, number: str, sticker_b64: str) -> bool:
        return await self._sender.send_sticker(number, sticker_b64)

    async def send_location(self, number: str, lat: float, long: float, address: str = "") -> bool:
        return await self._sender.send_location(number, lat, long, address)
    
    async def get_message_content(self, message_id: str) -> str:
        """
        Recupera SOLAMENTE el texto del mensaje.
        """
        # El sender ya nos devuelve el registro exacto, sin basura extra.
        msg_record = await self._sender.find_message(message_id)
        
        if not msg_record:
            return "[Mensaje no encontrado]"
            
        # Extraemos el contenido del payload 'message'
        base_msg = msg_record.get("message", {})
        
        # Jerarquía de extracción
        if "conversation" in base_msg:
            return base_msg["conversation"]
            
        elif "extendedTextMessage" in base_msg:
            return base_msg.get("extendedTextMessage", {}).get("text", "")
            
        elif "imageMessage" in base_msg:
            return base_msg.get("imageMessage", {}).get("caption", "[Imagen]")
            
        elif "videoMessage" in base_msg:
             return base_msg.get("videoMessage", {}).get("caption", "[Video]")
             
        return "[Contenido no textual]"
    
    
    async def download_media(self, message_data: dict, convert_to_mp4: bool = False) -> bytes:
        """
        Descarga media usando la URL base y la API Key configurada.
        """
        return await self._sender.download_media(
            message_data=message_data,
            convert_to_mp4=convert_to_mp4
        )