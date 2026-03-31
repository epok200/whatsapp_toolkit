from typing import Callable, Awaitable, Optional
from .message_type import MessageType
from .schemas import MessageUpsert
from colorstreak import Logger


MessageHandler = Callable[[MessageUpsert], Awaitable[None]]


def _matches_filters(event: MessageUpsert, is_group: Optional[bool], from_me: Optional[bool]) -> bool:
    if is_group is not None and event.is_group != is_group:
        return False
    if from_me is not None and event.from_me != from_me:
        return False
    return True


class MessageRouter:
    def __init__(self) -> None:
        self._routes: dict[str, list[tuple[MessageHandler, Optional[bool], Optional[bool]]]] = {}
        self._default_handlers: list[MessageHandler] = []

    def on(self, message_type: str, is_group: Optional[bool] = None, from_me: Optional[bool] = None):
        """
        Decorador para registrar un handler para un tipo especifico de mensaje.
        Filtros opcionales:
            is_group: True = solo grupos, False = solo chats directos, None = ambos
            from_me: True = solo mensajes propios, False = solo de otros, None = ambos

        Uso:
            @router.on(MessageType.AUDIO_MESSAGE)
            @router.on(MessageType.IMAGE_MESSAGE, is_group=True)
            @router.on(MessageType.CONVERSATION, from_me=False)
        """
        def wrapper(func: MessageHandler):
            if message_type not in self._routes:
                self._routes[message_type] = []
            self._routes[message_type].append((func, is_group, from_me))
            return func
        return wrapper

    def text(self, is_group: Optional[bool] = None, from_me: Optional[bool] = None):
        """
        Decorador especial: Atrapa TANTO 'conversation' COMO 'extendedTextMessage'.

        Uso:
            @router.text()                    # todo texto
            @router.text(is_group=True)       # solo texto en grupos
            @router.text(from_me=False)       # solo texto de otros
        """
        def wrapper(func: MessageHandler):
            for m_type in [MessageType.CONVERSATION, MessageType.EXTENDED_TEXT_MESSAGE]:
                if m_type not in self._routes:
                    self._routes[m_type] = []
                self._routes[m_type].append((func, is_group, from_me))
            return func
        return wrapper

    def default(self):
        """
        Decorador para registrar un handler que se ejecuta cuando ningun otro handler
        coincide con el tipo de mensaje.

        Uso:
            @router.default()
            async def fallback(event: MessageUpsert):
                print(f"Tipo no manejado: {event.message_type}")
        """
        def wrapper(func: MessageHandler):
            self._default_handlers.append(func)
            return func
        return wrapper

    async def route(self, event: MessageUpsert):
        message_type = event.message_type
        entries = self._routes.get(message_type, [])

        matched = False
        for handler, is_group, from_me in entries:
            if not _matches_filters(event, is_group, from_me):
                continue
            matched = True
            try:
                await handler(event)
            except Exception as e:
                Logger.error(f"Error en handler {handler.__name__} para {message_type}: {e}")

        if not matched:
            for handler in self._default_handlers:
                try:
                    await handler(event)
                except Exception as e:
                    Logger.error(f"Error en default handler {handler.__name__}: {e}")
