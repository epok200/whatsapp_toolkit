# ================================ DOCKER COMPOSE WEBHOOK ==============================
# Vive en: .wtk/webhook/docker-compose.yml
#
# ✅ Minimal y correcto con tu restricción:
# - build context SIEMPRE es ".wtk/webhook/" (no sube al root)
# - el código del usuario NO se copia, se MONTA con volumes
# - el .env del usuario NO se copia, se LEE con env_file
#
# Variables (las setea tu init dentro del env_compose):
# - HOST_PORT: puerto en tu máquina (ej. 8081)
# - WEBHOOK_DIR_REL: ruta relativa desde .wtk/webhook/ hacia ./webhook (ej. ../../webhook)
# - WEBHOOK_ENV_REL: ruta relativa desde .wtk/webhook/ hacia ./webhook/.env (ej. ../../webhook/.env)
# - PYTHON_VERSION: version base de python para build (ej. 3.13.11)
#
_DOCKER_COMPOSE_WEBHOOK = """services:
  whatsapp-webhook:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        PYTHON_VERSION: "${PYTHON_VERSION}"
    ports:
      - "${PORT}:8000"
    env_file:
      - "${WEBHOOK_ENV_REL}"
    volumes:
      - "${WEBHOOK_DIR_REL}:/app/webhook"
    restart: unless-stopped
"""


# ================================ DOCKERFILE WEBHOOK ==============================
# Vive en: .wtk/webhook/Dockerfile
#
# ✅ Minimal y correcto:
# - NO hace COPY del webhook del usuario (porque está fuera del context)
# - instala requirements desde .wtk/webhook/requirements.txt
# - corre uvicorn apuntando al archivo montado por volumen: /app/webhook/main_webhook.py
# - host 0.0.0.0 (si pones localhost, te encierras en el contenedor)
#
# Variables:
# - ${PYTHON_VERSION} viene como build-arg desde docker-compose.yml
#
_DOCKERFILE_WEBHOOK = """ARG PYTHON_VERSION=3.13.11
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# El código vive montado en /app/webhook (no se copia en build)
WORKDIR /app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "webhook.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""


# ================================ DOTENV COMPOSE WEBHOOK ==============================
# Vive en: .wtk/webhook/.env
#
# Este archivo lo usa TU tooling con: docker compose --env-file .env up
# Es el "mbfile-compose" que tú mencionas.
#
# Variables que tú INYECTAS en init (defaults):
# - {HOST_PORT} (ej. 8000 o 8081)
# - {PYTHON_VERSION} (ej. 3.13.11)
# - {WEBHOOK_DIR_REL} (ej. ../../webhook)
# - {WEBHOOK_ENV_REL} (ej. ../../webhook/.env)
#
_DOTENV_COMPOSE_WEBHOOK = """# =========================================
# WhatsApp Toolkit - Webhook (Docker Compose)
# =========================================
# Este archivo controla:
# - Puerto HOST
# - Ruta a carpeta ./webhook (para montar como volumen)
# - Ruta a ./webhook/.env (runtime env del contenedor)
# - Versión base de Python (build arg)
#
# Nota: rutas RELATIVAS son relativas a .wtk/webhook/
# Ejemplo típico:
# WEBHOOK_DIR_REL=../../webhook
# WEBHOOK_ENV_REL=../../webhook/.env

PORT={PORT}
PYTHON_VERSION={PYTHON_VERSION}

WEBHOOK_DIR_REL={WEBHOOK_DIR_REL}
WEBHOOK_ENV_REL={WEBHOOK_ENV_REL}
"""


# =============================== REQUIREMENTS WEBHOOK ==============================
_REQUIREMENTS_WEBHOOK = """whatsapp-toolkit=={VERSION}

# Agrega tus dependencias adicionales aquí:
"""



# =============================== DOTENV WEBHOOK ==============================
# =============================== DOTENV WEBHOOK ==============================
# Vive en: ./webhook/.env
#
# Este es el "mbfile-webhook" (runtime/app) que el usuario edita.
# Docker Compose lo lee por env_file usando WEBHOOK_ENV_REL.
#
# Variables que tú INYECTAS en init:
# - {API_KEY}
#
_DOTENV_WEBHOOK = """# =========================================
# WhatsApp Toolkit - Webhook (runtime/app)
# =========================================
# Este archivo lo consume la app FastAPI dentro del contenedor.
# Si cambias variables aquí, normalmente NO requiere rebuild; solo reiniciar el contenedor.

WHATSAPP_API_KEY={API_KEY}
WHATSAPP_INSTANCE=main
WHATSAPP_SERVER_URL=http://host.docker.internal:8080
"""


# =============================== README WEBHOOK ==============================
# Vive en: ./webhook/README.md
#
# README básico para el usuario final: cómo inicializar, configurar y levantar
# el webhook con Docker Compose usando los DevTools del paquete.
#
_README_WEBHOOK_MD = """# WhatsApp Toolkit - Webhook

Este folder contiene un webhook de ejemplo (FastAPI) para consumir eventos de tu proveedor (Evolution).

## Estructura

- `.wtk/webhook/` (generado por el toolkit)
    - `docker-compose.yml`, `Dockerfile`, `.env`, `requirements.txt`
    - Esta carpeta es el *stack* y es donde se corre `docker compose`.
- `webhook/` (tu código)
    - `main.py`, `config.py`, `manager.py`, `handlers.py`, `services.py`, `.env`
    - Esta carpeta se monta dentro del contenedor como volumen (no se copia en el build).

## Requisitos

- Docker instalado (con `docker compose`).
- Un servidor Evolution accesible desde el contenedor.
    - Por defecto el webhook usa `WHATSAPP_SERVER_URL=http://host.docker.internal:8080`.
    - En macOS/Windows `host.docker.internal` suele funcionar out-of-the-box.

## Configuración

Edita `webhook/.env`:

- `WHATSAPP_API_KEY`: tu API key
- `WHATSAPP_INSTANCE`: nombre de instancia (default: `main`)
- `WHATSAPP_SERVER_URL`: URL base de tu servidor Evolution

## Inicializar el stack

Desde la raíz de tu proyecto:

```bash
whatsapp-toolkit webhook init --api-key "TU_API_KEY"
```

Esto crea/actualiza:

- `.wtk/webhook/*` (archivos de Docker Compose)
- `webhook/*` (código del webhook)

## Levantar el webhook

```bash
whatsapp-toolkit webhook up --build
```

Luego abre la documentación interactiva:

- `http://localhost:{PORT}/docs`

Nota: si ves que el CLI imprime `/doc`, en FastAPI el default suele ser `/docs`.

## Endpoint de entrada

El webhook expone un endpoint único:

- `POST /evolution/webhook/{event_type}`

Ejemplos de `event_type` usados en este scaffold:

- `messages.upsert`
- `connection.update`

Los eventos desconocidos se ignoran (fast-fail) y devuelven `{"status": "ignored"}`.

## Logs

```bash
whatsapp-toolkit webhook logs --follow
```

## Parar y limpiar

```bash
whatsapp-toolkit webhook stop
whatsapp-toolkit webhook down
```
"""

# ================================ MINIMAL PYTHON SCRIPT ==============================
_MAIN_WEBHOOK_PY ='''import asyncio
from contextlib import asynccontextmanager

from colorstreak import Logger
from fastapi import FastAPI, Request

from .config import client_whatsapp
from .manager import webhook_manager
from .services import get_qr


# ==========================================
# 🔄 TAREA DE ARRANQUE (Background)
# ==========================================
async def startup_task():
    await asyncio.sleep(3)
    Logger.info("🔄 [Background] Verificando conexión...")
    
    try:
        status = await client_whatsapp.initialize()
        
        if status in ["created", "close"]:
            await get_qr()
                
        elif status == "open":
            Logger.success("🚀 Sistema ONLINE.")
            
    except Exception as e:
        Logger.error(f"❌ Error en arranque: {e}")
        
# ==========================================
# 🔄 LIFESPAN (Gestión de vida del servidor)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):

    Logger.info("🚀 Webhook System: ONLINE")
    
    asyncio.create_task(startup_task())
    yield
    
    Logger.info("🔌 Cerrando conexión con WhatsApp...")
    await client_whatsapp.close() 
    Logger.info("👋 Bye!")

# ==========================================
# 🚀 APP DEFINITION
# ==========================================
app = FastAPI(
    title="WhatsApp Webhook", 
    debug=True,
    lifespan=lifespan
)

@app.post("/evolution/webhook/{event_type}")
async def endpoint(event_type: str, request: Request):
    """
    Endpoint único de entrada.
    Filtra por URL antes de procesar el JSON (Fast Fail).
    """
    
    if not webhook_manager.knows_event(event_type):
        return {"status": "ignored"}

    Logger.info(f"✅ Procesando evento: {event_type}")
    payload = await request.json()
    
    await webhook_manager.dispatch(payload)
        
    return {"status": "ack"}
'''

# ================================ CONFIG PYTHON SCRIPT ==============================
_CONFIG_WEBHOOK_PY = '''import os

from dotenv import load_dotenv

from whatsapp_toolkit import AsyncWhatsappClient

load_dotenv()

# Groq 
#GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Whatsapp 
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY", "YOUR_WHATSAPP_API_KEY")
WHATSAPP_INSTANCE = os.getenv("WHATSAPP_INSTANCE", "main")
WHATSAPP_SERVER_URL = os.getenv("WHATSAPP_SERVER_URL", "http://host.docker.internal:8080")


client_whatsapp = AsyncWhatsappClient(
    api_key=WHATSAPP_API_KEY,
    instance_name=WHATSAPP_INSTANCE,
    server_url=WHATSAPP_SERVER_URL,
)
'''

# ================================ MANAGER PYTHON SCRIPT ==============================
_MANAGER_WEBHOOK_PY = '''from colorstreak import Logger

from whatsapp_toolkit.webhook import EventType, WebhookManager
from whatsapp_toolkit.webhook.schemas import ConnectionUpdate, MessageUpsert

from .handlers import message_router

webhook_manager = WebhookManager()


@webhook_manager.on(EventType.MESSAGES_UPSERT)
async def handle_messages(event: MessageUpsert):
    """
    Handler para eventos de mensajes nuevos (upsert).
    """
    es_mi_mensaje = event.from_me is True
    if not es_mi_mensaje:
        return  
    
    await message_router.route(event)
    
    
@webhook_manager.on(EventType.CONNECTION_UPDATE)
async def handler_conection(event: ConnectionUpdate):
    try:
        state = event.state
        reason = event.status_reason
        instance = event.instance
        
        Logger.info(f"📡 Estado Instancia '{instance}': {state}")
        
        if state == "open":
            Logger.success("🟢 [Webhook] Conexión establecida exitosamente.")
            
        elif state == "close":
            Logger.error(f"🔴 [Webhook] DESCONEXIÓN DETECTADA. Razón: {reason}")
            
            if reason == 401:
                Logger.warning("⚠️ La sesión fue cerrada (Logout). Se requiere nuevo escaneo de QR.")
                # TODO: Implementar lógica de reconexión si es necesario
                
        elif state == "connecting":
            Logger.info("🟡 Conectando...")

    except Exception as e:
        Logger.error(f"[Webhook] Error crítico en handler de conexión: {e}")
'''
# ================================ HANDLERS PYTHON SCRIPT ==============================
_HANDLERS_WEBHOOK_PY = '''from colorstreak import Logger
#from .services import speech_to_text
from .config import client_whatsapp
from whatsapp_toolkit.webhook import MessageRouter, MessageType
from whatsapp_toolkit.webhook.schemas import MessageUpsert
#import base64


message_router = MessageRouter()


reporte_n = 0

@message_router.on(MessageType.REACTION_MESSAGE)
async def bug_reporter(event: MessageUpsert):
    global reporte_n
    
    emoji = event.reaction_text
    
    if emoji == "🪲":
        
        mensaje = f"[Reporte # {reporte_n}] Generando reporte "
        await client_whatsapp.send_text(
                number=event.remote_jid,
                text=mensaje
            )
        reporte_n += 1


@message_router.on(MessageType.REACTION_MESSAGE)
async def like(event: MessageUpsert):
    """ Handler para reaccionar a un mensaje con un corazón. """
    emoji = event.reaction_text
    
    if emoji == "❤️":
        
        mensaje_id = event.reaction_target_id
        if not mensaje_id:
            Logger.error("❌ No se encontró el ID del mensaje reaccionado.")
            return
        
        mensaje_reaccionado =  await client_whatsapp.get_message_content(mensaje_id)
        
        mensaje = f"Te gusto el mensaje _'{mensaje_reaccionado}'_"
        await client_whatsapp.send_text(
                number=event.remote_jid,
                text=mensaje
            )


@message_router.text()
async def handler_text(event: MessageUpsert):
    key_word = "@bot"
    message =  event.body.lower().split()
    
    if key_word in message:
        await client_whatsapp.send_text(
            number=event.remote_jid,
            text="🤖 ¡Hola! ¿En qué puedo ayudarte hoy?"
        )
    Logger.info(f"💬 Mensaje de texto recibido: {event.body}")


@message_router.on(MessageType.AUDIO_MESSAGE)
async def handler_audio(event: MessageUpsert):
        Logger.info(f"🎙️ Procesando audio de {event.media_seconds} segundos...")
        
        # try:
        #     audio_bytes = await client_whatsapp.download_media(
        #         message_data=event.raw, 
        #     )
            
        #     transcription = await speech_to_text(audio_bytes)
            
            
        #     await client_whatsapp.send_text(
        #         number=event.remote_jid,
        #         text=transcription
        #     )
            
        # except Exception as e:
        #     Logger.error(f"❌ Error al procesar audio: {e}")
        #     await client_whatsapp.send_text(
        #         number=event.remote_jid,
        #         text="⚠️ Ocurrió un error al procesar el audio."
        #     )
 

@message_router.on(MessageType.IMAGE_MESSAGE)
async def handler_image(event: MessageUpsert):
    Logger.info(f"🖼️ Imagen recibida con caption: {event.body}")
    
    # try:
    #     image_bytes = await client_whatsapp.download_media(
    #         message_data=event.raw, 
    #     )
    #     image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    #     await client_whatsapp.send_media(
    #         number=event.remote_jid,
    #         media_b64=image_b64,
    #         filename="imagen_recibida.jpg",
    #         caption="Aquí está la imagen que enviaste."
    #     )
        
    # except Exception as e:
    #     Logger.error(f"❌ Error al procesar imagen: {e}")
    #     await client_whatsapp.send_text(
    #         number=event.remote_jid,
    #         text="⚠️ Ocurrió un error al procesar la imagen."
    #     )
'''
# ================================ SERVICES PYTHON SCRIPT ==============================
_SERVICES_WEBHOOK_PY = '''#import io

import qrcode
from colorstreak import Logger
#from groq import AsyncGroq, RateLimitError

from .config import  WHATSAPP_SERVER_URL, client_whatsapp #, GROQ_API_KEY,

EVOLUTION_BASE_URL = WHATSAPP_SERVER_URL

# groq_client = AsyncGroq(api_key=GROQ_API_KEY)



# async def speech_to_text(audio_bytes: bytes) -> str:
#     """
#     Función ficticia para convertir audio a texto.
#     En un caso real, aquí se integraría con un servicio de STT.
#     """
#     try:
#         audio_file = io.BytesIO(audio_bytes)
#         audio_file.name = "audio.ogg"
        
#         transcription = await groq_client.audio.transcriptions.create(
#             file=audio_file,
#             model="whisper-large-v3",
#             prompt="El audio es en español. Transcríbelo tal cual. ponle emojis si hay emociones.",
#         )
        
#         return transcription.text
    
#     except RateLimitError:
#         Logger.error("🚦 Tráfico alto en Groq (Rate Limit). Esperando...")
#         return "⚠️ El sistema está saturado, intenta de nuevo en un minuto."
        
#     except Exception as e:
#         Logger.error(f"❌ Error en STT: {e}")
#         return "⚠️ Ocurrió un error al procesar el audio."




async def get_qr()-> None:
    """ Obtiene y muestra el código QR para la autenticación de WhatsApp. """
    Logger.info("✨ Solicitando QR...")
    try:
        qr_string = await client_whatsapp.get_qr()
        
        if qr_string:
            Logger.success("📸 ESCANEA ESTE CÓDIGO:")
            
            qr = qrcode.QRCode()
            qr.add_data(qr_string)
            
            print("\\n\\n") 
            qr.print_ascii(invert=True) 
            print("\\n\\n")
            # TODO: IMPLEMENTAR REFRESCAR AUTOMÁTICO SI CADUCA
        else:
            Logger.error("❌ No se pudo obtener el código QR.")
    except Exception as e:
        Logger.error(f"❌ Error al obtener QR: {e}")
'''