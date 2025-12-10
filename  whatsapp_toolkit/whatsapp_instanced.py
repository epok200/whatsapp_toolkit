from colorstreak import log
from .whatsapp import WhatsappClient
from django.conf import settings
from celery import shared_task


API_KEY = settings.API_KEY
INSTANCE = settings.INSTANCE
SERVER_URL = settings.SERVER_URL

@shared_task
def send_whatsapp_message_async(number: str, message: str):
    log.library(f"Enviando mensaje a {number}: '{message}'")
    client = WhatsappClient(api_key=API_KEY, server_url=SERVER_URL, instance_name=INSTANCE)
    return client.send_text(number, message)


@shared_task
def send_whatsapp_media_async(number: str, media_b64: str, filename: str, caption: str, mediatype: str = "document", mimetype: str = "application/pdf"):
    log.library(f"Enviando media a {number}: '{filename}'")
    client = WhatsappClient(api_key=API_KEY, server_url=SERVER_URL, instance_name=INSTANCE)
    return client.send_media(number, media_b64, filename, caption, mediatype, mimetype)




def send_text(number: str, message: str):
    from colorstreak import log
    log.library(f"Programando tarea para {number}")
    send_whatsapp_message_async.delay(number, message)
    

def send_media(number: str, media_b64: str, filename: str, caption: str, mediatype: str = "document", mimetype: str = "application/pdf"):
    from colorstreak import log
    log.library(f"Programando tarea para enviar media a {number}")
    send_whatsapp_media_async.delay(number, media_b64, filename, caption, mediatype, mimetype)