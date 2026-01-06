

# ================================ DOTENV ==============================

_DOTENV_EVOLUTION = """# =========================================
# WhatsApp Toolkit (Python) - configuración local/dev
# =========================================
# NOTA:
# - Este es un archivo de creado automaticamente si cambias algo reinica el docker.
# - Sugerencia ignora esta carpeta '.wtk' en tu .gitignore.

# --- Ajustes del cliente Python ---
WHATSAPP_API_KEY={API_KEY}
WHATSAPP_INSTANCE={INSTANCE}
WHATSAPP_SERVER_URL={SERVER_URL}

# --- Secretos compartidos de Docker Compose ---
AUTHENTICATION_API_KEY={API_KEY}
"""



 # ================================ DOCKER COMPOSE EVOLUTION ==============================
 
_DOCKER_COMPOSE_EVOLUTION = """services:
    evolution-api:
        image: evoapicloud/evolution-api:v{VERSION}
        restart: always
        ports:
            - "{PORT}:{PORT}"
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
            - DATABASE_CONNECTION_URI=postgresql://postgresql:change_me@evolution-postgres:5432/evolution
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
            - POSTGRES_PASSWORD=change_me
    evolution-redis:
        image: redis:alpine
        restart: always
        volumes:
            - evolution-redis-data:/data
            



volumes:
    evolution-instances:
    evolution-postgres-data:
    evolution-redis-data:
"""
