from typing import Callable, Dict, Type, Optional
from pydantic import BaseModel
from colorstreak import Logger
from .events import EVENT_MODEL_MAP

class WebhookManager:
    def __init__(self):
        self._registry: Dict[str, tuple[Callable, Type[BaseModel]]] = {}

    def on(self, event_type: str, model: Optional[Type[BaseModel]] = None):
        """
        Decorador Inteligente.
        Uso simple: @manager.on(EventType.MESSAGES_UPSERT) -> Auto-detecta el modelo.
        Uso avanzado: @manager.on(..., model=MiModeloCustom) -> Sobrescribe el modelo.
        """
        
        if model is None:
            model = EVENT_MODEL_MAP.get(event_type)
            
            if model is None:
                raise ValueError(
                    f"❌ El evento '{event_type}' no tiene un modelo por defecto. "
                    "Debes pasar 'model=TuModelo' explícitamente."
                )

        def wrapper(func):
            Logger.debug(f"🔌 Handler registrado: {event_type} -> {model.__name__}")
            self._registry[event_type] = (func, model)
            return func
        return wrapper
    
    def knows_event(self, event_type: str) -> bool:
        """Verifica si el evento está registrado."""
        event_normalized = event_type.replace("-", ".")
        return event_normalized in self._registry

    async def dispatch(self, payload: dict):
        """
        Motor: Recibe JSON -> Busca Handler -> Valida -> Ejecuta.
        """
        event_name = payload.get("event")
        
        if not event_name or event_name not in self._registry:
            return

        handler_func, model_class = self._registry[event_name]

        try:
            clean_event = model_class.model_validate(payload)
            await handler_func(clean_event)
            
        except Exception as e:
            Logger.error(f"[Dispatcher] Error procesando {event_name}: {e}")

