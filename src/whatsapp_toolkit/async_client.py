from typing import Optional
from .async_instance import AsyncWhatsAppInstance
from .async_sender import AsyncWhatsAppSender
from colorstreak import Logger
from .webhook.schemas import MessageUpsert

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
        Retorna: 'open', 'connecting', 'close', 'created' o 'error'.
        """
        Logger.info(f"🔄 Verificando instancia '{self._instance.name_instance}'...")
        
        state = await self._instance.get_state()
        
        match state:
            case "open":
                Logger.success("🚀 Instancia ONLINE y lista.")
                return "open"

            case "connecting":
                Logger.info("🟡 Instancia intentando conectar...")
                return "connecting"
            
            case "close":
                Logger.warning("⚠️ Instancia existe pero está DESCONECTADA (Requiere QR).")
                return "close"
                
            case "not_found":
                # AQUÍ MANTENEMOS LA LÓGICA DE AUTO-CREACIÓN
                Logger.warning("⚠️ Instancia no encontrada. Creando nueva...")
                result = await self.create()
                
                if "error" in result:
                    Logger.error("❌ Fallo crítico creando instancia.")
                    return "error"
                    
                Logger.success("✅ Instancia creada correctamente.")
                return "created"
                
            case _:
                Logger.error(f"❌ Estado desconocido o error: {state}")
                return "error"
    
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

    async def send_text(self, number: str, text: str, delay_ms: int = 0, quoted: dict | None = None) -> bool:
        return await self._sender.send_text(number, text, delay_ms, quoted=quoted)

    async def send_media(self, number: str, media_b64: str, filename: str, caption: str = "", quoted: dict | None = None) -> bool:
        return await self._sender.send_media(number, media_b64, filename, caption, quoted=quoted)

    async def send_audio(self, number: str, audio_b64: str, ptt: bool = True, quoted: dict | None = None) -> bool:
        return await self._sender.send_audio(number, audio_b64, ptt=ptt, quoted=quoted)

    async def send_sticker(self, number: str, sticker_b64: str, quoted: dict | None = None) -> bool:
        return await self._sender.send_sticker(number, sticker_b64, quoted=quoted)

    async def send_reaction(self, remote_jid: str, message_id: str, reaction: str, from_me: bool = False) -> bool:
        return await self._sender.send_reaction(remote_jid, message_id, reaction, from_me)

    async def send_location(self, number: str, lat: float, long: float, address: str = "", quoted: dict | None = None) -> bool:
        return await self._sender.send_location(number, lat, long, address, quoted=quoted)
    
    async def get_message(self, message_id: str) -> Optional[MessageUpsert]:
        """
        Recupera un mensaje por ID y lo devuelve como un objeto MessageUpsert.
        Esto permite usar las mismas propiedades (.body, .media_url, .is_audio)
        que usas en el webhook.
        """
        raw_msg = await self._sender.find_message(message_id)
        
        if not raw_msg:
            return None


        payload_simulado = {
            "event": "messages.upsert",
            "instance": self._instance.name_instance, 
            "data": raw_msg
        }

        return MessageUpsert.model_validate(payload_simulado)
    
    
    async def download_media(self, message_data: dict, convert_to_mp4: bool = False) -> bytes:
        """
        Descarga media usando la URL base y la API Key configurada.
        """
        return await self._sender.download_media(
            message_data=message_data,
            convert_to_mp4=convert_to_mp4
        )