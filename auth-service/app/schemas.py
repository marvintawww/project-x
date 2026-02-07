import re
from pydantic import BaseModel, Field, EmailStr, field_validator

from .validators import regex_validator

class RegisterSchema(BaseModel):
    display_name: str = Field(min_length=3, max_length=30)
    login: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8)
    
    DNAME_PATTERN = r"^[A-Za-z]{3,30}$"
    LOGIN_PATTERN = r"^[A-Za-z_0-9]{3,30}$"
    PW_PATTERN = r"^(?=.*\d)(?=.*[!@#$%^&*()-=])(?=.*[a-z])(?=.*[A-Z])[a-zA-Z0-9_!@#$%^&*()-=]{8,}$"
        
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
    def login_validator(cls, dn: str) -> str:
        return regex_validator(cls.DNAME_PATTERN, dn, 'Имя не соответствует требованиям!')
        
        
        
#? Вообще касаемо AuthCreate у меня есть вопрос все-таки, насколько это правильная реализация

class AuthCreateSchema(BaseModel):
    login: str
    email: EmailStr
    hashed_password: str

    
class LoginSchema(BaseModel):
    login: str
    password: str
    

class AuthInfo(BaseModel):
    id: int
    login: str
    email: str
    
    class Config:
        from_attributes = True    
        

class AuthResponseSchema(BaseModel):
    user: AuthInfo
    token_pair: dict
    
    class Config:
        from_attributes=True