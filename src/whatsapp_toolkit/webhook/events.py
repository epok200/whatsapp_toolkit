from .schemas import MessageUpsert, ConnectionUpdate


class EventType:
    """ Catalogo oficial de eventos soportados por el webhook de WhatsApp """
    MESSAGES_UPSERT = "messages.upsert"
    CONNECTION_UPDATE = "connection.update"
    #MESSAGES_UPDATE = "messages.update"
    #CONTACTS_UPDATE = "contacts.update"
    #CHATS_UPDATE    = "chats.update"
    

EVENT_MODEL_MAP = {
    EventType.MESSAGES_UPSERT: MessageUpsert,
    EventType.CONNECTION_UPDATE: ConnectionUpdate,
}