from .schemas import MessageUpsert


class EventType:
    """ Catalogo oficial de eventos soportados por el webhook de WhatsApp """
    MESSAGES_UPSERT = "messages.upsert"
    #MESSAGES_UPDATE = "messages.update"
    #CONTACTS_UPDATE = "contacts.update"
    #CHATS_UPDATE    = "chats.update"
    

EVENT_MODEL_MAP = {
    EventType.MESSAGES_UPSERT: MessageUpsert,
}