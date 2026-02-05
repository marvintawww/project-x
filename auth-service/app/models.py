from sqlalchemy import Column, Integer, String
from .database import Base

class AuthInfo(Base):
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    hashed_password = Column(String)

