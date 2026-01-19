from typing import Any
from pydantic import BaseModel, Field, model_validator


class ConnectionUpdate(BaseModel):
    event_type: str = Field(..., alias="event")
    instance: str
    state: str
    status_reason: int = Field(default=0)
    
    @model_validator(mode="before")
    @classmethod
    def extract_data(cls, envelope: Any) -> Any:
        if not isinstance(envelope, dict): 
            return envelope
        

        data = envelope.get("data", {})
        
        envelope["instance"] = data.get("instance")
        envelope["state"] = data.get("state")
        envelope["status_reason"] = data.get("statusReason", 0)
        
        return envelope