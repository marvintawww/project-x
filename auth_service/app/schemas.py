import re
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import ClassVar, Optional

from .validators import regex_validator

class RegisterSchema(BaseModel):
    display_name: str = Field(min_length=3, max_length=30)
    login: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8)
    
    DNAME_PATTERN: ClassVar[str] = r"^[A-Za-z]{3,30}$"
    LOGIN_PATTERN: ClassVar[str] = r"^[A-Za-z_0-9]{3,30}$"
    PW_PATTERN: ClassVar[str] = r"^(?=.*\d)(?=.*[!@#$%^&*()-=])(?=.*[a-z])(?=.*[A-Z])[a-zA-Z0-9_!@#$%^&*()-=]{8,}$"
        
    @field_validator('password')
    @classmethod
    def password_validator(cls, pw: str) -> str:
        return regex_validator(cls.PW_PATTERN, pw, 'Пароль не соответствует требованиям!')
    
    @field_validator('login')
    @classmethod
    def login_validator(cls, ln: str) -> str:
        return regex_validator(cls.LOGIN_PATTERN, ln, 'Логин не соответствует требованиям!')
    
    @field_validator('display_name')
    @classmethod
    def displayname_validator(cls, dn: str) -> str:
        return regex_validator(cls.DNAME_PATTERN, dn, 'Имя не соответствует требованиям!')
        


class AuthCreateSchema(BaseModel):
    login: str
    email: EmailStr
    hashed_password: str

    
class LoginSchema(BaseModel):
    login: str
    password: str
    

#! Это схема которая выводит информацию пользователя, используется в AuthResponseSchema

class AuthInfo(BaseModel):
    id: int
    login: str
    email: str
    is_active: bool
    
    class Config:
        from_attributes = True    
        

#! Тут схема, которая включает в себя пользователя и пару токенов, эта схема возвращается в /register и /login

class AuthResponseSchema(BaseModel):
    user: AuthInfo
    token_pair: dict
    
    class Config:
        from_attributes=True
        
        
#! Пока что схемы для токенов будут здесь        

class RefreshTokenSchema(BaseModel):
    refresh_token: str
    
class TokenData(BaseModel):
    token: str
    token_id: str

class TokenResponseSchema(BaseModel):
    access_token: TokenData
    refresh_token: TokenData