from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from colorstreak import Logger as log
from pymongo import MongoClient, errors
from pymongo.collection import Collection

from .instance import WhatsAppInstance
from .schemas import Groups
from .sender import WhatsAppSender


# ===============================
# SISTEMA DE CACHE
# ===============================
@dataclass
class MongoCacheBackend:
    uri: str
    db_name: str = "whatsapp_toolkit"
    collection_name: str = "group_snapshots"
    ttl_seconds: int = 600
    _indexes_ready: bool = False
    _client: Optional[MongoClient] = None
    _collection: Optional[Collection] = None
    
    
    def _ensure(self) -> Collection:        
        if self._client is None:
            self._client = MongoClient(self.uri, serverSelectionTimeoutMS=1500)
        
        if self._collection is None:
            db = self._client[self.db_name]
            self._collection = db[self.collection_name]
        
        
        if self._collection is None:
            raise RuntimeError("No se pudo obtener la colección de MongoDB")
        
            
        if not self._indexes_ready:
            self._ttl_logic(self._collection)
            self._indexes_ready = True
            
            
        return self._collection


    def _ttl_logic(self, col: Collection) -> None:
        """ Asegura que el índice del ttl esté creado correctamente. """

        # Siempre aseguramos un índice único en 'key'
        col.create_index("key", unique=True)

        # Inspeccionamos los índices existentes para encontrar uno en created_at
        info = col.index_information()

        ttl_index_name: Optional[str] = None
        current_ttl: Optional[int] = None

        for name, meta in info.items():
            if meta.get("key") == [("created_at", 1)]:
                ttl_index_name = name
                current_ttl = meta.get("expireAfterSeconds")
                break

        # Si el índice TTL existe pero el TTL difiere, lo eliminamos para poder recrearlo
        if ttl_index_name and current_ttl != self.ttl_seconds:
            col.drop_index(ttl_index_name)
            ttl_index_name = None

        # Si falta, creamos el índice TTL
        if not ttl_index_name:
            col.create_index("created_at", expireAfterSeconds=self.ttl_seconds)


    # ========== MÉTODOS PÚBLICOS ==========
    def warmup(self) -> None:
        """ Inicializa la conexión y asegura los índices. """
        self._ensure()
    
    
    def get(self, key: str) -> Optional[dict[str, Any]]:
        """ Obtiene un documento de la caché por su clave. """
        try:
            col: Collection = self._ensure()
            doc = col.find_one({"key": key})
            return doc
        except errors.PyMongoError as e:
            log.error(f"[cache] Mongo get fallo: {e}")
            return None


    def set(self, key: str, doc: dict[str, Any]) -> None:
        """ Guarda un documento en la caché bajo la clave especificada. """
        try:
            col: Collection = self._ensure()
            col.update_one({"key": key}, {"$set": doc}, upsert=True)
        except errors.PyMongoError as e:
            log.error(f"[cache] Mongo set fallo: {e}")





class BaseClient:
    def __init__(self, instance_name: str = "con", cache: Optional[MongoCacheBackend] = None):
        self._instance_name: str = instance_name
        self.cache: Optional[MongoCacheBackend] = cache

    def _key_groups(self, get_participants: bool) -> str:
        return f"groups:{self._instance_name}:participants={str(get_participants).lower()}"

    def get_groups_raw(self, get_participants: bool = True) -> list[dict] | None:
        raise NotImplementedError("Este método debe ser implementado en una subclase.")


    def _get_groups(self, get_participants: bool = True, cache: bool = False) -> Groups:
        key = self._key_groups(get_participants)

        if cache and self.cache:
            log.debug("[cache] Intentando cargar snapshot de grupos desde caché")
            doc = self.cache.get(key)
            if doc and "groups" in doc:
                try:
                    log.debug("[cache] Cargando snapshot de grupos desde caché")
                    grupos: Groups = Groups.model_validate(doc.get("groups"))
                    return grupos
                except Exception as e:
                    log.error(f"[cache] Error al validar snapshot de grupos desde caché: {e}")
                    
            log.info("[cache] No se pudo cargar snapshot de grupos desde caché")

        log.debug("Llamando a la API ...")
        raw = self.get_groups_raw(get_participants=get_participants) 
        
        if raw is None:
            log.error("No se pudieron obtener los datos de grupos de la API")
            return Groups()
        
        grupos = Groups()
        grupos.upload_groups(raw)
        log.debug("Datos de grupos obtenidos de la API")
        if cache and self.cache:
            self.cache.set(key, {
                "key": key,
                "created_at": datetime.now(timezone.utc),
                "source": "whatsapp_api",
                "groups": grupos.model_dump(),
            })
            log.debug("Snapshot de grupos guardado en caché")

        return grupos






# ==============================
# CLIENTE DE WHATSAPP
# ==============================
# Decorador para asegurar conexión antes de ejecutar métodos de WhatsappClient que lo requieran
# def require_connection(method):
#     """
#     Decorador para métodos de WhatsappClient que necesitan una conexión activa.
#     Llama a `self.ensure_connected()` y solo ejecuta el método original si la
#     conexión se confirma; de lo contrario devuelve False.
#     """
#     from functools import wraps

#     @wraps(method)
#     def _wrapper(self, *args, **kwargs):
#         if not self.ensure_connected():
#             print("❌ No fue posible establecer conexión.")
#             return False
#         return method(self, *args, **kwargs)

#     return _wrapper





class WhatsappClient(BaseClient):
    def __init__(self, api_key: str, server_url: str, instance_name: str = "con", cache: Optional[MongoCacheBackend] = None):
        super().__init__(instance_name, cache)
        self._instance = WhatsAppInstance(api_key, instance_name, server_url)
        self._sender: Optional[WhatsAppSender] = None
        self._auto_initialize_sender()

    def _auto_initialize_sender(self):
        """Solo asigna sender si la instancia está enlazada a WhatsApp."""
        info = WhatsAppSender.get_instance_info(
            self._instance.api_key, self._instance.name_instance, self._instance.server_url
        )
        if info.get("ownerJid"):  # <- si tiene owner, significa que ya está enlazada
            self._sender = WhatsAppSender(self._instance)

    # def ensure_connected(self, retries: int = 3, delay: int = 30) -> bool:
    #     """
    #     Garantiza que la instancia esté conectada.
    #     Si aún no existe `self.sender`, intentará crearlo.
    #     Si la prueba de conexión falla, muestra un QR y reintenta.
    #     """
    #     import time

    #     # Si ya tenemos sender y está marcado como conectado, salimos rápido
    #     if self._sender and getattr(self._sender, "connected", False):
    #         return True

    #     def _init_sender():
    #         if self._sender is None:
    #             # Intentar inicializar si la instancia ya está enlazada
    #             info = WhatsAppSender.get_instance_info(
    #                 self._instance.api_key,
    #                 self._instance.name_instance,
    #                 self._instance.server_url,
    #             )
    #             if info.get("ownerJid"):
    #                 self._sender = WhatsAppSender(self._instance)

    #     # Primer intento de inicializar el sender
    #     _init_sender()

    #     for attempt in range(1, retries + 1):
    #         if self._sender and self._sender.test_connection_status():
    #             return True

    #         print(
    #             f"[{attempt}/{retries}] Conexión no disponible, mostrando nuevo QR (espera {delay}s)…"
    #         )
    #         self._instance.connect_instance_qr()  # muestra nuevo QR
    #         time.sleep(delay)

    #         # Reintentar inicializar sender después de mostrar QR
    #         _init_sender()

    #     print("❌ No fue posible establecer conexión después de varios intentos.")
    #     return False


    def send_text(self, number: str, text: str, link_preview: bool = True, delay_ms: int = 1000):
        sender = self._sender
        if sender is None:
            return False
        return sender.send_text(number, text, link_preview, delay_ms=delay_ms)


    def send_media(self, number: str, media_b64: str, filename: str, caption: str, mediatype: str = "document", mimetype: str = "application/pdf",):
        sender = self._sender
        if sender is None:
            return False
        return sender.send_media(number, media_b64, filename, caption, mediatype, mimetype)


    def send_sticker(self, number: str, sticker_b64: str, delay: int = 0, link_preview: bool = True, mentions_everyone: bool = True,):
        sender = self._sender
        if sender is None:
            return False
        return sender.send_sticker(number, sticker_b64, delay, link_preview, mentions_everyone)


    def send_location(self, number: str, name: str, address: str, latitude: float, longitude: float, delay: int = 0,):
        sender = self._sender
        if sender is None:
            return False
        return sender.send_location(number, name, address, latitude, longitude, delay)


    def send_audio(self, number: str, audio_b64: str, delay: int = 0):
        sender = self._sender
        if sender is None:
            return False
        return sender.send_audio(number, audio_b64, delay)


    def connect_number(self, number: str):
        sender = self._sender
        if sender is None:
            return False
        return sender.connect(number)


    def get_groups_raw(self, get_participants: bool = True) -> list[dict] | None:
        sender = self._sender
        if sender is None:
            return None

        response: list[dict] | None = sender.fetch_groups(get_participants)
        if response is None:
            return None
        return response
    
    
    def get_groups_typed(self, get_participants: bool = True, cache: bool = False) -> Groups | None:
        """
        Obtiene los grupos como una instancia de Groups.
        
        Si `cache` es True, intenta cargar desde la caché antes de llamar a la API.
        """
        groups: Groups = self._get_groups(get_participants=get_participants, cache=cache)
        if len(groups) == 0:
            return None
        return groups
    

    def create_instance(self):
        return self._instance.create_instance()

    def delete_instance(self):
        return self._instance.delete_instance()

    def connect_instance_qr(self):
        return self._instance.connect_instance_qr()

