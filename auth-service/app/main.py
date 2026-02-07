from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .database import Base, get_db, engine
from .crud import create_user, authenticate_user
from .schemas import AuthResponseSchema, RegisterSchema, AuthCreateSchema, AuthInfo, LoginSchema
from .sender import send_event


app = FastAPI(
    title='Auth API',
    description='API for Auth management',
    version='0.0.1'
)

@app.on_event('startup')
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        
@app.post(
    '/register',
    response_model=AuthResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Register for new user',
    tags=['Auth', 'Register']
)
async def register(reg_data: RegisterSchema, db: AsyncSession = Depends(get_db)):
    auth, token_pair = await create_user(db=db, 
                                         login=reg_data.login, 
                                         email=reg_data.email, 
                                         password=reg_data.password)
    
    send_event({
        'auth_id': auth.id,
        'display_name': reg_data.display_name
    })
    
    return AuthResponseSchema(user=AuthInfo.model_config(auth), token_pair=token_pair)


@app.post(
    '/login',
    response_model=AuthResponseSchema,
    summary='Login',
    tags=['Auth', 'Login']
)
async def login(login_data: LoginSchema, db: AsyncSession = Depends(get_db)):
    user, token_pair = await authenticate_user(db=db, 
                                          login=login_data.login, 
                                          password=login_data.password)
    
    return AuthResponseSchema(user=AuthInfo.model_config(user), token_pair=token_pair)