from typing import Any, Optional, Dict
from pydantic import BaseModel, Field, model_validator
from ..utils import pluck
from ..message_type import MessageType 

# ==============================
# CORE
# ==============================
class BaseEvent(BaseModel):
    event_type: str = Field(..., alias="event")
    instance: str = Field(default="")
    apikey: Optional[str] = None
    
    class Config:
        populate_by_name = True

# ==============================        
# MIXINS : Lógica Explícita (Sin Magia)
# ==============================  

class IdentityMixin(BaseEvent):
    remote_jid: str
    from_me: bool
    wa_id: str
    push_name: str
    participant: Optional[str] = None
    
    @model_validator(mode="before")
    @classmethod
    def extract_identity(cls, envelope: Any) -> Any:
        if not isinstance(envelope, dict): 
            return envelope
        
        envelope["remote_jid"] = pluck(envelope, "data.key.remoteJid")
        envelope["from_me"]    = pluck(envelope, "data.key.fromMe", False)
        envelope["wa_id"]      = pluck(envelope, "data.key.id")
        envelope["push_name"]  = pluck(envelope, "data.pushName", "")
        envelope["participant"]= pluck(envelope, "data.key.participant")
        
        return envelope

class MetaMixin(BaseEvent):
    timestamp: int
    raw_message: Dict[str, Any]
    raw: Dict[str, Any]
    
    @model_validator(mode="before")
    @classmethod
    def extract_metadata(cls, envelope: Any) -> Any:
        if not isinstance(envelope, dict): 
            return envelope
        
        envelope["timestamp"]   = pluck(envelope, "data.messageTimestamp")
        envelope["raw_message"] = pluck(envelope, "data.message", {})
        envelope["raw"]         = pluck(envelope, "data", {}) 
        
        return envelope
        
class ContentMixin(BaseEvent):
    message_type: str
    body: str

    @model_validator(mode="before")
    @classmethod
    def extract_content(cls, envelope: Any) -> Any:
        if not isinstance(envelope, dict): 
            return envelope
        
        # 1. Tipo de mensaje
        envelope["message_type"] = pluck(envelope, "data.messageType", "unknown")
        
        # 2. El Body (Lógica Polimórfica usando MessageType)
        msg = pluck(envelope, "data.message", {})
        body = ""
        
        if MessageType.CONVERSATION in msg:
            body = msg[MessageType.CONVERSATION]
            
        elif MessageType.EXTENDED_TEXT_MESSAGE in msg:
            # Construimos el path dinámicamente: "extendedTextMessage.text"
            body = pluck(msg, f"{MessageType.EXTENDED_TEXT_MESSAGE}.text", "")
            
        elif MessageType.IMAGE_MESSAGE in msg:
            body = pluck(msg, f"{MessageType.IMAGE_MESSAGE}.caption", "[Imagen]")
            
        elif MessageType.VIDEO_MESSAGE in msg:
            body = pluck(msg, f"{MessageType.VIDEO_MESSAGE}.caption", "[Video]")
            
        elif MessageType.DOCUMENT_MESSAGE in msg:
            body = pluck(msg, f"{MessageType.DOCUMENT_MESSAGE}.caption", "[Documento]")
            
        elif MessageType.AUDIO_MESSAGE in msg:
            body = "[Audio]"
            
        elif MessageType.STIKER_MESSAGE in msg: # Usamos tu nombre de variable
            body = "[Sticker]"

        # --- AQUÍ LA INTEGRACIÓN ---
        elif MessageType.REACTION_MESSAGE in msg:
            # Extraemos el emoji directamente para que 'event.body' no esté vacío
            body = pluck(msg, f"{MessageType.REACTION_MESSAGE}.text", "[Reacción]")
        
        envelope["body"] = body
        return envelope

class MediaMixin(BaseEvent):
    media_url: Optional[str] = None      
    media_mime: Optional[str] = None     
    media_seconds: Optional[int] = None
    is_sticker: bool = False
    
    @model_validator(mode="before")
    @classmethod
    def extract_media(cls, envelope: Any) -> Any:
        if not isinstance(envelope, dict): 
            return envelope
    
        message = pluck(envelope, "data.message", {})
        target = None
        is_stick = False
        
        # --- REFACTORIZADO CON CONSTANTES ---
        
        if MessageType.AUDIO_MESSAGE in message: 
            target = message[MessageType.AUDIO_MESSAGE]
            
        elif MessageType.IMAGE_MESSAGE in message: 
            target = message[MessageType.IMAGE_MESSAGE]
            
        elif MessageType.VIDEO_MESSAGE in message: 
            target = message[MessageType.VIDEO_MESSAGE]
            
        elif MessageType.STIKER_MESSAGE in message: 
            target = message[MessageType.STIKER_MESSAGE]
            is_stick = True
        
        if target:
            envelope["media_url"] = target.get("url")
            envelope["media_mime"] = target.get("mimetype")
            envelope["media_seconds"] = target.get("seconds")
            envelope["is_sticker"] = is_stick
            
        return envelope

class ReactionMixin(BaseEvent):
    is_reaction: bool = False
    reaction_target_id: Optional[str] = None
    reaction_text: Optional[str] = None 
    
    @model_validator(mode="before")
    @classmethod
    def extract_reaction(cls, envelope: Any) -> Any:
        if not isinstance(envelope, dict): 
            return envelope
        
        message = pluck(envelope, "data.message", {})
        
        # --- INTEGRACIÓN COMPLETA DE REACTION ---
        if MessageType.REACTION_MESSAGE in message:
            react = message[MessageType.REACTION_MESSAGE]
            
            envelope["is_reaction"] = True
            envelope["reaction_target_id"] = pluck(react, "key.id")
            envelope["reaction_text"] = pluck(react, "text") 
            
        return envelope

# ==============================
# SCHEMA MAESTRO
# ==============================
class MessageUpsert(
    IdentityMixin, 
    ContentMixin, 
    MediaMixin, 
    ReactionMixin, 
    MetaMixin
):
    @property
    def is_group(self) -> bool:
        return "@g.us" in self.remote_jid