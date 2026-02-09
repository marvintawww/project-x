from pydantic import BaseModel

class EventData(BaseModel):
    auth_id: int
    event_type: str
    display_name: str | None = None
    is_active: bool | None = True
    
    class Config:
        from_attributes=True