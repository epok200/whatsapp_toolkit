import requests
from typing import Optional
from functools import wraps
from dataclasses import dataclass


def timeout_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.Timeout:
            print("La solicitud ha excedido el tiempo de espera.")
            return HttpResponse(status_code=408, text="Timeout", json_data=None)
        except requests.RequestException as e:
            print(f"Error en la solicitud: {e}")
            return HttpResponse(
                status_code=500, text="Error", json_data={"error": str(e)}
            )

    return wrapper


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


@dataclass
class HttpResponse:
    status_code: int
    text: str
    json_data: Optional[dict] = None


class WhatsAppInstance:
    def __init__(self, api_key: str, instance: str, server_url: str):
        self.api_key = api_key
        self.name_instance = instance
        self.status = "disconnected"
        self.server_url = server_url.rstrip("/")
        self.headers = {"apikey": self.api_key, "Content-Type": "application/json"}

    def create_instance(self) -> HttpResponse:
        """Crea una nueva instancia de WhatsApp usando la API de Envole."""
        url = f"{self.server_url}/instance/create"
        payload = {
            "instanceName": self.name_instance,
            "integration": "WHATSAPP-BAILEYS",
            "syncFullHistory": False,
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return HttpResponse(response.status_code, response.text, response.json())

    def delete_instance(self) -> HttpResponse:
        """Elimina una instancia de WhatsApp usando la API de Envole."""
        url = f"{self.server_url}/instance/delete/{self.name_instance}"
        response = requests.delete(url, headers=self.headers)
        return HttpResponse(response.status_code, response.text)

    def show_qr(self, qr_text: str) -> None:
        """Genera un código QR a partir de `qr_text` y lo muestra con el visor por defecto."""
        import qrcode

        qr = qrcode.QRCode(border=2)
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image()
        img.show()

    def connect_instance_qr(self) -> None:
        """Conecta una instancia de WhatsApp y muestra una imagen"""
        url = f"{self.server_url}/instance/connect/{self.name_instance}"
        response = requests.get(url, headers=self.headers)
        codigo = response.json().get("code")
        self.show_qr(codigo)

    def mode_connecting(self):
        """
        Se intentará por 30 min el mantenter intentos de conexión a la instancia
        generando un qr cada 10 segundos, si es exitoso se podra enviar un mensaje,
        si después de eso no se conecta, se devolvera un error
        """
        pass


class WhatsAppSender:
    def __init__(self, instance: WhatsAppInstance):
        self.instance = instance.name_instance
        self.server_url = instance.server_url
        self.headers = instance.headers
        self._instance_obj = instance
        self.connected = True  # estado de conexión conocido

    def test_connection_status(self) -> bool:
        cel_epok = "5214778966517"
        print(f"Probando conexión enviando mensaje a {cel_epok}...")
        ok = bool(self.send_text(cel_epok, "ping"))
        self.connected = ok
        return ok

    @timeout_response
    def get(self, endpoint: str, params: Optional[dict] = None) -> requests.Response:
        url = f"{self.server_url}{endpoint}"
        return requests.get(url, headers=self.headers, params=params)

    def put(self, endpoint: str) -> requests.Response:
        url = f"{self.server_url}{endpoint}"
        return requests.put(url, headers=self.headers)

    def post(self, endpoint: str, payload: dict):
        url = f"{self.server_url}{endpoint}"
        request = requests.post(url, json=payload, headers=self.headers, timeout=10)
        # if timeout:
        try:
            return request
        except requests.Timeout:
            print("Request timed out")
            return HttpResponse(status_code=408, text="Timeout", json_data=None)

    def send_text(self, number: str, text: str, link_preview: bool = True, delay_ms: int = 0) -> str:
        payload = {
            "number": number,
            "text": text,
            "delay": delay_ms,
            "linkPreview": link_preview,
        }
        print(f"Enviando mensaje a {number}: {text}")
        resp = self.post(f"/message/sendText/{self.instance}", payload)

        # Si la solicitud se convirtió en HttpResponse por timeout
        status = resp.status_code if hasattr(resp, "status_code") else 0

        if 200 <= status < 300:
            self.connected = True
            return resp.text

        # Fallo: marcar desconexión y reportar
        print(f"Error al enviar mensaje a {number}: {status} - {resp.text}")
        self.connected = False
        return False

    def send_media(self, number: str, media_b64: str, filename: str, caption: str, mediatype: str = "document", mimetype: str = "application/pdf") -> str:
        payload = {
            "number": number,
            "mediatype": mediatype,
            "mimetype": mimetype,
            "caption": caption,
            "media": media_b64,
            "fileName": filename,
            "delay": 0,
            "linkPreview": False,
            "mentionsEveryOne": False,
        }
        resp = self.post(f"/message/sendMedia/{self.instance}", payload)
        return resp.text

    def send_sticker(self, number: str, sticker_b64: str, delay: int = 0, link_preview: bool = True, mentions_everyone: bool = True) -> str:
        """Envía un sticker a un contacto específico."""
        payload = {
            "number": number,
            "sticker": sticker_b64,
            "delay": delay,
            "linkPreview": link_preview,
            "mentionsEveryOne": mentions_everyone,
        }
        resp = self.post(f"/message/sendSticker/{self.instance}", payload)
        return resp.text

    def send_location(self, number: str, name: str, address: str, latitude: float, longitude: float, delay: int = 0) -> str:
        """Envía una ubicación a un contacto."""
        payload = {
            "number": number,
            "name": name,
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
            "delay": delay,
        }
        resp = self.post(f"/message/sendLocation/{self.instance}", payload)
        return resp.text

    def send_audio(self, number: str, audio_b64: str, delay: int = 0) -> str:
        """Envía un audio en formato base64 a un contacto."""
        payload = {
            "audio": audio_b64,
            "number": number,
            "delay": delay,
        }
        resp = self.post(f"/message/sendWhatsAppAudio/{self.instance}", payload)
        return resp.text

    def connect(self, number: str) -> str:
        querystring = {"number": number}
        resp = self.get(f"/instance/connect/{self.instance}", params=querystring)
        return resp.text

    def set_webhook(self, webhook_url: str, enabled: bool = True, webhook_by_events: bool = True, webhook_base64: bool = True, events: Optional[list] = None) -> str:
        """Configura el webhook para la instancia."""
        if events is None:
            events = ["SEND_MESSAGE"]
        payload = {
            "url": webhook_url,
            "enabled": enabled,
            "webhookByEvents": webhook_by_events,
            "webhookBase64": webhook_base64,
            "events": events,
        }
        resp = self.post(f"/webhook/set/{self.instance}", payload)
        return resp.text

    def fetch_groups(self, get_participants: bool = True) -> list:
        """Obtiene todos los grupos y sus participantes."""
        params = {"getParticipants": str(get_participants).lower()}
        resp = self.get(f"/group/fetchAllGroups/{self.instance}", params=params)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(
                f"Error al obtener grupos: {resp.status_code} - {resp.text}"
            )

    @staticmethod
    def fetch_instances(api_key: str, server_url: str) -> list:
        """Obtiene todas las instancias disponibles en el servidor."""
        url = f"{server_url}/instance/fetchInstances"
        headers = {"apikey": api_key}
        response = requests.get(url, headers=headers, verify=False)
        # Puede ser una lista o dict, depende del backend
        try:
            return response.json()
        except Exception:
            return []

    @staticmethod
    def get_instance_info(api_key: str, instance_name: str, server_url: str):
        """Busca la info de una instancia específica por nombre, robusto a diferentes formatos de respuesta."""
        instances = WhatsAppSender.fetch_instances(api_key, server_url)

        # Normalizar a lista para iterar
        if isinstance(instances, dict):
            instances = [instances]
        # print(f"Buscando instancia: {instance_name} en {len(instances)} instancias disponibles.")
        for item in instances:
            data = (
                item.get("instance")
                if isinstance(item, dict) and "instance" in item
                else item
            )
            # print(data)
            if not isinstance(data, dict):
                continue  # Formato inesperado para us

            if data.get("name") == instance_name:
                return data
        return {}



class WhatsappClient:
    """
    Cliente para interactuar con la API de WhatsApp.
    """
    def __init__(self, api_key: str, server_url: str, instance_name: str = "EPOK"):
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
        return self.sender.send_text(number, text, link_preview, delay_ms=delay_ms)

    @require_connection
    def send_media(self, number: str, media_b64: str, filename: str, caption: str, mediatype: str = "document", mimetype: str = "application/pdf"):
        return self.sender.send_media(number, media_b64, filename, caption, mediatype, mimetype)

    @require_connection
    def send_sticker(self, number: str, sticker_b64: str, delay: int = 0, link_preview: bool = True, mentions_everyone: bool = True):
        return self.sender.send_sticker(number, sticker_b64, delay, link_preview, mentions_everyone)

    @require_connection
    def send_location(self, number: str, name: str, address: str, latitude: float, longitude: float, delay: int = 0):
        return self.sender.send_location(number, name, address, latitude, longitude, delay)

    @require_connection
    def send_audio(self, number: str, audio_b64: str, delay: int = 0):
        return self.sender.send_audio(number, audio_b64, delay)

    @require_connection
    def connect_number(self, number: str):
        return self.sender.connect(number)

    @require_connection
    def fetch_groups(self, get_participants: bool = True):
        return self.sender.fetch_groups(get_participants)

    def create_instance(self):
        return self.instance.create_instance()

    def delete_instance(self):
        return self.instance.delete_instance()

    def connect_instance_qr(self):
        return self.instance.connect_instance_qr()