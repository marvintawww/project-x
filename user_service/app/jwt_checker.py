from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from .database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

SECRET = 'super-secret'
ALGORITHM = 'HS256'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> dict: 
    try: 
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
            
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