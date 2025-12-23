
# Whatsapp Toolkit

Versión: **1.5.1**

Librería ligera para enviar mensajes de WhatsApp a través de la API de Envole (WhatsApp Baileys).

Permite:

- Crear y administrar instancias de WhatsApp.
- Conectar una instancia escaneando un código QR.
- Enviar mensajes de texto, documentos (PDF), imágenes, stickers, ubicación y audio (nota de voz).

Toda la API pública se expone desde el módulo `whatsapp_toolkit`.

---

## Instalación

Con UV Package Manager:

```bash
uv add whatsapp-toolkit
```

Con pip:

```bash
pip install whatsapp-toolkit
```

### Requisitos

- Python 3.10 o superior
- `requests >= 2.32.5`

---

## Arrancar el server local (integrado)

La librería ya incluye un modo de **arranque del server** (Evolution API) pensado para desarrollo local, usando Docker Compose. El flujo de uso está tal cual en los tests (ver `test/test_wakpeup_evo.py`).

### 1) Generar plantillas (docker-compose + env)

Esto crea (en el directorio que elijas):

- `docker-compose.yml`
- `.env.example` (ejemplo; debes copiarlo a `.env` y completar secretos)
- `wakeup_evolution.sh`

```python
from whatsapp_toolkit import devtools

devtools.init_local_evolution(
    path=".",
    overwrite=False,
    verbose=True,
)
```

### 2) Configurar secretos para Docker

Copia `.env.example` a `.env` y configura al menos:

- `AUTHENTICATION_API_KEY` (la API key del server Evolution)
- `POSTGRES_PASSWORD`

Además, para el cliente Python, normalmente usarás:

- `WHATSAPP_API_KEY`
- `WHATSAPP_INSTANCE`
- `WHATSAPP_SERVER_URL` (por defecto `http://localhost:8080/`)

### 3) Levantar / ver logs / bajar el stack desde Python

Ejemplo (idéntico al test):

```python
from whatsapp_toolkit import devtools

stack = devtools.local_evolution(path=".")

stack.start(
    detached=False,
    build=True,
    verbose=True,
)

# Ver logs en vivo
stack.logs(follow=True)
```

Comandos útiles:

```python
from whatsapp_toolkit import devtools

stack = devtools.local_evolution(".")

stack.start(detached=True)   # Levanta en background
stack.stop()                 # Stop sin borrar volúmenes
stack.down(volumes=False)    # Down (opcional: volumes=True para limpiar datos)
stack.logs(service=None)     # o service="evolution-api"
```

### Alternativa: script shell

Si prefieres, también puedes levantar con el script:

```bash
./wakeup_evolution.sh
```

UI del manager:

- `http://localhost:8080/manager/`

---

## Componentes principales

```python
from whatsapp_toolkit import (
    WhatsappClient,
    PDFGenerator,
    obtener_gif_base64,
    obtener_imagen_base64,
)
```

- `WhatsappClient`: cliente principal para gestionar la instancia y enviar mensajes.
- `PDFGenerator`: utilidad para generar un PDF simple y devolverlo en base64 listo para enviar.
- `obtener_gif_base64()`: descarga un GIF y lo devuelve en base64 para usarlo como sticker.
- `obtener_imagen_base64()`: lee una imagen incluida en el paquete y la devuelve en base64 para enviarla como foto.

Internamente se usan los objetos `WhatsAppInstance` y `WhatsAppSender`, pero normalmente no necesitas usarlos directamente.

---

## Configuración rápida

La forma más sencilla de trabajar es usando variables de entorno, igual que en los tests del proyecto.

Variables de entorno esperadas:

- `WHATSAPP_API_KEY`: API key de Envole.
- `WHATSAPP_INSTANCE`: nombre de la instancia (por ejemplo, `"con"`).
- `WHATSAPP_SERVER_URL`: URL del servidor de Envole. Si no se define, se usa `"http://localhost:8080/"`.

Ejemplo mínimo de inicialización:

```python
import os
from whatsapp_toolkit import WhatsappClient

API_KEY = os.getenv("WHATSAPP_API_KEY", "")
INSTANCE = os.getenv("WHATSAPP_INSTANCE", "con")
SERVER_URL = os.getenv("WHATSAPP_SERVER_URL", "http://localhost:8080/")

client = WhatsappClient(API_KEY, SERVER_URL, INSTANCE)

# Si la instancia aún no está enlazada, muestra QR y escanea con tu WhatsApp
client.connect_instance_qr()
```

Nota: `WhatsappClient` inicializa internamente el sender cuando detecta que la instancia ya está enlazada.
Si acabas de escanear el QR, puede ser necesario reiniciar el proceso y crear un nuevo `WhatsappClient`.

---

## Enviar mensajes básicos

### Texto

Los números deben ir en formato internacional, por ejemplo México: `5214771234567`.

```python
client.send_text(
    number="5214771234567",
    text="¡Hola! Este es un mensaje de prueba 🚀",
    delay_ms=0,  # opcional, delay entre envíos en milisegundos
)
```

### PDF como documento

Usando el generador incluido, igual que en los tests:

```python
from whatsapp_toolkit import PDFGenerator

pdf_b64 = PDFGenerator.generar_pdf_base64(
    titulo="Prueba de PDF",
    subtitulo="Este PDF fue generado automáticamente.",
)

client.send_media(
    number="5214771234567",
    media_b64=pdf_b64,
    filename="prueba_envole_api.pdf",
    caption="Aquí tienes el PDF solicitado.",
    # mediatype y mimetype por default ya son de documento/PDF
)
```

### Imagen como foto

El propio paquete trae una imagen de ejemplo que puedes reutilizar tal como se hace en los tests:

```python
from whatsapp_toolkit import obtener_imagen_base64

imagen_b64 = obtener_imagen_base64()

client.send_media(
    number="5214771234567",
    media_b64=imagen_b64,
    filename="prueba_imagen.jpg",
    caption="Aquí tienes la imagen solicitada.",
    mediatype="image",
    mimetype="image/jpeg",
)
```

### Sticker

Puedes enviar un GIF como sticker pasando el base64 del GIF animado:

```python
from whatsapp_toolkit import obtener_gif_base64

gif_b64 = obtener_gif_base64()

client.send_sticker(
    number="5214771234567",
    sticker_b64=gif_b64,
)
```

### Ubicación

```python
client.send_location(
    number="5214771234567",
    name="Ubicación de prueba",
    address="Calle Falsa 123, Ciudad Ejemplo",
    latitude=19.4326,
    longitude=-99.1332,
)
```

### Audio (nota de voz)

Para enviar audio solo necesitas una cadena base64 del archivo OGG/OPUS (o WAV) que quieras mandar. El proyecto incluye en los tests un ejemplo de generación de audio con Piper, pero en producción puedes usar cualquier TTS o grabación propia:

```python
audio_b64 = "..."  # audio en base64 (OGG/OPUS recomendado)

client.send_audio(
    number="5214771234567",
    audio_b64=audio_b64,
)
```

---

## Administración de instancia y grupos

Algunos métodos útiles del cliente:

```python
# Crear y borrar instancia
client.create_instance()       # Crea una nueva instancia en el servidor Envole
client.delete_instance()       # Elimina la instancia actual

# Forzar mostrar QR manualmente en cualquier momento
client.connect_instance_qr()

# Obtener grupos (2 sabores)
# - raw: lista de dicts tal cual responde la API
groups_raw = client.get_groups_raw(get_participants=True)

# - typed: parsea/valida a modelos Pydantic (ver whatsapp_toolkit.schemas)
groups = client.get_groups_typed(get_participants=True)

# Forzar conexión a un número específico (cuando la API lo soporta)
client.connect_number("5214771234567")
```

### Obtener grupos (raw vs typed)

La librería incluye una forma nueva y más cómoda de **obtener y trabajar con grupos**.

- `client.get_groups_raw(get_participants=True)` devuelve `list[dict]` (JSON crudo del endpoint `/group/fetchAllGroups/{instance}`), útil si quieres guardarlo tal cual.
- `client.get_groups_typed(get_participants=True)` devuelve un objeto `Groups` (Pydantic), útil para buscar/filtrar y trabajar con tipos.

Ejemplo recomendado (similar a lo que hace [test/test_api.py](test/test_api.py)):

```python
from whatsapp_toolkit import WhatsappClient
from whatsapp_toolkit.schemas import Groups

client = WhatsappClient(API_KEY, SERVER_URL, INSTANCE)

# Si la instancia aún no está enlazada, muestra QR y escanea
# client.connect_instance_qr()

grupos: Groups | None = client.get_groups_typed(get_participants=True)
if grupos is None:
    raise RuntimeError("No se pudo obtener la lista de grupos")

print(grupos)                 # resumen: cuántos grupos y cuántos fallaron
print(grupos.count_by_kind()) # community_root / community_announce_child / regular_group

# Buscar por texto (match parcial, con scoring simple)
for g in grupos.search_group("club"):
    print(g.id, g.subject, g.kind)

# Buscar por ID exacto
g = grupos.get_group_by_id("120363405715130432@g.us")
if g:
    print(g.subject, "participantes:", len(g.participants))
```

Notas:

- Si llamas con `get_participants=False`, el endpoint puede devolver menos datos; en ese caso, `get_groups_typed()` puede marcar algunos grupos como inválidos y moverlos a `Groups.fails`.
- Si necesitas persistir los resultados para analizarlos offline, usa `get_groups_raw()` y guárdalo como JSON.

### Cache de grupos (MongoDB)

Para evitar pedir los grupos a la API en cada ejecución, puedes activar cache persistente usando `MongoCacheBackend`.

Cómo funciona:

- La clave de cache se calcula por instancia y por el flag `get_participants`.
- Se guarda un “snapshot” en Mongo con campo `created_at` y un índice TTL. Cuando el documento expira, Mongo lo elimina automáticamente.
- Para usarlo, crea el backend y pásalo a `WhatsappClient(..., cache=backend)`. Luego llama `get_groups_typed(..., cache=True)`.

Ejemplo (basado en [test/test_api.py](test/test_api.py)):

```python
import os
from whatsapp_toolkit import WhatsappClient, MongoCacheBackend
from whatsapp_toolkit.schemas import Groups

API_KEY = os.getenv("WHATSAPP_API_KEY", "")
INSTANCE = os.getenv("WHATSAPP_INSTANCE", "con")
SERVER_URL = os.getenv("WHATSAPP_SERVER_URL", "http://localhost:8080/")
URL_MONGO = os.getenv("URL_MONGO", "")  # ej: mongodb://user:pass@localhost:27017/db

cache_engine = MongoCacheBackend(
    uri=URL_MONGO,
    ttl_seconds=1000,  # segundos
)
cache_engine.warmup()  # asegura conexión + índices

client = WhatsappClient(
    api_key=API_KEY,
    server_url=SERVER_URL,
    instance_name=INSTANCE,
    cache=cache_engine,
)

grupos: Groups | None = client.get_groups_typed(
    get_participants=False,
    cache=True,  # <- usa Mongo primero; si no hay, pega a la API y guarda snapshot
)
print(grupos.count_by_kind() if grupos else "Sin grupos")
```

Notas:

- Si Mongo no está disponible, el cliente no revienta: el cache registra el error y sigue intentando obtener desde la API.
- Si cambias `ttl_seconds`, el backend ajusta el índice TTL recreándolo si hace falta.

---

## Flujo de prueba completo (similar a test_api_cruda)

Un flujo típico para pruebas locales se parece a lo que hay en `test/test_api_cruda.py`:

```python
import os
from whatsapp_toolkit import WhatsappClient, PDFGenerator, obtener_gif_base64, obtener_imagen_base64

API_KEY = os.getenv("WHATSAPP_API_KEY", "")
INSTANCE = os.getenv("WHATSAPP_INSTANCE", "con")
SERVER_URL = os.getenv("WHATSAPP_SERVER_URL", "http://localhost:8080/")

client = WhatsappClient(API_KEY, SERVER_URL, INSTANCE)

# Si la instancia aún no está enlazada, muestra QR y escanea
client.connect_instance_qr()

numero = "5214771234567"  # tu número o un grupo

# Texto
client.send_text(numero, "¡Hola! Esta es una prueba de envío de mensajes vía Envole API 🚀")

# PDF
pdf_b64 = PDFGenerator.generar_pdf_base64("Prueba de PDF", "Este es un PDF generado y enviado.")
client.send_media(numero, pdf_b64, filename="prueba.pdf", caption="Aquí tienes el PDF.")

# Sticker
gif_b64 = obtener_gif_base64()
client.send_sticker(numero, gif_b64)

# Imagen
img_b64 = obtener_imagen_base64()
client.send_media(numero, img_b64, filename="prueba.jpg", caption="Imagen de prueba", mediatype="image", mimetype="image/jpeg")

# Ubicación
client.send_location(numero, "Ubicación de prueba", "Calle Falsa 123", 19.4326, -99.1332)
```

Con esto deberías poder replicar y adaptar fácilmente el comportamiento que se demuestra en los tests del repositorio.


