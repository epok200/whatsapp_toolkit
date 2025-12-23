from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime, timezone
from pymongo import MongoClient, errors
from pymongo.collection import Collection
import json
from pathlib import Path
from colorstreak import Logger as log
from whatsapp_toolkit.schemas import Groups



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





@dataclass
class WhatsappClientFake:
    cache: Optional[MongoCacheBackend] = None
    instance: str = "ferchus_test"

    def _key_groups(self, get_participants: bool) -> str:
        return f"groups:{self.instance}:participants={str(get_participants).lower()}"

    def _api(self, get_participants: bool = True) -> list[dict[str, Any]]:
        base_dir = Path(__file__).resolve().parent.parent
        grupo_json = base_dir / "grupos_obtenidos.json"
        with open(grupo_json, "r", encoding="utf-8") as f:
            return json.load(f)



    def get_groups(self, get_participants: bool = True, cache: bool = False) -> Groups:
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
        raw = self._api(get_participants=get_participants)
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


def clean_up():
    from pymongo import MongoClient

    URI = "mongodb://sdialog_db:uhembz9ksxehe1bu@89.116.212.100:27017"

    client = MongoClient(URI)
    client.drop_database("whatsapp_toolkit")

    print("✅ Base de datos whatsapp_toolkit eliminada")


# ======== EJECUCIÓN DIRECTA ========

# TODO : Deprecar esta url de acceso
URK_MONGO = "mongodb://sdialog_db:uhembz9ksxehe1bu@89.116.212.100:27017"


cache_engine = MongoCacheBackend(
    uri=URK_MONGO,
    ttl_seconds=5,
)
cache_engine.warmup()

engine = WhatsappClientFake(
    cache=cache_engine,
)


grupos = engine.get_groups(get_participants=True , cache=True)
print(f"Grupos cargados desde DB: {grupos}")

# clean_up()