

# ================================ DOTENV EXAMPLE ==============================

_DOTENV_EXAMPLE = """# =========================================
# WhatsApp Toolkit (Python) - configuración local/dev
# =========================================
# NOTA:
# - Este es un archivo de EJEMPLO. Cópialo a `.env` y completa tus secretos.
# - NO subas `.env` al repositorio.

# --- Ajustes del cliente Python ---
WHATSAPP_API_KEY=YOUR_EVOLUTION_API_KEY
WHATSAPP_INSTANCE=fer
WHATSAPP_SERVER_URL=http://localhost:8080/

# --- Secretos compartidos de Docker Compose ---
AUTHENTICATION_API_KEY=YOUR_EVOLUTION_API_KEY
POSTGRES_PASSWORD=change_me
"""


# ================================ WAKEUP SCRIPT ==============================

_WAKEUP_SH = """#!/usr/bin/env bash
set -euo pipefail

# Este script está pensado para macOS/Linux y para Windows vía Git Bash o WSL.
# NO intenta iniciar Docker Desktop/daemon por ti.

echo "[devtools] Iniciando el stack de Evolution API (Docker Compose)"
echo "[devtools] Abrir: http://localhost:8080/manager/"

docker compose down || true
docker compose up${UP_ARGS}
"""


# ================================ MINIMAL PYTHON SCRIPT ==============================

_MAIN_WEBHOOK_PY ="""
#from whatsapp_toolkit import webhook
from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()


app = FastAPI(
    title="WhatsApp Webhook",
    description="A simple WhatsApp webhook using WhatsApp Toolkit and FastAPI",
    version="1.0.0",
    debug=True,
    docs_url="/docs",
)



@app.get("/webhook/whatsapp/health", tags=["WhatsApp Webhook"])
def whatsapp_webhook():
    mensaje = "Todo OK"
    return {"status_code": 200, "message": mensaje}


"""


 # ================================ DOCKER COMPOSE ==============================
 
_DOCKER_COMPOSE = """services:
    evolution-api:
        image: evoapicloud/evolution-api:v{VERSION}
        restart: always
        ports:
            - "8080:8080"
        volumes:
            - evolution-instances:/evolution/instances

        environment:
            # =========================
            # Identidad principal del servidor
            # =========================
            - SERVER_URL=localhost
            - LANGUAGE=en
            - CONFIG_SESSION_PHONE_CLIENT=Evolution API
            - CONFIG_SESSION_PHONE_NAME=Chrome

            # =========================
            # Telemetría (apagada por defecto)
            # =========================
            - TELEMETRY=false
            - TELEMETRY_URL=

            # =========================
            # Autenticación (el secreto permanece en .env / --env-file)
            # =========================
            - AUTHENTICATION_TYPE=apikey
            - AUTHENTICATION_API_KEY=${AUTHENTICATION_API_KEY}
            - AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES=true

            # =========================
            # Base de datos (configuración interna del stack)
            # =========================
            - DATABASE_ENABLED=true
            - DATABASE_PROVIDER=postgresql
            - DATABASE_CONNECTION_URI=postgresql://postgresql:${POSTGRES_PASSWORD}@evolution-postgres:5432/evolution
            - DATABASE_SAVE_DATA_INSTANCE=true
            - DATABASE_SAVE_DATA_NEW_MESSAGE=true
            - DATABASE_SAVE_MESSAGE_UPDATE=true
            - DATABASE_SAVE_DATA_CONTACTS=true
            - DATABASE_SAVE_DATA_CHATS=true
            - DATABASE_SAVE_DATA_LABELS=true
            - DATABASE_SAVE_DATA_HISTORIC=true

            # =========================
            # Caché Redis (configuración interna del stack)
            # =========================
            - CACHE_REDIS_ENABLED=true
            - CACHE_REDIS_URI=redis://evolution-redis:6379
            - CACHE_REDIS_PREFIX_KEY=evolution
            - CACHE_REDIS_SAVE_INSTANCES=true

    evolution-postgres:
        image: postgres:16-alpine
        restart: always
        volumes:
            - evolution-postgres-data:/var/lib/postgresql/data

        environment:
            - POSTGRES_DB=evolution
            - POSTGRES_USER=postgresql
            - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

    evolution-redis:
        image: redis:alpine
        restart: always
        volumes:
            - evolution-redis-data:/data
            
    whatsapp_webhook:
        build:
            context: .
            dockerfile: Dockerfile
        ports:
            - "8002:8002"
        env_file:
            - ./webhook/.env
        restart: unless-stopped


volumes:
    evolution-instances:
    evolution-postgres-data:
    evolution-redis-data:
"""


# ================================ DOCKERFILE WEBHOOK ==============================
_DOCKERFILE="""FROM python:3.13.11-slim
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY webhook/ /app/webhook/

EXPOSE 8002
CMD ["uvicorn", "webhook.main_webhook:app", "--host", "0.0.0.0", "--port", "8002"]
"""











_REQUIREMENTS_TXT = """# This file was autogenerated by uv via the following command:
#    uv export --format requirements-txt --no-hashes

annotated-doc==0.0.4
    # via fastapi
annotated-types==0.7.0
    # via pydantic
anyio==4.12.0
    # via starlette
certifi==2025.11.12
    # via requests
charset-normalizer==3.4.4
    # via
    #   reportlab
    #   requests
click==8.3.1
    # via uvicorn
colorama==0.4.6 ; sys_platform == 'win32'
    # via
    #   click
    #   qrcode
coloredlogs==15.0.1
    # via onnxruntime
colorstreak==2.1.0
    # via whatsapp-toolkit
dotenv==0.9.9
    # via whatsapp-toolkit
exceptiongroup==1.3.1 ; python_full_version < '3.11'
    # via anyio
fastapi==0.124.4
    # via whatsapp-toolkit
flatbuffers==25.9.23
    # via onnxruntime
h11==0.16.0
    # via uvicorn
humanfriendly==10.0
    # via coloredlogs
idna==3.11
    # via
    #   anyio
    #   requests
mpmath==1.3.0
    # via sympy
numpy==2.2.6 ; python_full_version < '3.11'
    # via onnxruntime
numpy==2.3.5 ; python_full_version >= '3.11'
    # via onnxruntime
onnxruntime==1.23.2
    # via piper-tts
packaging==25.0
    # via onnxruntime
pillow==12.0.0
    # via
    #   reportlab
    #   whatsapp-toolkit
piper-tts==1.3.0
    # via whatsapp-toolkit
platformdirs==4.5.1
    # via whatsapp-toolkit
protobuf==6.33.2
    # via onnxruntime
pydantic==2.12.5
    # via fastapi
pydantic-core==2.41.5
    # via pydantic
pyreadline3==3.5.4 ; sys_platform == 'win32'
    # via humanfriendly
python-dotenv==1.2.1
    # via dotenv
qrcode==8.2
    # via whatsapp-toolkit
reportlab==4.4.6
    # via whatsapp-toolkit
requests==2.32.5
    # via whatsapp-toolkit
starlette==0.50.0
    # via fastapi
sympy==1.14.0
    # via onnxruntime
typing-extensions==4.15.0
    # via
    #   anyio
    #   exceptiongroup
    #   fastapi
    #   pydantic
    #   pydantic-core
    #   starlette
    #   typing-inspection
    #   uvicorn
typing-inspection==0.4.2
    # via pydantic
urllib3==2.6.1
    # via requests
uvicorn==0.38.0
    # via whatsapp-toolkit
"""