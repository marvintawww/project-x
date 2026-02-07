from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class UserAuthInfo(Base):
    __tablename__ = 'auth_info'
    
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)