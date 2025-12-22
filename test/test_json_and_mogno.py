from dataclasses import dataclass
from typing import Any, Optional
from time import time
from pymongo import MongoClient, errors
import json
from pathlib import Path
from colorstreak import Logger as log
from whatsapp_toolkit.schemas import Groups


@dataclass
class CacheBackend:
    def get(self, key: str) -> Optional[dict[str, Any]]:
        raise NotImplementedError

    def set(self, key: str, doc: dict[str, Any]) -> None:
        raise NotImplementedError


@dataclass
class MongoCacheBackend(CacheBackend):
    uri: str
    db_name: str = "whatsapp_toolkit"
    collection_name: str = "group_snapshots"
    _client: Optional[MongoClient] = None
    _collection: Optional[Any] = None

    def _ensure(self):
        if self._client is None:
            self._client = MongoClient(self.uri, serverSelectionTimeoutMS=1500)
        if self._collection is None:
            db = self._client[self.db_name]
            self._collection = db[self.collection_name]
        return self._collection

    def get(self, key: str) -> Optional[dict[str, Any]]:
        try:
            col = self._ensure()
            return col.find_one({"key": key})
        except errors.PyMongoError as e:
            log.error(f"[cache] Mongo get failed: {e}")
            return None

    def set(self, key: str, doc: dict[str, Any]) -> None:
        try:
            col = self._ensure()
            col.update_one({"key": key}, {"$set": doc}, upsert=True)
        except errors.PyMongoError as e:
            log.error(f"[cache] Mongo set failed: {e}")


@dataclass
class WhatsappClientFake:
    cache: Optional[CacheBackend]
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
            doc = self.cache.get(key)
            if doc and "groups" in doc:
                try:
                    return Groups.model_validate(doc["groups"])
                except Exception as e:
                    log.error(f"[cache] Corrupt snapshot, falling back to API: {e}")

        raw = self._api(get_participants=get_participants)
        grupos = Groups()
        grupos.upload_groups(raw)

        if cache and self.cache:
            self.cache.set(key, {
                "key": key,
                "created_at": int(time()),
                "source": "whatsapp_api",
                "groups": grupos.model_dump(),
            })

        return grupos

    

# ======== EJECUCIÓN DIRECTA ========

URK_MONGO = "mongodb://sdialog_db:uhembz9ksxehe1bu@89.116.212.100:27017"


cache_engine = MongoCacheBackend(
    uri=URK_MONGO,
)

engine = WhatsappClientFake(
    cache=cache_engine,
)


grupos = engine.get_groups(get_participants=True , cache=True)
print(f"Grupos cargados desde DB: {grupos}")