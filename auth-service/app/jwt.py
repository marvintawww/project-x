from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
import secrets
from typing import Optional


SECRET = 'super-secret'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(user_id: int) -> str:
    payload = {
        'sub': str(user_id), 
        'exp': datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        'role':'user',
        'type': 'access'
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def create_refresh_token(user_id: int, token_id: Optional[str] = None) -> str:
    if not token_id:
        token_id = secrets.token_urlsafe(32)
        
    payload = {
        'sub': str(user_id),
        'exp': datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        'role': 'user',
        'type': 'refresh',
        'jti': token_id,
        'iat': datetime.now(timezone.utc).timestamp()
    }
    
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def create_token_pair(user_id: int):
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    

#! Вообще я тут не делаю ротацию только access токена, а сразу заменяю всю пару, вопрос насколько это целесообразно   
    
def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET, algorithms=[ALGORITHM])
        
        if payload.get('type') != 'refresh':
            raise ValueError('Неверный тип токена')
        
        user_id = payload.get('sub')
        if not user_id:
            raise ValueError('Invalid Token')
        
        return create_token_pair(user_id)
    
    except JWTError as e:
        raise ValueError(f'Invalid Token {str(e)}')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict: #! Возможно потом сменить на схему
    try: 
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return {
            'id': int(payload.get('sub')),
            'role': payload.get('role')
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Token'
        )
        


def required_role(role: str):
    async def role_checker(user: int = Depends(get_current_user)):
        if role not in user['role']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid Role'
            )
        return user.get('id')
    return required_role