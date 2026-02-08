from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status

from .models import User
from .schemas import UserUpdateSchema

async def get_one_user(user_id: int, db: AsyncSession) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User Not Found'
        )
        
    return user
    
    
async def update_user_info(user_id: int, update_data: UserUpdateSchema, db: AsyncSession) -> User | None:
    user = await get_one_user(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User Not Found'
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)    
    
    for field, value in update_dict.items():
        setattr(user, field, value)
        
    await db.commit()
    await db.refresh(user)
    
    return user
    