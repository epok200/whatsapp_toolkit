from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("whatsapp-toolkit")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .utils import generar_audio
from .client import WhatsappClient, MongoCacheBackend
from .media import PDFGenerator, obtener_gif_base64, obtener_imagen_base64
from .devtools import *
from .schemas import *
from .async_client import AsyncWhatsappClient