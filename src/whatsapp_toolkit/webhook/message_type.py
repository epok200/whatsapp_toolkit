"""
Modulo que define los tipos de mensajes soportados en el webhook de WhatsApp.
Estos tipos son utilizados para identificar y manejar diferentes formatos
de mensajes entrantes.
"""
class MessageType:
    CONVERSATION = "conversation"
    EXTENDED_TEXT_MESSAGE = "extendedTextMessage"
    IMAGE_MESSAGE = "imageMessage"
    VIDEO_MESSAGE = "videoMessage"
    DOCUMENT_MESSAGE = "documentMessage"
    AUDIO_MESSAGE = "audioMessage"
    STIKER_MESSAGE = "stickerMessage"
    REACTION_MESSAGE = "reactionMessage"