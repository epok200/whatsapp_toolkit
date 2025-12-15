from .utils import HttpResponse
import requests



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

