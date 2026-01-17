# dispatcher.py
from asyncio import log
from typing import Callable, Dict, Any, Type
from pydantic import BaseModel
from colorstreak import Logger
import json

class EventDispatcher:
    def __init__(self):
        # El 'casillero': Guarda {"nombre_evento": (funcion_handler, modelo_pydantic)}
        self._registry: Dict[str, tuple[Callable, Type[BaseModel]]] = {}

    def on(self, event_name: str, model: Type[BaseModel]):
        """
        Decorador: Registra la función y define qué molde (Schema) usar.
        Uso: @dispatcher.on("messages.upsert", model=MessageUpsert)
        """
        Logger.info(f"Registrando handler para evento: {event_name} con modelo {model.__name__}")
        def wrapper(func):
            self._registry[event_name] = (func, model)
            return func
        return wrapper

    async def dispatch(self, payload: dict):
        """
        Motor: Recibe JSON -> Busca Handler -> Valida -> Ejecuta.
        """
        event_name = payload.get("event")
        
        rawn_json_f = json.dumps(payload, ensure_ascii=False)
        raw_formatted = json.loads(rawn_json_f)
        
        
        # 1. Búsqueda eficiente en el registro
        if not event_name or event_name not in self._registry:
            return  # Ignora eventos no registrados (Fail-fast)

        handler_func, model_class = self._registry[event_name]

        try:
            # 2. Validación y Limpieza (Pydantic 'flatten_payload' actúa aquí)
            clean_event = model_class.model_validate(payload)
            
            # 3. Ejecución del Handler con datos limpios
            await handler_func(clean_event)
            
        except Exception as e:
            Logger.error(f"[Dispatcher] Error procesando {event_name}: {e}")

# Instancia única para importar en main
webhook_manager = EventDispatcher()