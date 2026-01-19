from typing import Callable, Awaitable
from .message_type import MessageType
from .schemas import MessageUpsert
from colorstreak import Logger


MessageHandler = Callable[[MessageUpsert],Awaitable[None]]

class MessageRouter:
    def __init__(self) -> None:
        self._routes: dict[str, list[MessageHandler]] = {}
    
    def on(self, message_type: str):
        """
        Decorador para registrar un handler para un tipo específico.
        Uso: @router.on(MessageType.AUDIO_MESSAGE)
        """
        def wrapper(func: MessageHandler):
            if message_type not in self._routes:
                self._routes[message_type] = []
            self._routes[message_type].append(func)
            return func
        return wrapper
    
    def text(self):
        """
        Decorador especial: Atrapa TANTO 'conversation' COMO 'extendedTextMessage'.
        Porque para nosotros, ambos son texto.
        """
        def wrapper(func: MessageHandler):
            for m_type in [MessageType.CONVERSATION, MessageType.EXTENDED_TEXT_MESSAGE]:
                if m_type not in self._routes:
                    self._routes[m_type] = []
                self._routes[m_type].append(func)
            return func
        return wrapper
    
    async def route(self, event: MessageUpsert):
        message_type = event.message_type
        
        handlers = self._routes.get(message_type, [])
        
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                Logger.error(f"Error al manejar el mensaje de tipo {message_type} con el handler {handler.__name__}: {e}")
                pass
        
        
        