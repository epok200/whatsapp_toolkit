from typing import Callable, Awaitable
from .message_type import MessageType
from .schemas import MessageUpsert


MessageHandler = Callable[[MessageUpsert],Awaitable[None]]

class MessageRouter:
    def __init__(self) -> None:
        self._routes: dict[str, MessageHandler] = {}
    
    def on(self, message_type: str):
        """
        Decorador para registrar un handler para un tipo específico.
        Uso: @router.on(MessageType.AUDIO_MESSAGE)
        """
        def wrapper(func: MessageHandler):
            self._routes[message_type] = func
            return func
        return wrapper
    
    def text(self):
        """
        Decorador especial: Atrapa TANTO 'conversation' COMO 'extendedTextMessage'.
        Porque para nosotros, ambos son texto.
        """
        def wrapper(func: MessageHandler):
            self._routes[MessageType.CONVERSATION] = func
            self._routes[MessageType.EXTENDED_TEXT_MESSAGE] = func
            return func
        return wrapper
    
    async def route(self, event: MessageUpsert):
        message_type = event.message_type
        
        handler = self._routes.get(message_type)
        
        if handler:
            await handler(event)
        else:
            pass
        
        
        