
# Whatsapp Toolkit

Este módulo permite el envío de mensajes, archivos y multimedia por WhatsApp, con manejo avanzado de conexión, errores y administración de instancias.


## Componentes principales

- **whatsapp.py**: Cliente principal para WhatsApp, incluye administración de instancias, conexión QR, envío de mensajes, archivos, multimedia, ubicación, audio y stickers.
- **whatsapp_instanced.py**: Utilidades avanzadas para instancias y flujos personalizados, incluyendo envío asíncrono de mensajes y archivos usando Celery.

---

## Ejemplos y recomendaciones de uso

### 1. Inicialización y conexión
Conecta tu cliente y asegura la conexión antes de enviar mensajes.
```python
from epok_toolkit.messaging.whatsapp import WhatsappClient

client = WhatsappClient(api_key="tu_api_key", server_url="https://api.whatsapp.com", instance_name="EPOK")
client.ensure_connected()  # Muestra QR y enlaza la instancia si es necesario
```
**Tip:** El método `ensure_connected` reintenta y muestra QR hasta enlazar la instancia.

### 2. Enviar mensajes de texto
```python
client.send_text(number="521234567890", text="Hola desde EPOK Toolkit!")
```

### 3. Enviar archivos y multimedia
Envía documentos, imágenes, stickers, audio y ubicación:
```python
# Enviar PDF
with open("ticket.pdf", "rb") as f:
    import base64
    pdf_b64 = base64.b64encode(f.read()).decode()
client.send_media(number="521234567890", media_b64=pdf_b64, filename="ticket.pdf", caption="Tu ticket", mediatype="document", mimetype="application/pdf")

# Enviar sticker
client.send_sticker(number="521234567890", sticker_b64=sticker_b64)

# Enviar ubicación
client.send_location(number="521234567890", name="EPOK", address="Calle 123", latitude=21.123, longitude=-101.456)

# Enviar audio
client.send_audio(number="521234567890", audio_b64=audio_b64)
```

### 4. Administración de instancias y grupos
```python
client.create_instance()      # Crea una nueva instancia en el servidor
client.delete_instance()      # Elimina la instancia
client.fetch_groups()         # Obtiene todos los grupos y participantes
```


### 6. Envío asíncrono con whatsapp_instanced.py
Envía mensajes y archivos en segundo plano usando Celery:
```python
from epok_toolkit.messaging.whatsapp_instanced import send_text, send_media

# Enviar mensaje de texto de forma asíncrona
send_text(number="521234567890", message="Hola desde EPOK Toolkit!")

# Enviar archivo PDF de forma asíncrona
send_media(number="521234567890", media_b64=pdf_b64, filename="ticket.pdf", caption="Tu ticket")
```
**Tip:** Configura Celery y los settings de API_KEY, INSTANCE y SERVER_URL para habilitar el envío asíncrono.

---

## Más información
Consulta la documentación de cada archivo para detalles avanzados, recomendaciones y ejemplos específicos.

## Instalación

Con UV Package Manager:
```bash
uv add whatsapp-toolkit
```

Con pip:
```bash
pip install whatsapp-toolkit
```
## Requisitos
- Python 3.10 o superior
- requests  >=2.32.5

