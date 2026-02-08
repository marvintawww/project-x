from pydantic import BaseModel
from typing import Optional

class UserResponseSchema(BaseModel):
    id: int
    display_name: str
    is_active: bool
    
    
    class Config:
        from_attributes=True
        

class UserUpdateSchema(BaseModel):
    display_name: str | None = None
    
    
class EventData(BaseModel):
    auth_id: int
    event_type: str
    display_name: str | None = None
    is_active: bool | None = True
    
    class Config:
        from_attributes=True