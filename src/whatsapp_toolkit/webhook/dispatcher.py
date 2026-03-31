from typing import Callable, Dict, List, Type, Optional
from pydantic import BaseModel
from colorstreak import Logger
from .events import EVENT_MODEL_MAP


class WebhookManager:
    def __init__(self):
        self._registry: Dict[str, List[tuple[Callable, Type[BaseModel]]]] = {}
        self._routers: list = []

    def on(self, event_type: str, model: Optional[Type[BaseModel]] = None):
        """
        Decorador para registrar handlers por evento. Soporta multiples handlers por evento.
        Uso simple: @manager.on(EventType.MESSAGES_UPSERT) -> Auto-detecta el modelo.
        Uso avanzado: @manager.on(..., model=MiModeloCustom) -> Sobrescribe el modelo.
        """
        if model is None:
            model = EVENT_MODEL_MAP.get(event_type)
            if model is None:
                raise ValueError(
                    f"El evento '{event_type}' no tiene un modelo por defecto. "
                    "Debes pasar 'model=TuModelo' explicitamente."
                )

        def wrapper(func):
            Logger.debug(f"Handler registrado: {event_type} -> {model.__name__}")
            if event_type not in self._registry:
                self._registry[event_type] = []
            self._registry[event_type].append((func, model))
            return func
        return wrapper

    def include_router(self, router, event_type: str = "messages.upsert"):
        """
        Conecta un MessageRouter al manager. El router se ejecuta automaticamente
        cuando llega un evento del tipo indicado.

        Uso:
            manager.include_router(router)
            manager.include_router(router, event_type="messages.upsert")
        """
        self._routers.append((router, event_type))

    def knows_event(self, event_type: str) -> bool:
        event_normalized = event_type.replace("-", ".")
        has_handlers = event_normalized in self._registry
        has_router = any(et == event_normalized for _, et in self._routers)
        return has_handlers or has_router

    async def dispatch(self, payload: dict):
        """
        Motor: Recibe JSON -> Busca Handlers -> Valida -> Ejecuta todos.
        Tambien despacha a routers registrados via include_router().
        """
        event_name = payload.get("event")
        if not event_name:
            return

        # Ejecutar handlers registrados con @manager.on()
        handlers = self._registry.get(event_name, [])
        for handler_func, model_class in handlers:
            try:
                clean_event = model_class.model_validate(payload)
                await handler_func(clean_event)
            except Exception as e:
                Logger.error(f"[Dispatcher] Error procesando {event_name}: {e}")

        # Ejecutar routers registrados con include_router()
        for router, router_event_type in self._routers:
            if event_name != router_event_type:
                continue
            try:
                model_class = EVENT_MODEL_MAP.get(event_name)
                if model_class is None:
                    continue
                clean_event = model_class.model_validate(payload)
                await router.route(clean_event)
            except Exception as e:
                Logger.error(f"[Dispatcher] Error en router para {event_name}: {e}")
