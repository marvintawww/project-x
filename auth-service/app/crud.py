from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_

from .models import UserAuthInfo
from .schemas import AuthCreateSchema
from .auth import hash_password, check_hash
from .jwt import create_token_pair


async def create_user(db: AsyncSession, login: str, email: str, password: str) -> tuple[UserAuthInfo, dict]:
    auth_data = AuthCreateSchema(
        login=login,
        email=email,
        hashed_password=hash_password(password)
    )
    
    stmt = select(UserAuthInfo).where(and_(
        or_(
            UserAuthInfo.login == login,
            UserAuthInfo.email == email
        ), 
        UserAuthInfo.is_active == True
    ))
    
    result = (await db.execute(stmt)).scalar_one_or_none() #! Поменять 'result' на что-то другое
    
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь с таким именем или почтой уже существует'
        )
    
    auth = UserAuthInfo(**auth_data.model_dump())
    
    db.add(auth)
    await db.commit()
    await db.refresh(auth)
    
    token_pair = create_token_pair(auth.id)
    
    return auth, token_pair



async def authenticate_user(db: AsyncSession, login: str, password: str) -> tuple[UserAuthInfo, dict]:
    stmt = select(UserAuthInfo).where(UserAuthInfo.login == login)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found'
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Account is deactivated'
        )
    
    if not check_hash(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Wrong password'
        )
        
    token_pair = create_token_pair(user.id)
    
    return user, token_pair


async def deactivate_user(db: AsyncSession, user_id: int):
    stmt = select(UserAuthInfo).where(UserAuthInfo.id == user_id)
    user = (await db.execute(stmt)).scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Account not found'
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Account already deactivated'
        )
        
    user.is_active = False
    await db.commit()
    
    return user
