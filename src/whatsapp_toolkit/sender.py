from typing import Optional
import requests
from .instance import WhatsAppInstance
from .utils import timeout_response, HttpResponse





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

    def send_text(
        self, number: str, text: str, link_preview: bool = True, delay_ms: int = 0
    ) -> str:
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

    def send_media(
        self,
        number: str,
        media_b64: str,
        filename: str,
        caption: str,
        mediatype: str = "document",
        mimetype: str = "application/pdf",
    ) -> str:
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

    def send_sticker(
        self,
        number: str,
        sticker_b64: str,
        delay: int = 0,
        link_preview: bool = True,
        mentions_everyone: bool = True,
    ) -> str:
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

    def send_location(
        self,
        number: str,
        name: str,
        address: str,
        latitude: float,
        longitude: float,
        delay: int = 0,
    ) -> str:
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

    def send_audio(
        self,
        number: str,
        audio_b64: str,
        delay: int = 0,
        mimetype: str = "audio/ogg; codecs=opus",
        ptt: bool = True,
    ) -> str:
        """Envía un audio tipo nota de voz (OGG/OPUS) y muestra errores reales."""
        payload = {
            "audio": audio_b64,
            "number": number,
            "delay": delay,
            "mimetype": mimetype,
            "ptt": ptt,
        }
        resp = self.post(f"/message/sendWhatsAppAudio/{self.instance}", payload)

        status = resp.status_code if hasattr(resp, "status_code") else 0
        if 200 <= status < 300:
            self.connected = True
            return resp.text

        print(f"❌ Error al enviar audio a {number}: {status} - {getattr(resp, 'text', resp)}")
        self.connected = False
        return ""

    def connect(self, number: str) -> str:
        querystring = {"number": number}
        resp = self.get(f"/instance/connect/{self.instance}", params=querystring)
        return resp.text

    def set_webhook(
        self,
        webhook_url: str,
        enabled: bool = True,
        webhook_by_events: bool = True,
        webhook_base64: bool = True,
        events: Optional[list] = None,
    ) -> str:
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

    def fetch_groups(self, get_participants: bool = True) -> list[dict]:
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

