from fastapi import HTTPException, Depends, status, FastAPI
from contextlib import asynccontextmanager
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import UserResponseSchema, UserUpdateSchema
from .consumer import start_consumer
from .jwt_checker import get_current_user
from .database import get_db
from .crud import get_one_user, update_user_info


@asynccontextmanager
async def lifespan(app: FastAPI): 
    task = asyncio.create_task(start_consumer())
    yield
    task.cancel()
    
    
app = FastAPI(
    title='User Service API',
    description='API For User Management',
    version='0.0.1', 
    lifespan=lifespan
)


@app.get(
    '/profile',
    response_model=UserResponseSchema,
    summary='Get Self Profile',
    tags=['User']
)
async def get_profile(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_one_user(user.get('id'), db)


@app.patch(
    '/edit-bio',
    response_model=UserResponseSchema,
    summary='Edit User Bio',
    tags=['User']
)
async def edit_profile( update_data: UserUpdateSchema, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await update_user_info(user.get('id'), update_data, db)
