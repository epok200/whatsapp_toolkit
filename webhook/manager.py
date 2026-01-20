from colorstreak import Logger

from whatsapp_toolkit.webhook import EventType, WebhookManager
from whatsapp_toolkit.webhook.schemas import ConnectionUpdate, MessageUpsert

from .handlers import message_router

webhook_manager = WebhookManager()


@webhook_manager.on(EventType.MESSAGES_UPSERT)
async def handle_messages(event: MessageUpsert):
    """
    Handler para eventos de mensajes nuevos (upsert).
    """
    es_mi_mensaje = event.from_me is True
    if not es_mi_mensaje:
        return  
    
    await message_router.route(event)
    
    
@webhook_manager.on(EventType.CONNECTION_UPDATE)
async def handler_conection(event: ConnectionUpdate):
    try:
        state = event.state
        reason = event.status_reason
        instance = event.instance
        
        Logger.info(f"📡 Estado Instancia '{instance}': {state}")
        
        if state == "open":
            Logger.success("🟢 [Webhook] Conexión establecida exitosamente.")
            
        elif state == "close":
            Logger.error(f"🔴 [Webhook] DESCONEXIÓN DETECTADA. Razón: {reason}")
            
            if reason == 401:
                Logger.warning("⚠️ La sesión fue cerrada (Logout). Se requiere nuevo escaneo de QR.")
                # TODO: Implementar lógica de reconexión si es necesario
                
        elif state == "connecting":
            Logger.info("🟡 Conectando...")

    except Exception as e:
        Logger.error(f"[Webhook] Error crítico en handler de conexión: {e}")