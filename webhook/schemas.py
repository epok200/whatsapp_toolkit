from typing import Any, Optional, Dict
from pydantic import BaseModel, Field, model_validator

# ========= PROTOCOLO BASE =========
class BaseEvent(BaseModel):
    event_type: str = Field(..., alias="event")
    instance_id: str = Field(default="")
    apikey: Optional[str] = None  # <--- ¡AGREGAMOS ESTO!
    
    class Config:
        populate_by_name = True

# ======== SCHEMA MAESTRO =========
class MessageUpsert(BaseEvent):
    # --- IDENTIDAD ---
    remote_jid: str       
    from_me: bool         
    wa_id: str            
    push_name: str        
    participant: Optional[str] = None 

    # --- CONTENIDO ---
    message_type: str
    body: str             
    
    # --- MULTIMEDIA ---
    media_url: Optional[str] = None      
    media_mime: Optional[str] = None     
    media_seconds: Optional[int] = None
    is_sticker: bool = False
    
    # --- CONTEXTO ---
    is_reaction: bool = False
    reaction_target_id: Optional[str] = None 
    
    # --- META ---
    timestamp: int
    raw_message: Dict[str, Any]
    raw: Dict[str, Any]

    @property
    def is_group(self) -> bool:
        return "@g.us" in self.remote_jid

    @model_validator(mode="before")
    @classmethod
    def flatten_payload(cls, envelope: Any) -> Any:
        if not isinstance(envelope, dict):
            return envelope

        data = envelope.get("data", {})
        key = data.get("key", {})
        msg = data.get("message", {})
        
        # 1. Determinar tipo 
        m_type = data.get("messageType", "unknown")
        
        body = ""
        url = None
        mime = None
        seconds = None
        reaction_target = None
        is_react = False
        is_stick = False

        # --- LÓGICA DE EXTRACCIÓN ---
        if "conversation" in msg:
            body = msg["conversation"]
        elif "extendedTextMessage" in msg:
            body = msg["extendedTextMessage"].get("text", "")
        elif "imageMessage" in msg:
            img = msg["imageMessage"]
            body = img.get("caption", "[Imagen]")
            url = img.get("url")
            mime = img.get("mimetype")
        elif "audioMessage" in msg:
            aud = msg["audioMessage"]
            body = "[Audio]"
            url = aud.get("url")
            mime = aud.get("mimetype")
            seconds = aud.get("seconds")
        elif "videoMessage" in msg:
            vid = msg["videoMessage"]
            body = vid.get("caption", "[Video]")
            url = vid.get("url")
            seconds = vid.get("seconds")
        elif "stickerMessage" in msg:
            stk = msg["stickerMessage"]
            body = "[Sticker]"
            url = stk.get("url")
            mime = stk.get("mimetype")
            is_stick = True
        elif "reactionMessage" in msg:
            react = msg["reactionMessage"]
            body = react.get("text", "") 
            reaction_target = react.get("key", {}).get("id")
            is_react = True

        # 2. Inyección de datos planos
        envelope.update({
            "remote_jid": key.get("remoteJid"),
            "from_me": key.get("fromMe", False),
            "wa_id": key.get("id"),
            "participant": key.get("participant") or data.get("sender"), 
            "push_name": data.get("pushName", ""),
            "message_type": m_type,
            "body": body,
            "media_url": url,
            "media_mime": mime,
            "media_seconds": seconds,
            "is_sticker": is_stick,
            "is_reaction": is_react,
            "reaction_target_id": reaction_target,
            "timestamp": data.get("messageTimestamp"),
            "raw_message": msg,
            "raw": data 
        })
        return envelope