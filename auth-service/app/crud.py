from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from .models import UserAuthInfo
from .schemas import RegisterSchema, LoginSchema, AuthCreateSchema
from .auth import hash_password, check_hash
from .jwt import create_token_pair


async def create_user(db: AsyncSession, login: str, email: str, password: str) -> tuple[UserAuthInfo, dict]:
    auth_data = AuthCreateSchema(
        login=login,
        email=email,
        password=hash_password(password)
    )
    
    stmt = select(UserAuthInfo).where(
        or_(
            UserAuthInfo.login == login,
            UserAuthInfo.email == email
        ))
    
    result = (await db.execute(stmt)).scalar_one_or_none()
    
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


async def authenticate_user(db: AsyncSession, login: str, password: str):
    stmt = select(UserAuthInfo).where(UserAuthInfo.login == login)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found'
        )
    
    if not check_hash(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Wrong password'
        )
        
    token_pair = create_token_pair(user.id)
    
    return user, token_pair