from .whatsapp import WhatsappClient
from dotenv import load_dotenv
import os

load_dotenv()


API_KEY = os.getenv("WHATSAPP_API_KEY")
# TODO: La instancia deberia ser creada y seteada (no desde variable de entorno)
INSTANCE = os.getenv("WHATSAPP_INSTANCE")
SERVER_URL = os.getenv("WHATSAPP_SERVER_URL")


def send_message(number: str, message: str):
    client = WhatsappClient(api_key=API_KEY, server_url=SERVER_URL, instance_name=INSTANCE)
    return client.send_text(number, message)



def send_media(number: str, media_b64: str, filename: str, caption: str, mediatype: str = "document", mimetype: str = "application/pdf"):
    client = WhatsappClient(api_key=API_KEY, server_url=SERVER_URL, instance_name=INSTANCE)
    return client.send_media(number, media_b64, filename, caption, mediatype, mimetype)



