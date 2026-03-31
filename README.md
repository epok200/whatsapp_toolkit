
# Whatsapp Toolkit

Version: **2.2.0**

Libreria Python para interactuar con WhatsApp a traves de [Evolution API](https://doc.evolution-api.com/). Soporta clientes sincronos y asincronos, envio de mensajes, reacciones, respuestas citadas, webhook con routing de eventos, y herramientas de desarrollo local.

---

## Instalacion

```bash
uv add whatsapp-toolkit
```

O con pip:

```bash
pip install whatsapp-toolkit
```

**Requisitos:** Python 3.10+

---

## Configuracion

Variables de entorno necesarias:

| Variable | Descripcion | Default |
|---|---|---|
| `WHATSAPP_API_KEY` | API key de Evolution API | - |
| `WHATSAPP_INSTANCE` | Nombre de la instancia | `"con"` |
| `WHATSAPP_SERVER_URL` | URL del servidor Evolution | `"http://localhost:8080/"` |

---

## Cliente Sincrono

```python
import os
from whatsapp_toolkit import WhatsappClient

client = WhatsappClient(
    api_key=os.getenv("WHATSAPP_API_KEY", ""),
    server_url=os.getenv("WHATSAPP_SERVER_URL", "http://localhost:8080/"),
    instance_name=os.getenv("WHATSAPP_INSTANCE", "con"),
)

# Conectar escaneando QR si la instancia no esta enlazada
client.connect_instance_qr()
```

### Enviar mensajes

Los numeros van en formato internacional (ej. Mexico: `5214771234567`).

```python
# Texto
client.send_text("5214771234567", "Hola mundo")

# Imagen
client.send_media("5214771234567", imagen_b64, "foto.jpg", "Mi foto", mediatype="image", mimetype="image/jpeg")

# Documento (PDF)
client.send_media("5214771234567", pdf_b64, "archivo.pdf", "Documento adjunto")

# Audio (nota de voz)
client.send_audio("5214771234567", audio_b64)

# Sticker
client.send_sticker("5214771234567", gif_b64)

# Ubicacion
client.send_location("5214771234567", "Mi lugar", "Calle 123", 19.4326, -99.1332)
```

### Reaccionar a un mensaje

```python
client.send_reaction(
    remote_jid="5214771234567@s.whatsapp.net",
    message_id="BAE58DA6CBC941BC",
    reaction="🚀",
    from_me=False,
)

# Quitar reaccion
client.send_reaction("5214771234567@s.whatsapp.net", "BAE58DA6CBC941BC", reaction="")
```

### Responder/citar un mensaje

Todos los metodos `send_*` aceptan el parametro opcional `quoted`:

```python
quoted = {
    "key": {"id": "BAE58DA6CBC941BC"},
    "message": {"conversation": "Mensaje original"}
}

client.send_text("5214771234567", "Esta es mi respuesta", quoted=quoted)
client.send_media("5214771234567", img_b64, "foto.jpg", "Respuesta con imagen", mediatype="image", mimetype="image/jpeg", quoted=quoted)
```

### Administracion de instancia

```python
client.create_instance()
client.delete_instance()
client.connect_instance_qr()
client.connect_number("5214771234567")
```

### Grupos

```python
# Raw (lista de dicts)
groups_raw = client.get_groups_raw(get_participants=True)

# Tipado (modelo Pydantic)
from whatsapp_toolkit.schemas import Groups

groups: Groups = client.get_groups_typed(get_participants=True)
print(groups.count_by_kind())

for g in groups.search_group("club"):
    print(g.id, g.subject)
```

---

## Cliente Asincrono

```python
from whatsapp_toolkit import AsyncWhatsappClient

client = AsyncWhatsappClient(
    api_key="tu-api-key",
    server_url="http://localhost:8080/",
    instance_name="con",
)

# Inicializacion inteligente (healthcheck + auto-create)
state = await client.initialize()  # -> "open", "connecting", "close", "created", "error"
```

### Enviar mensajes (async)

```python
await client.send_text("5214771234567", "Hola async")
await client.send_media("5214771234567", img_b64, "foto.jpg", "Caption")
await client.send_audio("5214771234567", audio_b64)
await client.send_sticker("5214771234567", sticker_b64)
await client.send_location("5214771234567", 19.4326, -99.1332, "Direccion")
```

### Reacciones y respuestas (async)

```python
# Reaccionar
await client.send_reaction("5214771234567@s.whatsapp.net", "MSG_ID", "❤️")

# Responder citando
quoted = {"key": {"id": "MSG_ID"}, "message": {"conversation": "Texto original"}}
await client.send_text("5214771234567", "Mi respuesta", quoted=quoted)
```

### Recuperar mensajes y media

```python
# Obtener un mensaje por ID
msg = await client.get_message("BAE58DA6CBC941BC")
if msg:
    print(msg.body, msg.message_type)

# Descargar media de un mensaje
media_bytes = await client.download_media(msg.raw_message)
```

### Cerrar cliente

```python
await client.close()
```

---

## Webhook

El toolkit incluye un sistema de webhook con dos niveles de routing: **WebhookManager** (nivel evento) y **MessageRouter** (nivel tipo de mensaje).

### Setup rapido

La forma mas directa de conectar ambos niveles:

```python
from whatsapp_toolkit.webhook import WebhookManager, MessageRouter, EventType, MessageType, MessageUpsert

manager = WebhookManager()
router = MessageRouter()

# Conectar el router al manager (sin boilerplate)
manager.include_router(router)

# Registrar handlers por tipo de mensaje
@router.text()
async def handle_text(event: MessageUpsert):
    print(f"{event.push_name}: {event.body}")

@router.on(MessageType.IMAGE_MESSAGE)
async def handle_image(event: MessageUpsert):
    print(f"Imagen recibida: {event.media_url}")

# En tu endpoint de FastAPI:
@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    await manager.dispatch(payload)
```

### WebhookManager (nivel evento)

Recibe el JSON crudo del webhook y lo despacha a los handlers registrados.

```python
manager = WebhookManager()

# Multiples handlers para el mismo evento (todos se ejecutan)
@manager.on(EventType.MESSAGES_UPSERT)
async def log_message(event: MessageUpsert):
    print(f"LOG: {event.push_name} -> {event.body}")

@manager.on(EventType.MESSAGES_UPSERT)
async def save_message(event: MessageUpsert):
    await db.save(event.raw)

@manager.on(EventType.CONNECTION_UPDATE)
async def handle_connection(event):
    print(f"Estado: {event.state}")
```

#### include_router()

Conecta un `MessageRouter` al manager sin necesidad de crear un handler puente:

```python
manager = WebhookManager()
router = MessageRouter()

# Antes (manual):
@manager.on(EventType.MESSAGES_UPSERT)
async def bridge(event: MessageUpsert):
    await router.route(event)

# Ahora (directo):
manager.include_router(router)
```

Puedes combinar handlers directos + routers:

```python
manager = WebhookManager()
router = MessageRouter()

# Handler directo para logging
@manager.on(EventType.MESSAGES_UPSERT)
async def log_all(event: MessageUpsert):
    print(f"[LOG] {event.message_type}: {event.body}")

# Router para logica por tipo
manager.include_router(router)

@router.text()
async def reply_text(event: MessageUpsert):
    await client.send_text(event.remote_jid, "Recibido!")
```

### MessageRouter (nivel tipo de mensaje)

Enruta mensajes a handlers segun su tipo, con filtros opcionales.

```python
router = MessageRouter()

@router.text()  # Captura conversation + extendedTextMessage
async def handle_text(event: MessageUpsert):
    print(f"Texto: {event.body}")

@router.on(MessageType.AUDIO_MESSAGE)
async def handle_audio(event: MessageUpsert):
    print(f"Audio: {event.media_seconds}s")

@router.on(MessageType.REACTION_MESSAGE)
async def handle_reaction(event: MessageUpsert):
    print(f"{event.reaction_text} al mensaje {event.reaction_target_id}")
```

#### Filtros: is_group y from_me

Todos los decoradores (`on`, `text`) aceptan filtros opcionales:

| Filtro | `True` | `False` | `None` (default) |
|---|---|---|---|
| `is_group` | Solo grupos | Solo chats directos | Ambos |
| `from_me` | Solo mensajes propios | Solo de otros | Ambos |

```python
# Solo texto en grupos, de otros usuarios
@router.text(is_group=True, from_me=False)
async def handle_group_text(event: MessageUpsert):
    print(f"[{event.push_name}] en grupo: {event.body}")

# Solo texto en chats directos
@router.text(is_group=False)
async def handle_dm(event: MessageUpsert):
    print(f"DM de {event.push_name}: {event.body}")

# Solo imagenes en grupos
@router.on(MessageType.IMAGE_MESSAGE, is_group=True)
async def handle_group_image(event: MessageUpsert):
    print(f"Imagen en grupo: {event.media_url}")

# Solo audios que NO son mios
@router.on(MessageType.AUDIO_MESSAGE, from_me=False)
async def handle_incoming_audio(event: MessageUpsert):
    print(f"Audio recibido de {event.push_name}")
```

#### Handler por defecto (fallback)

Se ejecuta cuando llega un tipo de mensaje que ningun handler maneja:

```python
@router.default()
async def fallback(event: MessageUpsert):
    print(f"Tipo no manejado: {event.message_type} de {event.push_name}")
```

### Detectar mensajes citados (replies)

```python
@router.text()
async def handle_text(event: MessageUpsert):
    if event.is_reply:
        print(f"Respuesta al mensaje {event.quoted_message_id}")
        print(f"Texto citado: {event.quoted_body}")
        print(f"Autor original: {event.quoted_participant}")

    print(f"Mensaje: {event.body}")
```

### Ejemplo completo: bot echo con filtros

```python
from fastapi import FastAPI, Request
from whatsapp_toolkit import AsyncWhatsappClient
from whatsapp_toolkit.webhook import WebhookManager, MessageRouter, EventType, MessageType, MessageUpsert

app = FastAPI()
manager = WebhookManager()
router = MessageRouter()
manager.include_router(router)

client = AsyncWhatsappClient(api_key="...", server_url="...", instance_name="con")

# Echo solo en DMs, ignorando mensajes propios
@router.text(is_group=False, from_me=False)
async def echo(event: MessageUpsert):
    await client.send_text(event.remote_jid, f"Dijiste: {event.body}")

# Reaccionar con un corazon a todas las imagenes en grupos
@router.on(MessageType.IMAGE_MESSAGE, is_group=True, from_me=False)
async def react_to_images(event: MessageUpsert):
    await client.send_reaction(event.remote_jid, event.wa_id, "❤️")

# Responder a mensajes citados
@router.text(from_me=False)
async def handle_reply(event: MessageUpsert):
    if event.is_reply:
        await client.send_text(
            event.remote_jid,
            f"Respondiste a: {event.quoted_body}",
            quoted={"key": {"id": event.wa_id}, "message": {"conversation": event.body}}
        )

# Fallback para todo lo demas
@router.default()
async def fallback(event: MessageUpsert):
    await client.send_text(event.remote_jid, "No entiendo ese tipo de mensaje")

@app.post("/webhook")
async def webhook(request: Request):
    await manager.dispatch(await request.json())
```

### Propiedades de MessageUpsert

| Propiedad | Tipo | Descripcion |
|---|---|---|
| `remote_jid` | `str` | JID del chat |
| `from_me` | `bool` | Si el mensaje es propio |
| `wa_id` | `str` | ID del mensaje |
| `push_name` | `str` | Nombre del remitente |
| `participant` | `str \| None` | Participante en grupos |
| `is_group` | `bool` | Si es un grupo |
| `message_type` | `str` | Tipo de mensaje |
| `body` | `str` | Contenido del mensaje |
| `media_url` | `str \| None` | URL del media |
| `media_mime` | `str \| None` | MIME del media |
| `media_seconds` | `int \| None` | Duracion del media |
| `is_sticker` | `bool` | Si es sticker |
| `is_reaction` | `bool` | Si es reaccion |
| `reaction_text` | `str \| None` | Emoji de la reaccion |
| `reaction_target_id` | `str \| None` | ID del mensaje reaccionado |
| `is_reply` | `bool` | Si es respuesta a otro mensaje |
| `quoted_message_id` | `str \| None` | ID del mensaje citado |
| `quoted_participant` | `str \| None` | Autor del mensaje citado |
| `quoted_body` | `str \| None` | Texto del mensaje citado |
| `timestamp` | `int` | Timestamp del mensaje |
| `raw_message` | `dict` | Mensaje raw completo |
| `raw` | `dict` | Data raw completa |

### Tipos de mensaje soportados

| Constante | Valor |
|---|---|
| `MessageType.CONVERSATION` | `"conversation"` |
| `MessageType.EXTENDED_TEXT_MESSAGE` | `"extendedTextMessage"` |
| `MessageType.IMAGE_MESSAGE` | `"imageMessage"` |
| `MessageType.VIDEO_MESSAGE` | `"videoMessage"` |
| `MessageType.DOCUMENT_MESSAGE` | `"documentMessage"` |
| `MessageType.AUDIO_MESSAGE` | `"audioMessage"` |
| `MessageType.STIKER_MESSAGE` | `"stickerMessage"` |
| `MessageType.REACTION_MESSAGE` | `"reactionMessage"` |

---

## Herramientas de desarrollo

### Levantar Evolution API local

```python
from whatsapp_toolkit import devtools

# Generar plantillas (docker-compose + env)
devtools.init_local_evolution(path=".", overwrite=False, verbose=True)

# Levantar el stack
stack = devtools.local_evolution(path=".")
stack.start(detached=True)
stack.logs(follow=True)
stack.stop()
stack.down(volumes=False)
```

UI del manager: `http://localhost:8080/manager/`

---

## Utilidades incluidas

```python
from whatsapp_toolkit import PDFGenerator, obtener_gif_base64, obtener_imagen_base64

# Generar PDF en base64
pdf_b64 = PDFGenerator.generar_pdf_base64("Titulo", "Contenido del PDF")

# Obtener GIF/imagen de ejemplo en base64
gif_b64 = obtener_gif_base64()
img_b64 = obtener_imagen_base64()
```

---

## Cache de grupos (MongoDB)

```python
from whatsapp_toolkit import WhatsappClient, MongoCacheBackend

cache = MongoCacheBackend(uri="mongodb://localhost:27017/db", ttl_seconds=1000)
cache.warmup()

client = WhatsappClient(api_key="...", server_url="...", instance_name="con", cache=cache)
groups = client.get_groups_typed(get_participants=True, cache=True)
```

---

## CLI

```bash
wtk --help
```

---

## Licencia

MIT
