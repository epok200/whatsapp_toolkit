
from whatsapp_toolkit.webhook import WebhookManager, EventType
from .handlers import message_router

webhook_manager = WebhookManager()


@webhook_manager.on(EventType.MESSAGES_UPSERT)
async def handle_messages(event):
    """
    Handler para eventos de mensajes nuevos (upsert).
    """
    es_mi_mensaje = event.from_me is True
    if not es_mi_mensaje:
        return  
    
    await message_router.route(event)
    