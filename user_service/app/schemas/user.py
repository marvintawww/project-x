from pydantic import BaseModel

class UserResponseSchema(BaseModel):
    id: int
    display_name: str
    is_active: bool
    
    
    class Config:
        from_attributes=True
        

class UserUpdateSchema(BaseModel):
    display_name: str | None = None
    