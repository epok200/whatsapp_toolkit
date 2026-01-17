from typing import Optional
from .async_instance import AsyncWhatsAppInstance
from .async_sender import AsyncWhatsAppSender

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

    async def initialize(self):
        """(Opcional) Verifica conexión al arrancar."""
        # En async, los constructores no pueden hacer IO. 
        # Si necesitas validar algo al inicio, hazlo aquí.
        pass
    
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