import os

#from colorstreak import Logger
from dotenv import load_dotenv

from whatsapp_toolkit import AsyncWhatsappClient

load_dotenv()

# Groq 
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Whatsapp 
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY", "YOUR_WHATSAPP_API_KEY")
WHATSAPP_INSTANCE = os.getenv("WHATSAPP_INSTANCE", "main")
WHATSAPP_SERVER_URL = os.getenv("WHATSAPP_SERVER_URL", "http://host.docker.internal:8080")

#Logger.debug(f"⚙️ Configurando cliente WhatsApp con instancia '{WHATSAPP_INSTANCE}' y servidor '{WHATSAPP_SERVER_URL}' | API Key: '{WHATSAPP_API_KEY}'")

client_whatsapp = AsyncWhatsappClient(
    api_key=WHATSAPP_API_KEY,
    instance_name=WHATSAPP_INSTANCE,
    server_url=WHATSAPP_SERVER_URL,
)