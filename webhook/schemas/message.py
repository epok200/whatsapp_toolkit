from typing import Any, Optional, Dict
from pydantic import BaseModel, Field, model_validator
from ..utils import pluck

# ==============================
# CORE
# ==============================
class BaseEvent(BaseModel):
    event_type: str = Field(..., alias="event")
    instance_id: str = Field(default="")
    apikey: Optional[str] = None
    
    class Config:
        populate_by_name = True
        
    # SIN AUTO_MAP. Simplicidad total.

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
        
        # Extracción MANUAL y EXPLÍCITA con pluck
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
        envelope["raw"]         = pluck(envelope, "data", {}) # Contexto para desencriptar
        
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
        
        # 2. El Body (Lógica Polimórfica)
        msg = pluck(envelope, "data.message", {})
        body = ""
        
        if "conversation" in msg:
            body = msg["conversation"]
        elif "extendedTextMessage" in msg:
            body = pluck(msg, "extendedTextMessage.text", "")
        elif "imageMessage" in msg:
            body = pluck(msg, "imageMessage.caption", "[Imagen]")
        elif "videoMessage" in msg:
            body = pluck(msg, "videoMessage.caption", "[Video]")
        elif "documentMessage" in msg:
            body = pluck(msg, "documentMessage.caption", "[Documento]")
        elif "audioMessage" in msg:
            body = "[Audio]"
        elif "stickerMessage" in msg:
            body = "[Sticker]"
        
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
        
        if "audioMessage" in message: 
            target = message["audioMessage"]
        elif "imageMessage" in message: 
            target = message["imageMessage"]
        elif "videoMessage" in message: 
            target = message["videoMessage"]
        elif "stickerMessage" in message: 
            target = message["stickerMessage"]
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
    
    @model_validator(mode="before")
    @classmethod
    def extract_reaction(cls, envelope: Any) -> Any:
        if not isinstance(envelope, dict): 
            return envelope
        
        message = pluck(envelope, "data.message", {})
        
        if "reactionMessage" in message:
            react = message["reactionMessage"]
            envelope["is_reaction"] = True
            envelope["reaction_target_id"] = pluck(react, "key.id")
            
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