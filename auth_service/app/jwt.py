from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
import secrets
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .blacklist import is_token_blacklisted, token_to_blacklist
from .database import get_db


SECRET = 'super-secret'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 10080



def create_token(user_id: int, exp_time: int, type: str) -> dict[str, str]:
    token_id = secrets.token_urlsafe(32)
    
    payload = {
        'sub': str(user_id), 
        'exp': datetime.now(timezone.utc) + timedelta(minutes=exp_time),
        'role':'user',
        'type': type,
        'jti': token_id,
        'iat': datetime.now(timezone.utc).timestamp()
    }
    
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    
    return {
        'token': token,
        'token_id': token_id
    }



def create_token_pair(user_id: int) -> dict:
    access_token = create_token(user_id, exp_time=ACCESS_TOKEN_EXPIRE_MINUTES, type='access')
    refresh_token = create_token(user_id, exp_time=REFRESH_TOKEN_EXPIRE_MINUTES, type='refresh')
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


    
async def refresh_access_token(db: AsyncSession, refresh_token: str) -> dict:
    try:
        payload = jwt.decode(refresh_token, SECRET, algorithms=[ALGORITHM])
        
        if payload.get('type') != 'refresh':
            raise ValueError('Неверный тип токена')
        
        jti = payload.get('jti')
        if await is_token_blacklisted(db=db, jti=jti):
            raise ValueError('Refresh Token Revoked')
        
        user_id = int(payload.get('sub'))
        if not user_id:
            raise ValueError('Invalid Token')
        
        expires_at = datetime.fromtimestamp(payload.get('exp'), tz=timezone.utc)
        await token_to_blacklist(db, jti, user_id, expires_at)        
        return create_token_pair((user_id))
    
    except JWTError as e:
        raise ValueError(f'Invalid Token {str(e)}')



oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> dict: 
    try: 
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        
        jti = payload.get('jti')
        if not jti or await is_token_blacklisted(db, jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token blacklisted'
            )
            
        return {
            'id': int(payload.get('sub')),
            'role': payload.get('role'),
            'jti': payload.get('jti')
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Token'
        )
        

def required_role(role: str):
    async def role_checker(user: dict = Depends(get_current_user)):
        if role != user.get('role'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid Role'
            )
        return user
    return role_checker