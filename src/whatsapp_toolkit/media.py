from io import BytesIO
import base64
import random
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .sender import WhatsAppSender
import requests




class PDFGenerator:
    @staticmethod
    def generar_pdf_base64(titulo: str, subtitulo: str) -> str:
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(72, 740, titulo)
        c.setFont("Helvetica", 16)
        c.drawString(72, 700, subtitulo)
        c.setFont("Helvetica", 12)
        c.drawString(
            72, 670, f"Generado automáticamente: {datetime.now():%Y-%m-%d %H:%M:%S}"
        )
        c.save()
        pdf_buffer.seek(0)
        return base64.b64encode(pdf_buffer.read()).decode("utf-8")


def enviar_media(
    sender: WhatsAppSender,
    numero: str,
    media_b64: str,
    filename: str,
    caption: str,
    mediatype: str,
    mimetype: str,
) -> None:
    print(
        f"Media enviado: {sender.send_media(numero, media_b64, filename, caption, mediatype, mimetype)}"
    )


def obtener_gif_base64() -> str:
    """
    Devuelve un GIF de fiesta codificado en base64 tomado de una lista
    de URLs públicas, sin necesidad de API ni autenticación.
    """
    party_gifs = [
        "https://media.giphy.com/media/l0HUpt2s9Pclgt9Vm/giphy.gif",
    ]
    gif_url = random.choice(party_gifs)

    gif_bytes = requests.get(gif_url, timeout=10).content
    return base64.b64encode(gif_bytes).decode("utf-8")


def obtener_imagen_base64() -> str:
    """
    Devuelve una imagen de fiesta codificada en base64 tomada de una URL pública.
    """
    from pathlib import Path
    base_dir = Path(__file__).parent
    print(f"Base dir: {base_dir}")
    image_url = base_dir / "pc.jpeg"  # Reemplaza con una URL válida
    with open(image_url, "rb") as image_file:
        image_bytes = image_file.read()
    return base64.b64encode(image_bytes).decode("utf-8")


