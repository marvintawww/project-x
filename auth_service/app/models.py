from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .database import Base
from datetime import datetime, timezone

class UserAuthInfo(Base):
    __tablename__ = 'auth_info'
    
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    

class TokenBlackList(Base):
    __tablename__ = 'token_blacklist'
    
    id = Column(Integer, primary_key=True)
    jti = Column(String, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)) 
    