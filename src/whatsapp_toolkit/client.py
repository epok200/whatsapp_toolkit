from typing import Optional
from .instance import WhatsAppInstance
from .sender import WhatsAppSender
from .types import Groups







# Decorador para asegurar conexión antes de ejecutar métodos de WhatsappClient que lo requieran
def require_connection(method):
    """
    Decorador para métodos de WhatsappClient que necesitan una conexión activa.
    Llama a `self.ensure_connected()` y solo ejecuta el método original si la
    conexión se confirma; de lo contrario devuelve False.
    """
    from functools import wraps

    @wraps(method)
    def _wrapper(self, *args, **kwargs):
        if not self.ensure_connected():
            print("❌ No fue posible establecer conexión.")
            return False
        return method(self, *args, **kwargs)

    return _wrapper







class WhatsappClient:
    def __init__(self, api_key: str, server_url: str, instance_name: str = "con"):
        self.instance = WhatsAppInstance(api_key, instance_name, server_url)
        self.sender: Optional[WhatsAppSender] = None
        self._auto_initialize_sender()

    def _auto_initialize_sender(self):
        """Solo asigna sender si la instancia está enlazada a WhatsApp."""
        info = WhatsAppSender.get_instance_info(
            self.instance.api_key, self.instance.name_instance, self.instance.server_url
        )
        if info.get("ownerJid"):  # <- si tiene owner, significa que ya está enlazada
            self.sender = WhatsAppSender(self.instance)

    def ensure_connected(self, retries: int = 3, delay: int = 30) -> bool:
        """
        Garantiza que la instancia esté conectada.
        Si aún no existe `self.sender`, intentará crearlo.
        Si la prueba de conexión falla, muestra un QR y reintenta.
        """
        import time

        # Si ya tenemos sender y está marcado como conectado, salimos rápido
        if self.sender and getattr(self.sender, "connected", False):
            return True

        def _init_sender():
            if self.sender is None:
                # Intentar inicializar si la instancia ya está enlazada
                info = WhatsAppSender.get_instance_info(
                    self.instance.api_key,
                    self.instance.name_instance,
                    self.instance.server_url,
                )
                if info.get("ownerJid"):
                    self.sender = WhatsAppSender(self.instance)

        # Primer intento de inicializar el sender
        _init_sender()

        for attempt in range(1, retries + 1):
            if self.sender and self.sender.test_connection_status():
                return True

            print(
                f"[{attempt}/{retries}] Conexión no disponible, mostrando nuevo QR (espera {delay}s)…"
            )
            self.instance.connect_instance_qr()  # muestra nuevo QR
            time.sleep(delay)

            # Reintentar inicializar sender después de mostrar QR
            _init_sender()

        print("❌ No fue posible establecer conexión después de varios intentos.")
        return False

    @require_connection
    def send_text(self, number: str, text: str, link_preview: bool = True, delay_ms: int = 1000):
        sender = self.sender
        if sender is None:
            return False
        return sender.send_text(number, text, link_preview, delay_ms=delay_ms)

    @require_connection
    def send_media(self, number: str, media_b64: str, filename: str, caption: str, mediatype: str = "document", mimetype: str = "application/pdf",):
        sender = self.sender
        if sender is None:
            return False
        return sender.send_media(number, media_b64, filename, caption, mediatype, mimetype)

    @require_connection
    def send_sticker(self, number: str, sticker_b64: str, delay: int = 0, link_preview: bool = True, mentions_everyone: bool = True,):
        sender = self.sender
        if sender is None:
            return False
        return sender.send_sticker(number, sticker_b64, delay, link_preview, mentions_everyone)

    @require_connection
    def send_location(self, number: str, name: str, address: str, latitude: float, longitude: float, delay: int = 0,):
        sender = self.sender
        if sender is None:
            return False
        return sender.send_location(number, name, address, latitude, longitude, delay)

    @require_connection
    def send_audio(self, number: str, audio_b64: str, delay: int = 0):
        sender = self.sender
        if sender is None:
            return False
        return sender.send_audio(number, audio_b64, delay)

    @require_connection
    def connect_number(self, number: str):
        sender = self.sender
        if sender is None:
            return False
        return sender.connect(number)

    @require_connection
    def get_groups_raw(self, get_participants: bool = True) -> list[dict] | None:
        sender = self.sender
        if sender is None:
            return None

        response: list[dict] | None = sender.fetch_groups(get_participants)
        if response is None:
            return None
        return response
    
    @require_connection
    def get_groups_typed(self, get_participants: bool = True) -> Groups | None:
        raw = self.get_groups_raw(get_participants=get_participants)
        if not raw:
            return None
        g = Groups()
        g.upload_groups(raw)
        return g

    def create_instance(self):
        return self.instance.create_instance()

    def delete_instance(self):
        return self.instance.delete_instance()

    def connect_instance_qr(self):
        return self.instance.connect_instance_qr()

